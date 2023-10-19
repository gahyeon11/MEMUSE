from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import requests
import logging  

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('translations.db', check_same_thread=False)
c = conn.cursor()

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

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text')

        if not text:
            raise ValueError("No text provided")

        client_id = 'fIfMjFH9VJ1GjQPim7j5'
        client_secret = 'iue1sb53T7'

        url = 'https://openapi.naver.com/v1/papago/n2mt'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret,
        }
        body = 'source=ko&target=en&text=' + text
        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception("Translation API request failed")

        translated_text = response.json().get('message', {}).get('result', {}).get('translatedText', "")

        c.execute("INSERT INTO translations (original_text, translated_text) VALUES (?, ?)", (text, translated_text))
        conn.commit()

        return jsonify(status="success", translated_text=translated_text, message="서버 저장 성공")

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return jsonify(status="failure", error=str(e), message="서버 저장 실패"), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify(status="failure", error=str(e), message="서버 저장 실패"), 500

@app.route("/translations", methods=["GET"])
def get_translations():
    try:
        c.execute("SELECT * FROM translations")
        translations = c.fetchall()
        return jsonify(translations), 200
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify(status="failure", error=str(e)), 500    

@app.route('/reset', methods=['GET'])
def reset():
    try:
        # 데이터베이스의 모든 데이터를 삭제
        c.execute("DELETE FROM translations")
        conn.commit()

        # 확인 메시지 반환
        return "Database has been reset!", 200
    except Exception as e:
        print(e)
        return "An error occurred while resetting the database.", 500
    
if __name__ == '__main__':
    app.run(debug=True)
