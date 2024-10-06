import cv2
import numpy as np
import base64
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # リクエストのコンテンツ長を取得
        content_length = int(self.headers['Content-Length'])
        # リクエストボディを読み込む
        body = self.rfile.read(content_length)
        # JSONデータとしてパース
        data = json.loads(body)
        file_name = data['fileName']
        image_base64 = data['imageBase64']

        # base64文字列を画像データにデコード
        image_data = base64.b64decode(image_base64.split(',')[1])
        np_image = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # 画像処理 (エッジ検出、膨張処理)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)

        # 処理結果をbase64形式にエンコード
        _, buffer = cv2.imencode(f'{file_name}.png', dilated)
        result_base64 = base64.b64encode(buffer).decode('utf-8')

        # JSON形式で結果を返す
        response = json.dumps({"dilatedBase64": "data:image/png;base64," + result_base64})
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

