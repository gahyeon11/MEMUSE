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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # 새 사용자 객체를 생성할 때 해시된 비밀번호를 사용
        new_user = User(id=id,username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('-Xq3.html')  # HTML 파일명이 잘못되었을 수 있습니다. 실제 파일명을 확인하세요.

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
            return redirect(url_for('dashboard'))  # 함수명 'home'이 정의되지 않았습니다. 'dashboard'로 변경했습니다.
        else:
            return 'Invalid credentials'
    return render_template('-ucV.html')
# 기타 라우트들...
@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        # 대시보드 페이지를 보여주는 로직
        return render_template('dashboard.html')  # 'dashboard.html'은 실제 파일명으로 교체해야 합니다.
    else:
        # 사용자가 로그인하지 않았으면 로그인 페이지로 리디렉션
        return redirect(url_for('login'))
@app.route('/ucV')
def ucv():
    return render_template('-ucV.html')

@app.route('/')
def index():
    return render_template('-VAH.html') 

if __name__ == '__main__':
    app.run(debug=True)
