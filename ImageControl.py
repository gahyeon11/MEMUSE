from flask import Flask, render_template, jsonify, send_from_directory,request
import os
from rembg import remove
from io import BytesIO
from PIL import Image

app = Flask(__name__)
OBJECT_FOLDER = 'object'
PROCESSED_FOLDER = 'processed'

@app.route("/")
def index():
    return render_template("Imagever2.html")

@app.route('/processed/<filename>')
def send_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route("/images")
def get_images():
    # Process new images
    object_images = os.listdir(OBJECT_FOLDER)
    processed_images = os.listdir(PROCESSED_FOLDER)
    for image in object_images:
        if image not in processed_images and image.endswith(('png', 'jpg', 'jpeg')):
            input_path = os.path.join(OBJECT_FOLDER, image)
            output_path = os.path.join(PROCESSED_FOLDER, image.rsplit('.', 1)[0] + '.png')
            with open(input_path, "rb") as inp_file:
                input_data = inp_file.read()
                output_data = remove(input_data)
                # 바이트 데이터를 PIL 이미지로 변환
                image = Image.open(BytesIO(output_data))

                # 이미지를 PNG로 저장
                image.save(output_path, "PNG")
                    
    # Send processed images list
    images = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(('png'))]
    return jsonify(images=images)

@app.route('/save-image', methods=['POST'])
def save_image():
    try:
        image_data = request.data  # 클라이언트로부터 이미지 데이터 받기
        with open('saved_image.png', 'wb') as f:  # 파일로 이미지 저장
            f.write(image_data)
        return jsonify({'message': 'Image saved successfully'}), 200  # 성공 응답 반환
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to save image'}), 500  # 실패 응답 반환

if __name__ == "__main__":
    app.run(debug=True)
