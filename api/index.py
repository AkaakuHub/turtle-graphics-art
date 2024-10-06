from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize
from skimage import filters, morphology
from io import BytesIO
import base64
from collections import deque

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
            if (0 <= nx < binary.shape[1] and 0 <= ny < binary.shape[0] and binary[ny, nx] == 255):
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
        image = Image.open(BytesIO(image_data)).convert('L')
        np_image = np.array(image)

        # 画像処理
        blurred = filters.gaussian(np_image, sigma=1)
        edges = filters.sobel(blurred)
        dilated = morphology.dilation(edges)

        # 二値化
        binary = (dilated > dilated.mean()).astype(np.uint8) * 255
        
        # スケルトン化
        skeleton = skeletonize(binary // 255) * 255  # skeletonizeは0-1の配列を受け取るので、255で割る

        # Find islands
        islands = find_islands(skeleton)
        turtle_commands = generate_turtle_commands(islands)

        turtle_json = {
            "size": [np_image.shape[1], np_image.shape[0]],
            "commands": turtle_commands,
        }

        # 処理結果の画像をbase64エンコード
        processed_image = Image.fromarray(skeleton.astype('uint8'))
        buffered = BytesIO()
        processed_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        response_data = {
            "turtle": turtle_json,
            "dilatedBase64": img_str,
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5328)
