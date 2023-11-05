from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

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
        password = request.form['password']
        email = request.form['email']

        # 새 사용자 객체를 생성할 때 해시된 비밀번호를 사용
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
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        # 대시보드 페이지를 보여주는 로직
        return render_template('dashboard.html')
    else:
        # 사용자가 로그인하지 않았으면 로그인 페이지로 리디렉션
        return redirect(url_for('login'))
    
@app.route('/workplace')
def workplace():
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

@app.route('/join_success')
def join_success():
    return render_template('join_success.html')

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

@app.route('/new_back')
def new_back():
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

@app.route('/new_object')
def new_object():
    return render_template('new_object.html')

@app.route('/new_save_success')
def new_save_success():
    return render_template('new_save_success.html')

@app.route('/new_shot')
def new_shot():
    return render_template('new_shot.html')

@app.route('/new_style')
def new_style():
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

@app.route('/')
def index():
    return render_template('intro.html')

if __name__ == '__main__':
    app.run(debug=True)
