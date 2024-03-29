from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.mymungo                       # 'mymungo'라는 이름의 db를 만듭니다.

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'mymungolibrary'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')

@app.route('/register')
def register():
   return render_template('sign_up.html')

@app.route('/main')
def main():
   return render_template('main.html')

@app.route('/write')
def write():
   return render_template('write.html')

@app.route('/main_list')
def main_list():
   return render_template('main_list.html')

@app.route('/member_info')
def member_info():
   return render_template('member_info.html')

@app.route('/search')
def search():
   return render_template('search.html')

@app.route('/search/result')
def search_result():
   return render_template('search_result.html')


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# email, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():

## 클라이언트로부터 데이터를 받는 부분
   user_email_receive = request.form['user_email_give']
   user_pw_receive = request.form['user_pw_give']
   user_id_receive = request.form['user_id_give']
   user_phone_receive = request.form['user_phone_give']
   user_birth_receive = request.form['user_birth_give']

   pw_hash = hashlib.sha256(user_pw_receive.encode('utf-8')).hexdigest()

# mongoDB에 넣는 부분
   account = {'user_email': user_email_receive,
              'user_pw': pw_hash,
              'user_id': user_id_receive,
              'user_phone': user_phone_receive,
              'user_birth': user_birth_receive}

   db.accounts.insert_one(account)

   return jsonify({'result': 'success'})

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    user_email_receive = request.form['user_email_give']
    user_pw_receive = request.form['user_pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(user_pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.accounts.find_one({'user_email': user_email_receive,'user_pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
       # JWT 토큰에는, payload와 시크릿키가 필요합니다.
       # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
       # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
       # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
       payload = {
          'user_email': user_email_receive,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
       }
       token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

       # token을 줍니다.
       return jsonify({'result': 'success','token':token})
    # 찾지 못하면
    else:
       return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)

@app.route('/api/nick', methods=['GET'])
def api_valid():
   # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
   # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
   token_receive = request.headers['token_give']

   # try / catch 문?
   # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

   try:
      # token을 시크릿키로 디코딩합니다.
      # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      print(payload)

      # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
      # 여기에선 그 예로 닉네임을 보내주겠습니다.
      userinfo = db.accounts.find_one({'user_email':payload['user_email']},{'_id':0})
      return jsonify({'result': 'success','nickname':userinfo['user_id']})
   except jwt.ExpiredSignatureError:
      # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
      return jsonify({'result': 'fail', 'msg':'로그인 시간이 만료되었습니다.'})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)