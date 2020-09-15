from flask import Flask, render_template, request
import os, h5py, pickle, re


app = Flask(__name__)


# 默认路由
@app.route('/')  # 路由默认使用GET方式进行路径访问，可以配置成methods=['GET', 'POST']等
def index():
    return render_template('index.html')


# 初始化路由
@app.route('/initialization')
def initialization():
    pass


@app.route('/dataPreprocess', methods=['POST'])
def message():
    pass


@app.route('/get', methods=["GET"])
def get():
    pass


if __name__ == "__main__":
    app.run(debug=True)
