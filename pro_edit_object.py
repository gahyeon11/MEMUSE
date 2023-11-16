from flask import render_template, session, url_for
from rembg import remove
import os
import logging
logging.getLogger('numba').setLevel(logging.WARNING)

def process_edit_object():
    username = session.get('username', 'Guest')

    # 수정된 경로: 'static/background'와 'static/pro_object'
    # 수정된 경로: 'static/background'와 'static/pro_object'
    background_folder = 'static/background'
    pro_object_folder = 'static/pro_object'

    # 배경 이미지 선택 (가장 최근 파일)
    background_images = os.listdir(background_folder)
    if background_images:
        latest_background = max(background_images, key=lambda x: os.path.getmtime(os.path.join(background_folder, x)))
        background_image_url = 'background/' + latest_background
        background_image_url = 'background/' + latest_background
    else:
        background_image_url = None
        background_image_url = None

    # 객체 이미지 선택 및 배경 제거
    processed_image_paths = []
    for object_image_file in os.listdir(pro_object_folder):
        object_image_path = os.path.join(pro_object_folder, object_image_file)
        # 경로에서 역슬래시(\)를 슬래시(/)로 변환하고, 'static/'을 제거
        object_image_url = object_image_path.replace('\\', '/').replace('static/', '', 1)
    processed_image_paths = []
    for object_image_file in os.listdir(pro_object_folder):
        object_image_path = os.path.join(pro_object_folder, object_image_file)
        # 경로에서 역슬래시(\)를 슬래시(/)로 변환하고, 'static/'을 제거
        object_image_url = object_image_path.replace('\\', '/').replace('static/', '', 1)
        with open(object_image_path, 'rb') as file:
            input_image = file.read()
        output_image = remove(input_image)
        
        # 결과 이미지 저장 (예: 'static/processed/object.png')
        processed_file_name = 'processed/' + object_image_file
        processed_image_path = processed_file_name.replace('static/', '', 1)
        processed_image_abs_path = os.path.join('static', processed_file_name)
        with open(processed_image_abs_path, 'wb') as file:
        
            file.write(output_image)
        processed_image_paths.append(processed_image_path)

    return render_template('pro_edit_object.html', username=username, background_image=background_image_url, object_image=object_image_url, processed_image=processed_image_path)
