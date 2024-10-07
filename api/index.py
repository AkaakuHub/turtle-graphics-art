from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)


@app.route("/api/run", methods=["POST"])
def process_image():
    try:
        data = request.get_json()
        image_base64 = data.get("image")

        image_data = base64.b64decode(image_base64)
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # OpenCVの処理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=0)
        turned = cv2.bitwise_not(dilated)

        response_data = {
            "image": base64.b64encode(
                cv2.imencode(".png", turned)[1]
            ).decode(),
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5328)
