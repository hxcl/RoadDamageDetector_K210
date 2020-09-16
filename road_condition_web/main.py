from flask import Flask,render_template,request
import os,base64

app = Flask(__name__)


# 默认路由
@app.route('/')  # 路由默认使用GET方式进行路径访问，可以配置成methods=['GET', 'POST']等
def index():
    return render_template('base.html')


@app.route('/showPicture', methods=['POST', 'GET'])
def picture():
    # if request.method == "POST":
    #     # 发送图片
    #     img = open("static/data/eg_tulip.jpg", 'rb')  # 读取图片文件
    #     data = base64.b64encode(img.read()).decode()  # 进行base64编码
    #     html = '''<img src="data:image/jpg;base64,{}" style="width:100%;height:100%;"/>'''  # html代码
    #     htmlstr = html.format(data)  # 添加数据
    #     return htmlstr
    pass


@app.route('/receivePicture', methods=["GET", "POST"])
def receivePicture():
    pass


if __name__ == "__main__":
    app.run(debug=True)
