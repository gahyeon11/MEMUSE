from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import g 
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from PIL import Image, PngImagePlugin, ImageEnhance, ImageFilter
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,  SubmitField
from wtforms.validators import DataRequired
import sqlite3
import pyscrypt
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
from flask_bcrypt import Bcrypt
from wtforms.validators import DataRequired
import pymysql
import shutil


pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

app.secret_key = '0000'

db_path = 'translations.db'

# 절대 경로로 변환
absolute_path = os.path.abspath(db_path)

# 데이터베이스 연결

conn = sqlite3.connect('translations.db', check_same_thread=False)
c = conn.cursor()

# # translations 테이블 생성 쿼리
c.execute('''
     CREATE TABLE IF NOT EXISTS translations (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         original_text TEXT,
         translated_text TEXT
     )
''')

# # 변경 내용 저장
conn.commit()

# # 연결 종료
# # conn.close()

# # 전역 변수로 번역된 텍스트를 저장
# translated_text = ""


# conn = sqlite3.connect('users.db', check_same_thread=False)
# c = conn.cursor()

# 번역 함수
def translate_text(text_to_translate):
    try:
        # Naver Papago API에 번역 요청
        naver_client_id = 'fIfMjFH9VJ1GjQPim7j5'
        naver_client_secret = 'iue1sb53T7'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Naver-Client-Id': naver_client_id,
            'X-Naver-Client-Secret': naver_client_secret,
        }
        data = {
            'source': 'ko',
            'target': 'en',
            'text': text_to_translate,
        }
        response = requests.post('https://openapi.naver.com/v1/papago/n2mt', headers=headers, data=data)
        translated_text = response.json()['message']['result']['translatedText']
        return translated_text
    except Exception as e:
        return str(e)

# 번역 요청을 처리하는 엔드포인트
@app.route('/translate', methods=['POST'])
def translate_endpoint():
    try:
        request_data = request.json
        text_to_translate = request_data['text']
        translated_text = translate_text(text_to_translate)
        return jsonify({'translatedText': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)})

# @app.route('/get_translation', methods=['GET'])
# def get_translation():
#     try:
#         # 데이터베이스에서 데이터를 가져옴
#         conn = sqlite3.connect(absolute_path, check_same_thread=False)
#         c = conn.cursor()
#         c.execute("SELECT * FROM your_table")
#         data = c.fetchall()
#         conn.close()

#         # 가져온 데이터를 JSON 형식으로 응답
#         response_data = [{"id": row[0], "text": row[1]} for row in data]
#         return jsonify(response_data)
#     except Exception as e:
#         return jsonify({"error": str(e)})


conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
bcrypt = Bcrypt()

url = "http://127.0.0.1:7860"

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://myuser:mypassword@localhost/mydatabase'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "123123123"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

db_path = 'translations.db'
absolute_path = os.path.abspath(db_path)
conn = sqlite3.connect(absolute_path, check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_text TEXT,
        translated_text TEXT
    )
''')
conn.commit()
app.config['SQLALCHEMY_POOL_SIZE'] = 50  # 최대 연결 수
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 60  # 연결 타임아웃 (초)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600  # 연결 재사용 주기 (초)


def close_connection(exception):
    if conn:
        conn.close()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    birthdate = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    pwd = db.Column(db.String(512), nullable=False)

    def set_pwd(self, pwd):
        self.pwd = pwd
    
    def check_pwd(self, pwd):
        return self.pwd == pwd
    
    def __init__(self, name, birthdate, username, pwd):
        self.name = name
        self.birthdate = birthdate
        self.username = username
        self.pwd = pwd

class ImageModel(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(128), nullable=False)
    caption = db.Column(db.String(512))
    user = db.relationship('User', foreign_keys=[user_id], backref='images')
    def __init__(self, user_id, file_path, title, category, caption=None):
        self.user_id = user_id
        
        self.file_path = file_path
        self.title = title
        self.category = category
        self.caption = caption


class ImageInfoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    caption = TextAreaField('Caption')
    submit = SubmitField('저장')

class ProImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    background_image_path = db.Column(db.String(255))  # 배경 이미지 파일 경로
    object_image_paths = db.Column(db.String(255))  # 오브젝트 이미지 파일 경로들
    user_id = db.Column(db.Integer)  # 사용자 ID

@app.route('/')
def index():
    return render_template('intro.html')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


with app.app_context():
    db.create_all()

# @app.route('/translate', methods=['POST'])
# def translate():
#     try:
#         data = request.json
#         text = data.get('text')

#         if not text:
#             raise ValueError("No text provided")

#         client_id = 'fIfMjFH9VJ1GjQPim7j5'
#         client_secret = 'iue1sb53T7'

#         url = 'https://openapi.naver.com/v1/papago/n2mt'
#         headers = {
#             'Content-Type': 'application/json',
#             'X-Naver-Client-Id': client_id,
#             'X-Naver-Client-Secret': client_secret,
#         }
#         data = {
#             'source': 'ko',
#             'target': 'en',
#             'text': text
#         }
       
#         response = requests.post(url, headers=headers, json=data)

#         if response.status_code != 200:
#             raise Exception("Translation API request failed")

#         translated_text = response.json().get('message', {}).get('result', {}).get('translatedText', "")

#         c.execute("INSERT INTO translations (original_text, translated_text) VALUES (?, ?)", (text, translated_text))
#         conn.commit()

#         return jsonify(status="success", message="서버 저장 성공", translated_text=translated_text)

#     except ValueError as e:
#         logging.error(f"ValueError: {e}")
#         return jsonify(status="failure", error=str(e), message="서버 저장 실패"), 400
#     except Exception as e:
#         logging.error(f"Exception: {e}")
#         return jsonify(status="failure", error=str(e), message="서버 저장 실패"), 500

# @app.route('/save_results', methods=['POST'])
# def save_results():
#     try:
#         data = request.json
#         original_text = data.get('originalText')
#         translated_text = data.get('translatedText')

#         c.execute("INSERT INTO translations (original_text, translated_text) VALUES (?, ?)", (original_text, translated_text))
#         conn.commit()

#         return jsonify(status="success", message="Result saved successfully")
#     except Exception as e:
#         logging.error(f"Exception: {e}")
#         return jsonify(status="failure", error=str(e), message="Failed to save result"), 500

# @app.route('/get_translation', methods=['GET'])
# def get_translation():
#     translated_text = getattr(g, 'translated_text', None)
    
#     if translated_text:
#         return jsonify(status="success", translated_text=translated_text)
#     else:
#         return jsonify(status="failure", message="저장된 번역이 없음"), 404

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate = request.form.get('birthdate')
        username = request.form.get('username')
        pwd = request.form.get('pwd')  # 비밀번호 값을 받아옵니다.
        # 데베에 뉴유저 추가
               # 데이터베이스에서 동일한 username을 가진 사용자가 있는지 확인
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('join'))

        # 새 사용자 생성 및 데이터베이스에 추가
        new_user = User(name=name, birthdate=birthdate, username=username, pwd=pwd)
        db.session.add(new_user)
        db.session.commit()
        flash('Successfully signed up! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('join.html')
    
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
            
        # 사용자가 존재하는지 확인
        user = User.query.filter_by(username=username).first()
        if user and user.check_pwd(pwd):
            # 로그인 성공 처리
            session['logged_in'] = True
            # session['user'] = user.username 
            session['user_id'] = user.id 
            session['username'] = username
            return redirect(url_for('workplace'))
        else:
            # 로그인 실패 처리
            flash('Invalid username or password', 'error')
                
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
    page = request.args.get('page', 1, type=int)  # URL에서 페이지 번호를 가져옴, 기본값은 1
    per_page = 3  # 한 페이지당 표시할 이미지 수
    # 카테고리가 "helloflatcute2d_V10.safetensors [5a7204177d]"인 이미지만 필터링하고 페이지네이션 적용
    pagination = ImageModel.query.filter_by(category="helloflatcute2d_V10.safetensors [5a7204177d]").paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items  # 현재 페이지의 이미지들
    username = session.get('username', 'Guest')
    return render_template('cartoon_gallery1.html', images=images, pagination=pagination)

# @app.route('/cartoon_gallery2')
# def cartoon_gallery2():
#     cartoon_images = ImageModel.query.filter_by(category='cartoon').all()

#     return render_template('cartoon_gallery2.html')

# @app.route('/cartoon_gallery3')
# def cartoon_gallery3():
#     cartoon_images = ImageModel.query.filter_by(category='cartoon').all()

#     return render_template('cartoon_gallery3.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/live_gallery1')
def live_gallery1():
    page = request.args.get('page', 1, type=int)  # URL에서 페이지 번호를 가져옴, 기본값은 1
    per_page = 3  # 한 페이지당 표시할 이미지 수

    # 카테고리가 "helloflatcute2d_V10.safetensors [5a7204177d]"인 이미지만 필터링하고 페이지네이션 적용
    pagination = ImageModel.query.filter_by(category="chosenMix_bakedVae.safetensors [52b8ebbd5b]").paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items  # 현재 페이지의 이미지들

    return render_template('live_gallery1.html', images=images, pagination=pagination)

# @app.route('/live_gallery2')
# def live_gallery2():
#     live_images = ImageModel.query.filter_by(category='live').all()

#     return render_template('live_gallery2.html', images=live_images)

# @app.route('/live_gallery3')
# def live_gallery3():
#     live_images = ImageModel.query.filter_by(category='live').all()

#     return render_template('live_gallery3.html', images=live_images)

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
    form = ImageInfoForm()
    username = session.get('username', 'Guest')

    # 이미지 제목과 캡션 입력 폼을 렌더링
    form = ImageInfoForm()

    username = session.get('username', 'Guest')
    return render_template('new_complete.html', username=username, form=form)


@app.route('/new_filter', methods=['GET', 'POST'])
def new_filter():
    if request.method == 'POST':
        if not session.get('file_path'):
            flash('Image file is missing.', 'error')
            return redirect(url_for('new_object'))
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_number = request.form.get('filter')
        if not filter_number:
            # 적절한 오류 메시지를 표시하거나 기본 값을 설정
            flash('Filter number is required.', 'error')
            return redirect(url_for('new_object')) 
        file_path = session.get('file_path') 
        if not file_path:
            flash('Image file is missing.', 'error')
            return redirect(url_for('new_object'))
        full_file_path = os.path.join(app.static_folder, file_path)
        print("Attempting to open:", full_file_path)
                # 파일 존재 여부 확인
        if not os.path.exists(full_file_path):
            flash('Image file not found.', 'error')
            return redirect(url_for('new_object'))
        image = Image.open(full_file_path)
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
        
        
        filter_file_name = f'fin/output_t2i_{filter_number}_{current_time}.png'
        image.save(os.path.join(app.static_folder, filter_file_name))
        session['file_path'] = filter_file_name
        print(filter_file_name)
        # 이미지 저장(db x)
        # image.save(file_name, pnginfo = pnginfo)
        
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
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f'object/output_t2i_{current_time}.png'
            image.save(os.path.join(app.static_folder, file_name))
            session['file_path'] = file_name
            # 이미지 저장(db x)
            # image.save(file_name, pnginfo = pnginfo)
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

    form = ImageInfoForm()
    if form.validate_on_submit():
        try:
            db.session.begin_nested()
            title = form.title.data
            caption = form.caption.data
            user_id = session.get('user_id')  # 세션에서 사용자 ID를 가져옴

            if user_id is None:
                flash('사용자 ID가 없습니다. 다시 로그인하십시오.', 'error')
                return redirect(url_for('login'))

            file_path = session.get('file_path')
            print(file_path)
            image_style = session.get('image_style', 'default_style')
            print(f"Title: {title}, Caption: {caption}, User ID: {user_id}, File Path: {file_path}, Image Style: {image_style}")
            new_image = ImageModel(user_id=user_id, file_path=file_path, title=title, category=image_style, caption=caption)
            db.session.add(new_image)
            db.session.commit()
            session['title'] = title
            session['caption'] = caption
            flash('작품이 저장되었습니다!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('오류가 발생했습니다.', 'error')
        finally:
            db.session.close()  # 데이터베이스 세션을 명시적으로 닫음

        return redirect(url_for('new_save_success'))

    username = session.get('username', 'Guest')
    title = session.get('title', '')
    caption = session.get('caption', '')
    return render_template('new_save_success.html', username=username, form=form, title=title, caption=caption)

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
    page = request.args.get('page', 1, type=int) 
    per_page = 3  

   
    pagination = ImageModel.query.filter_by(category="pastelMixStylizedAnime_pastelMixPrunedFP16.safetensors [d01a68ae76]").paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items  # 현재 페이지의 이미지들

    return render_template('pastel_gallery1.html', images=images, pagination=pagination)

# @app.route('/pastel_gallery2')
# def pastel_gallery2():
#     pastel_images = ImageModel.query.filter_by(category='pastel').all()

#     return render_template('pastel_gallery2', images=pastel_images)

# @app.route('/pastel_gallery3')
# def pastel_gallery3():
#     pastel_images = ImageModel.query.filter_by(category='pastel').all()

#     return render_template('pastel_gallery3', images=pastel_images)

@app.route('/pro_back', methods=['GET', 'POST'])
def pro_back():
    # payload 값 참조
    global payload
    
    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json
        user_input = data['translatedText']

        # prompt 문자열에 추가
        payload["prompt"] += "landscape, no human, " + user_input + ", "
        payload["negative_prompt"] += "nsfw, lowres, wortst quality, watermark, bad hands, missing fingers, extra arms, bed legs, human, "

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
    background_folder = 'static/background'
    
    # 'background' 폴더 내의 모든 파일 나열
    background_images = [filename for filename in os.listdir(background_folder) if filename.endswith(".png")]
    
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    print(payload)
    r = response.json()
    
    # 이미지 저장, 텍스트 데이터를 이진 데이터로 디코딩
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        # API 요청을 보내 이미지 정보 검색
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        # PIL 이미지에 메타 데이터 삽입
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        # 현재 날짜와 시간을 문자열로 가져와 파일 이름으로 설정
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.join(background_folder, f'output_t2i{current_time}.png')  # 경로 수정
        
        # 이미지 저장
        image.save(file_name, pnginfo=pnginfo)
    
    # 가장 최근에 저장된 이미지 파일 경로 찾기
    latest_image_path = None
    if background_images:
        latest_image_path = os.path.join('background', background_images[-1])  # 경로 수정
        latest_image_path = latest_image_path.replace('\\', '/')  # 백슬래시를 슬래시로 변경
    
    username = session.get('username', 'Guest')
    return render_template('pro_back_complete.html', username=username, latest_image_path=latest_image_path)

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
    return process_edit_object()

@app.route('/list_processed_images')
def list_processed_images():
    pro_object_folder = 'static/processed'  # 수정된 폴더 경로

    # 처리된 이미지 파일 목록 가져오기
    processed_image_files = os.listdir(pro_object_folder)

    # JSON 형식으로 반환
    return jsonify(processed_image_files)
    
@app.route('/pro_edit_shot_check')
def pro_edit_shot_check():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_check.html', username=username)

@app.route('/pro_edit_shot_num')
def pro_edit_shot_num():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_num.html', username=username)
@app.route('/pro_filter', methods=['GET', 'POST'])
def pro_filter():
    if request.method == 'POST':
        if not session.get('file_path'):
            flash('Image file is missing.', 'error')
            return redirect(url_for('pro_filter'))
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_number = request.form.get('filter')
        if not filter_number:
            # 적절한 오류 메시지를 표시하거나 기본 값을 설정
            flash('Filter number is required.', 'error')
            return redirect(url_for('pro_filter')) 
        file_path = session.get('file_path') 
        if not file_path:
            flash('Image file is missing.', 'error')
            return redirect(url_for('pro_filter'))
        full_file_path = os.path.join(app.static_folder, file_path)
        print("Attempting to open:", full_file_path)
                # 파일 존재 여부 확인
        if not os.path.exists(full_file_path):
            flash('Image file not found.', 'error')
            return redirect(url_for('pro_filter'))
        image = Image.open(full_file_path)

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
        
        
        file_name = f'pro_object/output_t2i_{filter_number}_{current_time}.png'
        image.save(os.path.join(app.static_folder, file_name))

        session['file_path'] = file_name
        
        return redirect(url_for('pro_complete'))
    
    # GET 요청
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

@app.route('/pro_object', methods=['GET', 'POST'])
def pro_object():
    # payload 값 참조
    global payload
    
    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json
        user_input = data['translatedText']
        
        # prompt 문자열에 추가
        payload["prompt"] += user_input + ", "
        payload["negative_prompt"] += "nsfw, lowres, wortst quality, watermark, bad hands, missing fingers, extra arms, bed legs, "

        print("payload 확인:", payload)
        translatedText = data.get('translatedText', '')

        # 서버 로그에 출력
        app.logger.info(f'Translated Text: {translatedText}')
        
        # 다음 페이지 리디렉션 url
        redirect_url = url_for('pro_object_complete')
        return jsonify(redirect = redirect_url)
    
    else:
        # prompt 초기화
        payload["prompt"] = "masterpiece, best quality, highres, "
        payload["negative_prompt"] = "easynegative, "
        
        print(payload)
        
        # GET 요청 시 HTML 반환
        print(translate_text)
        username = session.get('username', 'Guest')
        return render_template('pro_object.html', username=username)
    
@app.route('/pro_object_complete')
def pro_object_complete():
    # 이미지 생성 코드
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    print(payload)
    r = response.json()
    
    # 이미지 저장, 텍스트 데이터를 이진 데이터로 디코딩
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        # API 요청을 보내 이미지 정보 검색
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        # PIL 이미지에 메타 데이터 삽입
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        # 현재 날짜와 시간을 문자열로 가져와 파일 이름으로 설정
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'static/pro_object/output_t2i{current_time}.png'
        
        # 이미지 저장
        image.save(file_name, pnginfo=pnginfo)
    
    # 가장 최근에 저장된 이미지 파일 경로 찾기
    latest_image_path = None
    pro_object_folder = 'static/pro_object'
    pro_object_images = [filename for filename in os.listdir(pro_object_folder) if filename.endswith(".png")]
    
    if pro_object_images:
        latest_image_path = os.path.join('pro_object', pro_object_images[-1])  # 경로 수정
        latest_image_path = latest_image_path.replace('\\', '/')  # 백슬래시를 슬래시로 변경
    
    username = session.get('username', 'Guest')
    return render_template('pro_object_complete.html', username=username, latest_image_path=latest_image_path)

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
    page = request.args.get('page', 1, type=int) 
    per_page = 3  
    # 카테고리가 "helloflatcute2d_V10.safetensors [5a7204177d]"인 이미지만 필터링하고 페이지네이션 적용
    pagination = ImageModel.query.filter_by(category="pasteldiffusedmix_v22.safetensors [7d21f7acff]").paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items  # 현재 페이지의 이미지들
    return render_template('watercolor_gallery1.html', images=images, pagination=pagination)

# @app.route('/watercolor_gallery2')
# def watercolor_gallery2():
#     return render_template('watercolor_gallery2.html', images=images, pagination=pagination)
# @app.route('/watercolor_gallery3')
# def watercolor_gallery3():
#     watercolor_images = ImageModel.query.filter_by(category='watercolor').all()

#     return render_template('watercolor_gallery3', images=watercolor_images)
@app.route('/whole_gallery1')
def whole_gallery1():
    page = request.args.get('page', 1, type=int)  # URL에서 페이지 번호를 가져옴, 기본값은 1
    per_page = 3  # 한 페이지당 표시할 이미지 수
    # paginate 메서드를 사용해 이미지를 페이지 별로 나눔
    pagination = ImageModel.query.paginate(page=page, per_page=per_page, error_out=False)
    images = pagination.items  # 현재 페이지의 이미지들
    # 수정된 리스트를 템플릿에 전달합니다.
    return render_template('whole_gallery1.html', images=images, pagination=pagination)
@app.route('/whole_gallery2')
def whole_gallery2():
    return render_template('whole_gallery2.html')

    
# @app.route('/whole_gallery2')
# def whole_gallery2():
#     return render_template('whole_gallery2.html')

# @app.route('/whole_gallery3')
# def whole_gallery3():
#     return render_template('whole_gallery3.html')

@app.route('/intro')
def intro():
 
    return render_template('intro.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.route('/delete_image', methods=['POST'])
def delete_image():
    background_folder = 'static/background'
    
    # 'background' 폴더의 모든 이미지 삭제
    for filename in os.listdir(background_folder):
        print("삭제")
        file_path = os.path.join(background_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'All images deleted successfully'}), 200
@app.route('/delete_object_image', methods=['POST'])
def delete_object_image():
    background_folder = 'static/pro_object'

    # 폴더 내의 모든 파일 목록을 얻고, 가장 최근에 수정된 파일 찾기
    try:
        files = [os.path.join(background_folder, f) for f in os.listdir(background_folder)]
        if not files:
            return jsonify({'message': 'No files to delete'}), 404

        latest_file = max(files, key=os.path.getmtime)
        print(f"삭제할 파일: {latest_file}")

        # 가장 최근 파일 삭제
        if os.path.isfile(latest_file) or os.path.islink(latest_file):
            os.unlink(latest_file)
        elif os.path.isdir(latest_file):
            shutil.rmtree(latest_file)

        return jsonify({'message': f'File {latest_file} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.session.begin()
        users = User.query.all()  # 모든 User 레코드를 조회합니다.
        # for user in users:
        #     print(user.id, user.name, user.birthdate, user.username, user.pwd)
        # images = ImageModel.query.all()  # ImageModel의 모든 인스턴스를 조회
        # for image in images:
        #     print(f'ID: {image.id}, User ID: {image.user_id}, File Path: {image.file_path}, Title: {image.title}, Created At: {image.created_at}, Category: {image.category}, Caption: {image.caption}')

        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
        try:
            db.create_all()  # 첫 실행에서만 필요하고 그 다음부터는 주석 처리
        except Exception as e:
            print(f"An error occurred while creating tables: {e}")

    app.run(debug=True)


