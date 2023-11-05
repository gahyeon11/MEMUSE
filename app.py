from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import requests
import os  # 환경 변수를 사용하기 위해 import
import logging  # 로깅 모듈 추가

app = Flask(__name__)
CORS(app)

# 데이터베이스 파일 생성 및 연결
conn = sqlite3.connect('translations.db', check_same_thread=False)
c = conn.cursor()

# 테이블 생성 (이미 존재하는 경우 생략)
c.execute('''
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_text TEXT,
        translated_text TEXT
    )
''')
conn.commit()

@app.route("/")
def index():
    return render_template("index.html")



# 네이버 파파고 API 키 값
NAVER_CLIENT_ID = 'fIfMjFH9VJ1GjQPim7j5'
NAVER_CLIENT_SECRET = 'iue1sb53T7'

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()  # `request.json` 대신 `request.get_json()` 사용
        if data is None or 'text' not in data:
            app.logger.error('No text field in the request')
            return jsonify(status="failure", error="No text field in the request"), 400

        text = data['text'].strip()
        if not text:
            app.logger.error('Text field is empty')
            return jsonify(status="failure", error="Text field is empty"), 400

        # 네이버 파파고 API 요청
        url = 'https://openapi.naver.com/v1/papago/n2mt'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET,
        }
        body = {
            'source': 'ko',
            'target': 'en',
            'text': text
        }
        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            return jsonify(status="failure", error="Translation API request failed"), 500

        translated_text = response.json().get('message', {}).get('result', {}).get('translatedText', "")
        return jsonify(status="success", translated_text=translated_text)

    except Exception as e:
        app.logger.error('Exception: %s', str(e))
        return jsonify(status="failure", error=str(e)), 500

@app.route('/save-results', methods=['POST'])
def save_results():
    try:
        data = request.json
        original_text = data.get('originalText')
        translated_text = data.get('translatedText')

        if not original_text or not translated_text:
            raise ValueError("Invalid data")

        # 데이터베이스에 저장
        c.execute('INSERT INTO translations (original_text, translated_text) VALUES (?, ?)', 
                  (original_text, translated_text))
        conn.commit()

        return jsonify(status="success", original_text=original_text, translated_text=translated_text)

    except ValueError as e:
        return jsonify(status="failure", error=str(e)), 400
    except Exception as e:
        return jsonify(status="failure", error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)