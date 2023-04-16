from flask import Flask, render_template, jsonify, request
import config
import openai
import aiapi as a
from flask_login import LoginManager

#http://127.0.0.1:5000/
#python -m flask --app app run
######root@chatgptflask:/project/flask_8855# gunicorn -w 3 --bind 0.0.0.0:8000 app
#root@chatgptflask:/project/flask_8855# gunicorn -w 3 --bind 127.0.0.1:8000 app


def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])

app.register_error_handler(404, page_not_found)


@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        prompt_question = request.form['prompt_question']

        res = {}
        res['answer'] = a.generateChatResponse(prompt_question)
        return jsonify(res), 200

    return render_template('index.html', **locals())

from app import app as application
app = application

