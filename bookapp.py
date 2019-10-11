from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.mymungo                     # 'mymungo'라는 이름의 db를 만듭니다.

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')

@app.route('/sign_up')
def sign_up():
   return render_template('sign_up.html')

@app.route('/main_whitespace')
def main_whitespace():
   return render_template('main.html')

##API역할을 하는 부분
@app.route('/sign', methods=['POST'])
def sign():

## 클라이언트로부터 데이터를 받는 부분
   user_email_receive = request.form['user_email_give']
   user_pw_receive = request.form['user_pw_give']
   user_id_receive = request.form['user_id_give']
   user_phone_receive = request.form['user_phone_give']
   user_birth_receive = request.form['user_birth_give']

# mongoDB에 넣는 부분
   account = {'user_email': user_email_receive, 'user_pw': user_pw_receive, 'user_id': user_id_receive, 'user_phone': user_phone_receive,
               'user_birth': user_birth_receive}

   db.accounts.insert_one(account)

   return jsonify({'result': 'success'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)