from flask import render_template, session, url_for
from rembg import remove
import os
import logging
logging.getLogger('numba').setLevel(logging.WARNING)


# 실제 이미지 처리 로직을 수행하는 함수
def process_edit_object():
    username = session.get('username', 'Guest')

    background_folder = 'static/background'
    pro_object_folder = 'static/pro_object'

    # 배경 이미지 선택 (가장 최근 파일)
    background_images = os.listdir(background_folder)
    if background_images:
        latest_background = max(background_images, key=lambda x: os.path.getmtime(os.path.join(background_folder, x)))
        background_image = url_for('static', filename=os.path.join('background', latest_background))
    else:
        background_image = None

    # 객체 이미지 선택 및 배경 제거
    object_images = os.listdir(pro_object_folder)
    processed_image_path = None
    if object_images:
        object_image_path = os.path.join(pro_object_folder, object_images[-1])
        with open(object_image_path, 'rb') as file:
            input_image = file.read()
        output_image = remove(input_image)
        # 결과 이미지 저장 (예: 'static/processed/object.png')
        processed_file_name = 'processed/object.png'
        processed_image_path = os.path.join('static', processed_file_name)
        with open(processed_image_path, 'wb') as file:
            file.write(output_image)
        processed_image_path = url_for('static', filename=processed_file_name)

    return render_template('pro_edit_object.html', username=username, background_image=background_image, object_image=processed_image_path)
