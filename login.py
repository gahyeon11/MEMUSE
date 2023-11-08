from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import io
import json
import sqlite3
from PIL import Image, PngImagePlugin
from datetime import datetime


app = Flask(__name__)
CORS(app)

# Stable Diffusion의 로컬 주소
url = "http://127.0.0.1:7860"
# Stable Diffusion에 적용될 프롬프트
payload = {
    "prompt" : "masterpiece, best quality, highres, ",
    "negative_prompt" : "easynegative"
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
@app.context_processor
def inject_user():
    if 'username' in session:
        return dict(username=session['username'])
    return dict(username=None)
class User(db.Model):
    """ 사용자 테이블 생성 """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 해시된 비밀번호 저장을 위해 필드 길이 증가
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password)  # 생성자에서 비밀번호를 해시하여 저장
        self.email = email


with app.app_context():
    db.create_all()

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # 해시된 비밀번호를 저장
        email = request.form['email']

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('join.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # 비밀번호가 일치하는 경우
            session['logged_in'] = True
            session['username'] = user.username
            return redirect(url_for('join_success'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')
@app.route('/join_success')
def join_success():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        # 세션에서 username을 가져와서 dashboard.html에 전달합니다.
        username = session.get('username')
        return render_template('join_success.html', username=username)
@app.route('/workplace')
def workplace():
    global payload
    # payload 초기화
    payload = {
    "prompt" : "",
    "negative_prompt" : "easynegative"
    }
    print(payload)
    return render_template('workplace.html')

@app.route('/voice_login_join_choice')
def voice_login_join_choice():
    # Your logic here
    return render_template('voice_login_join_choice.html')

@app.route('/cartoon_gallery1')
def cartoon_gallery1():
    return render_template('cartoon_gallery1.html')

@app.route('/cartoon_gallery2')
def cartoon_gallery2():
    return render_template('cartoon_gallery2.html')

@app.route('/cartoon_gallery3')
def cartoon_gallery3():
    return render_template('cartoon_gallery3.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/live_gallery1')
def live_gallery1():
    return render_template('live_gallery1.html')

@app.route('/live_gallery2')
def live_gallery2():
    return render_template('live_gallery2.html')

@app.route('/live_gallery3')
def live_gallery3():
    return render_template('live_gallery3.html')

@app.route('/my_page')
def my_page():
    return render_template('my_page.html')

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
        return render_template('new_back.html')

@app.route('/new_complete')
def new_complete():
    return render_template('new_complete.html')

@app.route('/new_filter')
def new_filter():
    return render_template('new_filter.html')

@app.route('/new_no_save')
def new_no_save():
    return render_template('new_no_save.html')

@app.route('/new_object', methods=['GET', 'POST'])
def new_object():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_filter')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        return render_template('new_object.html')

@app.route('/new_save_success')
def new_save_success():
    return render_template('new_save_success.html')

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
        return render_template('new_shot.html')

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
        return render_template('new_style.html')

@app.route('/pastel_gallery1')
def pastel_gallery1():
    return render_template('pastel_gallery1.html')

@app.route('/pastel_gallery2')
def pastel_gallery2():
    return render_template('pastel_gallery2.html')

@app.route('/pastel_gallery3')
def pastel_gallery3():
    return render_template('pastel_gallery3.html')

@app.route('/pro_back')
def pro_back():
    return render_template('pro_back.html')

@app.route('/pro_back_complete')
def pro_back_complete():
    return render_template('pro_back_complete.html')

@app.route('/pro_complete')
def pro_complete():
    return render_template('pro_complete.html')

@app.route('/pro_edit_obj_check')
def pro_edit_obj_check():
    return render_template('pro_edit_obj_check.html')

@app.route('/pro_edit_obj_num')
def pro_edit_obj_num():
    return render_template('pro_edit_obj_num.html')
@app.route('/pro_edit_object')
def pro_edit_object():
    return render_template('pro_edit_object.html')

@app.route('/pro_edit_shot_check')
def pro_edit_shot_check():
    return render_template('pro_edit_shot_check.html')

@app.route('/pro_edit_shot_num')
def pro_edit_shot_num():
    return render_template('pro_edit_shot_num.html')

@app.route('/pro_filter')
def pro_filter():
    return render_template('pro_filter.html')

@app.route('/pro_lora')
def pro_lora():
    return render_template('pro_lora.html')

@app.route('/pro_lora_num')
def pro_lora_num():
    return render_template('pro_lora_num.html')

@app.route('/pro_more_edit_obj')
def pro_more_edit_obj():
    return render_template('pro_more_edit_obj.html')

@app.route('/pro_more_object')
def pro_more_object():
    return render_template('pro_more_object.html')

@app.route('/pro_more_specify_obj')
def pro_more_specify_obj():
    return render_template('pro_more_specify_obj.html')

@app.route('/pro_no_save')
def pro_no_save():
    return render_template('pro_no_save.html')

@app.route('/pro_object')
def pro_object():
    return render_template('pro_object.html')

@app.route('/pro_object_complete')
def pro_object_complete():
    return render_template('pro_object_complete.html')

@app.route('/pro_save_success')
def pro_save_success():
    return render_template('pro_save_success.html')

@app.route('/pro_specify_obj')
def pro_specify_obj():
    return render_template('pro_specify_obj.html')

@app.route('/pro_specify_obj_check')
def pro_specify_obj_check():
    return render_template('pro_specify_obj_check.html')

@app.route('/pro_specify_obj_check2')
def pro_specify_obj_check2():
    return render_template('pro_specify_obj_check2.html')

@app.route('/pro_specify_obj_num')
def pro_specify_obj_num():
    return render_template('pro_specify_obj_num.html')

@app.route('/pro_specify_obj_num2')
def pro_specify_obj_num2():
    return render_template('pro_specify_obj_num2.html')

@app.route('/pro_style')
def pro_style():
    return render_template('pro_style.html')

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
    return render_template('watercolor_gallery1.html')

@app.route('/watercolor_gallery2')
def watercolor_gallery2():
    return render_template('watercolor_gallery2.html')

@app.route('/watercolor_gallery3')
def watercolor_gallery3():
    return render_template('watercolor_gallery3.html')

@app.route('/whole_gallery1')
def whole_gallery1():
    return render_template('whole_gallery1.html')

@app.route('/whole_gallery2')
def whole_gallery2():
    return render_template('whole_gallery2.html')

@app.route('/whole_gallery3')
def whole_gallery3():
    return render_template('whole_gallery3.html')

@app.route('/intro')
def intro():
 
    return render_template('intro.html')

@app.route('/')
def index():
    return render_template('intro.html')

if __name__ == '__main__':
    app.run(debug=True)
