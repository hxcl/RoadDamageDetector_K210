from flask import Flask,render_template,request,jsonify
import os,base64
from database import get_db_conn, close_db_conn

db_file = './roaddata.db'

app = Flask(__name__)


# 默认路由
@app.route('/')  # 路由默认使用GET方式进行路径访问，可以配置成methods=['GET', 'POST']等
def index():
    return render_template('base.html')


@app.route('/showPicture', methods=['POST', 'GET'])
def picture():
    with open('./static/data/earthquake.js', 'r', encoding='utf-8') as f:
        content = f.read()
    earthQuake = content[17:len(content)-1]
    return earthQuake


@app.route('/receivePicture', methods=["GET", "POST"])
def receivePicture():
    pass


if __name__ == "__main__":
    app.run(debug=True)

