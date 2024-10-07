from flask import Flask, request, jsonify
import cv2
import numpy as np
import json
from collections import deque
import base64

app = Flask(__name__)


def find_islands(image):
    height, width = image.shape[:2]
    islands = []
    visited = np.zeros((height, width), dtype=bool)

    for y in range(height):
        for x in range(width):
            if image[y, x] == 255 and not visited[y, x]:
                island = bfs(image, x, y, visited)
                islands.append(island)

    return islands


def bfs(binary, start_x, start_y, visited):
    queue = deque([(start_x, start_y)])
    island = []

    while queue:
        x, y = queue.popleft()
        if visited[y, x]:
            continue

        visited[y, x] = True
        island.append((x, y))

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < binary.shape[1]
                and 0 <= ny < binary.shape[0]
                and binary[ny, nx] == 255
            ):
                queue.append((nx, ny))

    return island


def calculate_distance(p1, p2):
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))


def find_nearest_island(current_pos, islands):
    min_distance = float("inf")
    nearest_island = None

    for island in islands:
        distance = calculate_distance(current_pos, island[0])
        if distance < min_distance:
            min_distance = distance
            nearest_island = island

    return nearest_island


def get_direction(dx, dy):
    if abs(dx) > abs(dy):
        return 0 if dx > 0 else 180
    else:
        return 90 if dy > 0 else 270


def generate_zigzag_commands(start, end, current_angle):
    commands = []
    x1, y1 = start
    x2, y2 = end

    while (x1, y1) != (x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            break

        direction = get_direction(dx, dy)
        angle_diff = (direction - current_angle + 360) % 360

        if angle_diff != 0:
            if angle_diff == 180:
                commands.append("r180")
            elif angle_diff > 180:
                commands.append(f"l{360 - angle_diff}")
            else:
                commands.append(f"r{angle_diff}")

        if direction in [0, 180]:
            move_x = 1 if dx > 0 else -1
            commands.append("m1")
            x1 += move_x
        else:
            move_y = 1 if dy > 0 else -1
            commands.append("m1")
            y1 += move_y

        current_angle = direction

    return commands, current_angle


def generate_turtle_commands(islands):
    commands = []
    current_pos = (0, 0)
    current_angle = 0

    while islands:
        nearest_island = find_nearest_island(current_pos, islands)
        islands.remove(nearest_island)

        # Move to the start of the island
        commands.append("u")  # Pen up
        zigzag_commands, current_angle = generate_zigzag_commands(
            current_pos, nearest_island[0], current_angle
        )
        commands.extend(zigzag_commands)

        # Draw the island
        commands.append("d")  # Pen down
        for i in range(1, len(nearest_island)):
            zigzag_commands, current_angle = generate_zigzag_commands(
                nearest_island[i - 1], nearest_island[i], current_angle
            )
            commands.extend(zigzag_commands)

        current_pos = nearest_island[-1]

    return commands


@app.route("/api/run", methods=["POST"])
def process_image():
    try:
        data = request.get_json()
        image_base64 = data.get("imageBase64")

        image_data = base64.b64decode(image_base64)
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # OpenCVの処理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=0)

        # Find islands
        islands = find_islands(dilated)
        turtle_commands = generate_turtle_commands(islands)

        turtle_json = {
            "size": [image.shape[1], image.shape[0]],
            "commands": turtle_commands,
        }

        # turtle_json = {}

        response_data = {
            "turtle": turtle_json,
            "dilatedBase64": base64.b64encode(
                cv2.imencode(".png", dilated)[1]
            ).decode(),
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5328)