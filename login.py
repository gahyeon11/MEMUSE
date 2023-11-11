from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from PIL import Image, PngImagePlugin, ImageEnhance, ImageFilter
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
import sqlite3
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import requests
import io
import json
import sqlite3
from PIL import Image, PngImagePlugin, ImageFilter
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
# Stable Diffusion의 로컬 주소
url = "http://127.0.0.1:7860"
# Stable Diffusion에 적용될 프롬프트
payload = {
    "prompt" : "masterpiece, best quality, highres, ",
    "negative_prompt" : "easynegative, "
    }

# 모델 리스트
models = [
    "helloflatcute2d_V10.safetensors [5a7204177d]",
    "pasteldiffusedmix_v22.safetensors [7d21f7acff]",
    "pastelMixStylizedAnime_pastelMixPrunedFP16.safetensors [d01a68ae76]",
    "chosenMix_bakedVae.safetensors [52b8ebbd5b]",
    "v1-5-pruned-emaonly.safetensors [6ce0161689]"
    ]

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "123123123"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

conn.commit()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    birthdate = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if password is None:
            return False
        return check_password_hash(self.password, password)

    def __init__(self, name, birthdate, username, password):
        self.name = name
        self.birthdate = birthdate
        self.username = username
        self.password = generate_password_hash(password)

class ImageModel(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(256))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(512))  


    user = db.relationship('User', backref=db.backref('images', lazy=True))

    def __init__(self, user_id, file_path, title, category, caption=None):
        self.user_id = user_id
        self.file_path = file_path
        self.title = title
        self.category = category
        self.caption = caption 
class MyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    caption = TextAreaField('Caption')
@app.route('/')
def index():
    return render_template('intro.html')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


with app.app_context():
    db.create_all()

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate = request.form.get('birthdate')
        username = request.form.get('username')
        password = request.form.get('password')
        print("get 저장")

        # 뉴유저 생성
        new_user = User(name=name, birthdate=birthdate, username=username, password=password)
        print("new 저장")

        # 데베에 뉴유저 추가
        try:
            # 데베에 뉴유저 추가
            db.session.add(new_user)
            db.session.commit()
            flash('Successfully signed up! Please login.', 'success')
            print("데베 저장")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            
            flash('Username already exists. Please choose a different one.', 'error')
            print("Username already exists. Please choose a different one.")
            
            return redirect(url_for('join'))

    return render_template('join.html')
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
            
        # 사용자가 존재하는지 확인
        user = User.query.filter_by(username=username).first()
        if user:                # 비밀번호가 맞는지 확인
            if user.check_password(password):
                session['logged_in'] = True
                session['user_id'] = user.username
                session['username'] = username
                session['name'] = user.name
                session['birthdate'] = user.birthdate
                return redirect(url_for('workplace'))
            else:
                # 개발 환경에서만 사용하고 실제 배포 시에는 제거하세요
                # 해시된 비밀번호와 입력된 비밀번호의 해시를 콘솔에 출력
                print(f"Stored hash: {user.password}")
                print(f"Entered hash: {generate_password_hash(password)}")
                flash('Invalid password', 'error')
                print("Incorrect password")
        else:
            flash('Invalid username', 'error')
            print("Username not found")
                
    return render_template('login.html')

# @app.route('/join_success')
# def join_success():
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))
#     else:
#         # 세션에서 username을 가져와서 dashboard.html에 전달합니다.
#         username = session.get('username')
#         return render_template('join_success.html', username=username)
    
@app.route('/workplace')
def workplace():
    if not session.get('logged_in'):
        flash('Please login to view this page.', 'error')
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    global payload
    # payload 초기화
    payload = {
    "prompt" : "",
    "negative_prompt" : "easynegative"
    }
    print(payload)
    return render_template('workplace.html',  username=username)

@app.route('/voice_login_join_choice')
def voice_login_join_choice():
    # Your logic here
    return render_template('voice_login_join_choice.html')

@app.route('/cartoon_gallery1')
def cartoon_gallery1():
    username = session.get('username', 'Guest')
    return render_template('cartoon_gallery1.html', username=username, images=cartoon_images)

@app.route('/cartoon_gallery2')
def cartoon_gallery2():
    cartoon_images = ImageModel.query.filter_by(category='cartoon').all()

    return render_template('cartoon_gallery2.html', images=cartoon_images)

@app.route('/cartoon_gallery3')
def cartoon_gallery3():
    cartoon_images = ImageModel.query.filter_by(category='cartoon').all()

    return render_template('cartoon_gallery3.html', images=cartoon_images)

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/live_gallery1')
def live_gallery1():
    live_images = ImageModel.query.filter_by(category='live').all()

    return render_template('live_gallery1.html', images=live_images)

@app.route('/live_gallery2')
def live_gallery2():
    live_images = ImageModel.query.filter_by(category='live').all()

    return render_template('live_gallery2.html', images=live_images)

@app.route('/live_gallery3')
def live_gallery3():
    live_images = ImageModel.query.filter_by(category='live').all()

    return render_template('live_gallery3.html', images=live_images)

@app.route('/my_page')
def my_page():
    if 'username' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    name = session.get('name', 'Guest')
    birthdate = session.get('birthdate', 'Guest')
    
    return render_template('my_page.html', username=username, name = name, birthdate = birthdate)

@app.route('/my_page_my_gallery1')
def my_page_my_gallery1():

    
    return render_template('my_page_my_gallery1.html')

@app.route('/my_page_my_gallery2')
def my_page_my_gallery2():
    return render_template('my_page_my_gallery2.html')

@app.route('/my_page_my_gallery3')
def my_page_my_gallery3():
    return render_template('my_page_my_gallery3.html')

@app.route('/new_back', methods=['GET', 'POST'])
def new_back():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_object')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_back.html', username=username)

@app.route('/new_complete', methods=['GET', 'POST'])
def new_complete():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    form = MyForm()  # 폼 객체를 생성하세요

    return render_template('new_complete.html', username=username, form=form)

@app.route('/new_filter', methods=['GET', 'POST'])
def new_filter():
    if request.method == 'POST':
        filter_number = request.form.get('filter')
        if not filter_number:
            # 적절한 오류 메시지를 표시하거나 기본 값을 설정
            flash('Filter number is required.', 'error')
            return redirect(url_for('new_object')) 
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = session.get('file_path', f'object/output_t2i_{current_time}.png')  # 세션에서 파일 경로를 가져옵니다.
        image = Image.open(file_path)
        print(file_path)
        print(filter_number)
        if filter_number == '1':
            pass
        elif filter_number == '2':
            image = image.point(lambda p: p * 1.1)
        elif filter_number == '3':
            lut_size = 8
            image = image.filter(ImageFilter.Color3DLUT.generate(lut_size, lambda r, g, b: (r, g*0.9, b*0.6)))
        elif filter_number == '4':
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  
        elif filter_number == '5':
        # '새벽하늘' 필터 예시: 파란색 톤을 강조합니다.
            r, g, b = image.split()
            b = b.point(lambda i: i * 1.2)  # 파란색 채널을 강화합니다.
            image = Image.merge('RGB', (r, g, b))
        elif filter_number == '6':
            # '낭만적' 필터 예시: 붉은색 톤을 강조합니다.
            r, g, b = image.split()
            r = r.point(lambda i: i * 1.2)  # 빨간색 채널을 강화합니다.
            image = Image.merge('RGB', (r, g, b))   
        elif filter_number == '7':
        # '높은 대비' 필터 예시: 대비를 증가시킵니다.
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # 대비를 두 배로 증가시킵니다.

        elif filter_number == '8':
            # '차분한' 필터 예시: 색상의 강도를 낮춥니다.
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.5)  # 색상의 강도를 낮춥니다.

        elif filter_number == '9':
            # '빈티지' 필터 예시: 세피아 톤을 적용하고, 콘트라스트를 약간 낮춤
            r, g, b = image.split()
            r = r.point(lambda i: i * 0.9)
            g = g.point(lambda i: i * 0.7)
            b = b.point(lambda i: i * 0.5)
            image = Image.merge('RGB', (r, g, b))
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.8)

        elif filter_number == '10':
            # '블루밍' 필터 예시: 전체적으로 밝고, 푸른 톤을 증가
            r, g, b = image.split()
            r = r.point(lambda i: i * 0.8)
            g = g.point(lambda i: i * 0.8)
            b = b.point(lambda i: i * 1.2)
            image = Image.merge('RGB', (r, g, b))
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.2)

        elif filter_number == '11':
            # '세피아' 필터 예시: 세피아 톤으로 이미지를 변환
            sepia_filter = Image.new('RGB', image.size, (255, 240, 192))
            image = Image.blend(image.convert('RGB'), sepia_filter, 0.3)

        elif filter_number == '12':
            # '흑백' 필터 예시: 이미지를 그레이스케일로 변환
            image = image.convert('L')     
        
        
        file_name = f'object/output_t2i_{filter_number}_{current_time}.png'
        session['file_path'] = file_name
        image.save(file_name)
        username = session.get('username', 'Guest')
        return redirect(url_for('new_complete'))
    username = session.get('username', 'Guest')
    return render_template('new_filter.html', username=username)

@app.route('/new_no_save')
def new_no_save():
    username = session.get('username', 'Guest')
    return render_template('new_no_save.html', username=username)


@app.route('/new_object', methods=['POST', 'GET'])
def new_object():
    if request.method == 'POST':
        data = request.json
        payload["prompt"] += data.get('prompt', '')
        payload["negative_prompt"] += data.get('negative', '')
        
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json = payload)
        print(payload)
        user_id = session.get('user_id', 'default_user_id')
        r = response.json()
        # 이미지 저장, 텍스트 데이터를 이진 데이터로 디코딩
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
            # API 요청을 보내 이미지 정보 검색
            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json = png_payload)
            # PIL 이미지에 메타 데이터 삽입
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            # 현재 날짜와 시간을 문자열로 가져와 파일 이름으로 설정
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f'object/output_t2i{current_time}.png'
            
            # 이미지 저장
            image.save(file_name, pnginfo = pnginfo)

        # 다음 페이지 리디렉션 url
        return jsonify(redirect=url_for('new_filter'))
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_object.html', username=username)


@app.route('/new_save_success', methods=['GET', 'POST'])
def new_save_success():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    form = MyForm()  # 폼 객체를 생성하세요
    print('save')
    if form.validate_on_submit():
        # 폼 데이터를 추출합니다.
        title = form.title.data
        caption = form.caption.data
        print(title, caption)
        user_id = session.get('user_id')
        file_path = session.get('file_path')
        image_style = session.get('image_style', 'default_style')  # image_style 값을 세션에서 가져옵니다.
        
        # 데이터베이스에 이미지 정보 저장
        new_image = ImageModel(
            user_id=user_id,
            file_path=file_path,
            title=title,
            category=image_style,  # 이미지 스타일을 카테고리로 사용
            caption=caption
        )
 
        db.session.add(new_image)
        db.session.commit()
                # 이미지 제목과 설명을 세션에 저장
        session['title'] = title
        session['caption'] = caption
        flash('작품이 저장되었습니다!', 'success')
        return redirect(url_for('new_save_success'))

    username = session.get('username', 'Guest')
    title = session.get('title')
    caption = session.get('caption')

    return render_template('new_save_success.html', username=username, form=form, title=title, caption = caption)

@app.route('/new_shot', methods=['GET', 'POST'])
def new_shot():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_back')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_shot.html', username=username)

@app.route('/new_style', methods=['GET', 'POST'])
def new_style():
    if request.method == 'POST':
        # POST 요청 시 JSON 처리
        data = request.json
        style_number = data['style']
        selected_model = models[style_number - 1]
        option_payload = {
            "sd_model_checkpoint" : selected_model
        }
        print(selected_model)
        session['image_style'] = selected_model
        # checkpoint 모델 변경
        response = requests.post(url = f'{url}/sdapi/v1/options', json = option_payload)

        # payload 옵션 추가
        options = data.get('options', {})
        if 'styleNumber' in options:
            del options['styleNumber'] #styleNumber 키 제거
        # payload 딕셔너리에 options 값 추가
        for key, value in options.items():
            payload[key] = value
        
        print("payload = ", payload)
        
        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_shot', _external=True)
        
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청 시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_style.html', username = username)

@app.route('/pastel_gallery1')
def pastel_gallery1():
    pastel_images = ImageModel.query.filter_by(category='pastel').all()

    return render_template('pastel_gallery1', images=pastel_images)

@app.route('/pastel_gallery2')
def pastel_gallery2():
    pastel_images = ImageModel.query.filter_by(category='pastel').all()

    return render_template('pastel_gallery2', images=pastel_images)

@app.route('/pastel_gallery3')
def pastel_gallery3():
    pastel_images = ImageModel.query.filter_by(category='pastel').all()

    return render_template('pastel_gallery3', images=pastel_images)

@app.route('/pro_back', methods=['GET', 'POST'])
def pro_back():
    # payload 값 참조
    global payload
    
    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json
        user_input = data['prompt']

        # prompt 문자열에 추가
        payload["prompt"] += "landscape, no human, " + user_input + ", "
        payload["negative_prompt"] += "nsfw, lowres, wortst quality, watermark, bad hands, missing fingers, extra arms, bed legs, "

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('pro_lora')
        return jsonify(redirect = redirect_url)
    
    else:
        # prompt 초기화
        payload["prompt"] = "masterpiece, best quality, highres, "
        payload["negative_prompt"] = "easynegative, "
        
        # GET 요청 시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('pro_back.html', username = username)

@app.route('/pro_back_complete')
def pro_back_complete():
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json = payload)
    print(payload)
    r = response.json()
    # 이미지 저장, 텍스트 데이터를 이진 데이터로 디코딩
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        # API 요청을 보내 이미지 정보 검색
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json = png_payload)
        # PIL 이미지에 메타 데이터 삽입
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        # 현재 날짜와 시간을 문자열로 가져와 파일 이름으로 설정
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'object/output_t2i{current_time}.png'
        
        # 이미지 저장
        image.save(file_name, pnginfo = pnginfo)
    
    username = session.get('username', 'Guest')
    return render_template('pro_back_complete.html', username=username)

@app.route('/pro_complete')
def pro_complete():
    username = session.get('username', 'Guest')
    return render_template('pro_complete.html', username=username)

@app.route('/pro_edit_obj_check')
def pro_edit_obj_check():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_obj_check.html', username=username)

@app.route('/pro_edit_obj_num')
def pro_edit_obj_num():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_obj_num.html', username=username)
@app.route('/pro_edit_object')
def pro_edit_object():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_object.html', username=username)

@app.route('/pro_edit_shot_check')
def pro_edit_shot_check():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_check.html', username=username)

@app.route('/pro_edit_shot_num')
def pro_edit_shot_num():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_num.html', username=username)

@app.route('/pro_filter')
def pro_filter():
    username = session.get('username', 'Guest')
    return render_template('pro_filter.html', username=username)

@app.route('/pro_lora', methods=['GET', 'POST'])
def pro_lora():
    # payload 값 참조
    global payload
    
    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json
        
        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')
        
        print("payload 확인:", payload)
        
        # 클라이언트에 응답
        return jsonify(success = True)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('pro_lora.html', username=username)

@app.route('/pro_lora_num', methods=['GET', 'POST'])
def pro_lora_num():
    # payload 값 참조
    global payload
    
    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json
        lora_num_data = data.get('prompt', '')
        
        # 받은 데이터를 숫자로 변환 후 계산
        try:
            num_value = float(lora_num_data)
            lora_num = num_value / 100
        except ValueError:
            # 데이터가 숫자로 변환되지 않는 경우
            return jsonify(success = False, message = "Invalid numeric value")
        
        # prompt 문자열에 추가
        payload["prompt"] += str(lora_num) + ">"

        print("최종 prompt 확인:", payload)
        # 클라이언트에 응답
        return jsonify(success = True)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('pro_lora_num.html', username=username)

@app.route('/pro_more_edit_obj')
def pro_more_edit_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_more_edit_obj.html', username=username)

@app.route('/pro_more_object')
def pro_more_object():
    username = session.get('username', 'Guest')
    return render_template('pro_more_object.html', username=username)

@app.route('/pro_more_specify_obj')
def pro_more_specify_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_more_specify_obj.html', username=username)

@app.route('/pro_no_save')
def pro_no_save():
    username = session.get('username', 'Guest')
    return render_template('pro_no_save.html', username=username)

@app.route('/pro_object')
def pro_object():
    username = session.get('username', 'Guest')
    return render_template('pro_object.html', username=username)

@app.route('/pro_object_complete')
def pro_object_complete():
    username = session.get('username', 'Guest')
    return render_template('pro_object_complete.html', username=username)

@app.route('/pro_save_success')
def pro_save_success():
    username = session.get('username', 'Guest')
    return render_template('pro_save_success.html', username=username)

@app.route('/pro_specify_obj')
def pro_specify_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj.html', username=username)

@app.route('/pro_specify_obj_check')
def pro_specify_obj_check():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj_check.html', username=username)

@app.route('/pro_specify_obj_check2')
def pro_specify_obj_check2():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj_check2.html', username=username)

@app.route('/pro_specify_obj_num')
def pro_specify_obj_num():
    username = session.get('username', 'Guest')
    
    return render_template('pro_specify_obj_num.html', username=username)

@app.route('/pro_specify_obj_num2')
def pro_specify_obj_num2():
    username = session.get('username', 'Guest')
    
    return render_template('pro_specify_obj_num2.html', username=username)

@app.route('/pro_style', methods=['GET', 'POST'])
def pro_style():
    if request.method == 'POST':
        # POST 요청 시 JSON 처리
        data = request.json
        style_number = data['style']
        selected_model = models[style_number - 1]
        option_payload = {
            "sd_model_checkpoint" : selected_model
        }
        print(selected_model)
        session['image_style'] = selected_model
        # checkpoint 모델 변경
        response = requests.post(url = f'{url}/sdapi/v1/options', json = option_payload)
        # payload 옵션 추가
        options = data.get('options', {})
        if 'styleNumber' in options:
            del options['styleNumber'] #styleNumber 키 제거
        # payload 딕셔너리에 options 값 추가
        for key, value in options.items():
            payload[key] = value
        
        print("payload = ", payload)
        
        # 다음 페이지 리디렉션 url
        redirect_url = url_for('pro_back', _external=True)
        
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청 시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('pro_style.html', username = username)

@app.route('/voice_join_success')
def voice_join_success():
    return render_template('voice_join_success.html')

@app.route('/voice_join1')
def voice_join1():
    return render_template('voice_join1.html')

@app.route('/voice_join2')
def voice_join2():
    return render_template('voice_join2.html')

@app.route('/voice_login')
def voice_login():
    return render_template('voice_login.html')

@app.route('/watercolor_gallery1')
def watercolor_gallery1():
    watercolor_images = ImageModel.query.filter_by(category='watercolor').all()

    return render_template('watercolor_gallery1', images=watercolor_images)

@app.route('/watercolor_gallery2')
def watercolor_gallery2():
    watercolor_images = ImageModel.query.filter_by(category='watercolor').all()

    return render_template('watercolor_gallery2', images=watercolor_images)

@app.route('/watercolor_gallery3')
def watercolor_gallery3():
    watercolor_images = ImageModel.query.filter_by(category='watercolor').all()

    return render_template('watercolor_gallery3', images=watercolor_images)
@app.route('/whole_gallery1')
def whole_gallery1():
    # ImageModel의 모든 인스턴스를 가져옵니다.
    images = ImageModel.query.all()

    # 수정된 리스트를 템플릿에 전달합니다.
    return render_template('whole_gallery1.html', images=images)
@app.route('/whole_gallery2')
def whole_gallery2():
    return render_template('whole_gallery2.html')

@app.route('/whole_gallery3')
def whole_gallery3():
    return render_template('whole_gallery3.html')

@app.route('/intro')
def intro():
 
    return render_template('intro.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        users = User.query.all()  # 모든 User 레코드를 조회합니다.
        for user in users:
            print(user.id, user.name, user.birthdate, user.username)
        images = ImageModel.query.all()  # ImageModel의 모든 인스턴스를 조회
        for image in images:
            print(f'ID: {image.id}, User ID: {image.user_id}, File Path: {image.file_path}, Title: {image.title}, Created At: {image.created_at}, Category: {image.category}, Caption: {image.caption}')

        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
        try:
            db.create_all()  # 첫 실행에서만 필요하고 그 다음부터는 주석 처리
        except Exception as e:
            print(f"An error occurred while creating tables: {e}")

    app.run(debug=True)