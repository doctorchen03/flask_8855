#v0.04 START
from flask import Flask, request, abort, render_template, url_for, flash, redirect,jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import flask_login #v0.04
#v0.04 END
import config
import openai
import aiapi as a
import pymysql
import logging
import sys
import traceback
from flask import session

#http://127.0.0.1:5000/
#python -m flask --app app run
######root@chatgptflask:/project/flask_8855# gunicorn -w 3 --bind 0.0.0.0:8000 app
#root@chatgptflask:/project/flask_8855# gunicorn -w 3 --bind 127.0.0.1:8000 app


def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])
app.secret_key = 'super secret string'  # Change this!
app.register_error_handler(404, page_not_found)
# v0.04 START
users = {'admin': {'password': 'admin@PSWD'},'user': {'password': 'user@PSWD'}}
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = '任何緯創軟體的問題或支援，我都可以幫上忙'
# v0.04 END

@app.route('/', methods = ['POST', 'GET'])
@login_required#v0.04
def chat():
    #print(session['_user_id'])
    if request.method == 'POST':
        prompt_question = str(request.form['prompt_question']).strip()
        #SetChatHistory(prompt_question, '', 'TEST')#[TEST CODE]
        chat_input_session_token = str(request.form['chat_input_session_token']).strip()
        token = a.GetSessionToken(prompt_question, chat_input_session_token)
        a.SetChatHistory(prompt_question, "Q", token)#0.05 
        res = {}
        res['answer'] = a.generateChatResponse(prompt_question, chat_input_session_token)
        res['chat_input_session_token'] = token
        a.SetChatHistory(res['answer'], "A", token) 
        res_json = jsonify(res)
        #print(res_json)
        return res_json, 200

    return render_template('chat.html', **locals())

#0.04 START
@app.route('/chat_history', methods = ['POST', 'GET'])
@login_required#v0.04
def chat_history():
    #print('/chat_history')#[TEST CODE]
    sql = ''' SELECT `CHAT_HISTORY`.`id`,
    `CHAT_HISTORY`.`token`,
    `CHAT_HISTORY`.`user`,
    `CHAT_HISTORY`.`role`,
    `CHAT_HISTORY`.`data`,
    `CHAT_HISTORY`.`create_datetime` 
    FROM sys.CHAT_HISTORY ORDER BY create_datetime DESC '''
    conn = pymysql.connect(**a.db_settings)
    with conn.cursor() as cursor:
        cursor.execute(sql)
        logging.info(sql)
        res_data = cursor.fetchall()
        #print(res_data)#[TEST CODE]
        return render_template('chat_history.html', **locals(), data=res_data)    

class User(UserMixin):
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    user_id = request.form['user_id']
    if (user_id in users) and (request.form['password'] == users[user_id]['password']):
        user = User()
        user.id = user_id
        login_user(user)
        a._login_user = user_id

        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = current_user.get_id()
    logout_user()
    return render_template('login.html') 

@login_manager.user_loader
def user_loader(user_id):
    if user_id not in users:
        return

    user = User()
    user.id = user_id
    return user


@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('user_id')
    if user_id not in users:
        return

    user = User()
    user.id = user_id

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[user_id]['password']

    return user
#0.04 END

#0.05 START
@app.route('/reservation_history', methods = ['POST', 'GET'])
@login_required#v0.05
def reservation_history():
    try:
        #print('/chat_history')#[TEST CODE]
        sql = ''' SELECT r.id,
r.room_id,
r.start,
r.end,
r.applicant,
r.contact_phone,
r.contact_email,
r.purpose,
r.confirmation_status, 
m.room_name
FROM sys.RESERVATION r 
LEFT JOIN sys.MEETING_ROOM m
ON r.room_id=m.room_id
WHERE r.applicant='<user>' ORDER BY r.start DESC '''
        #session['_user_id']
        user_id = session['_user_id']
        if user_id != 'admin':
            sql = sql.replace('<user>', user_id)
            pass
        else:
            sql = sql.replace("WHERE r.applicant='<user>'", '')
            pass
        conn = pymysql.connect(**a.db_settings)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            logging.info(sql)
            res_data = cursor.fetchall()
            #print(res_data)#[TEST CODE]
            return render_template('reservation_history.html', **locals(), data=res_data)
    except Exception as e:
        s,r = getattr(e, 'message', str(e)), getattr(e, 'message', repr(e))
        traceback.print_exception(*sys.exc_info())
        logging.error(a.GetMsg(s))
        logging.error(a.GetMsg(r))
        logging.error(a.GetMsg(traceback.print_exception(*sys.exc_info())))
#0.05 END

from app import app as application
app = application

