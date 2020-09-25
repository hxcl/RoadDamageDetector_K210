# 作为上位机接收客户机发送的图片和分类数据，视后期业务逻辑送往数据库/服务器二次鉴别

# 图片信息：使用 json 字符串存储图片的文件名、经纬度、时间等信息
# 图片名初步计划使用 拍摄时间-序号组成。如 2020-0920-08:00:00-5.jpg 代表 20200920 八点整拍摄的第五张照片 
# json 格式初定如下
# {
#     'client_num': ,
#     'latitude': ,
#     'longtitude': ,
#     'date': ,
#     'UTC_time': ,
#     'pic_name': 
# }

# 使用 socket 发送时，先发送图片信息，再是图片本身

import socket, threading, json

def link_handler(link, client):
    """
    
    """

    print("Sever start receiving the requeset from [%s:%s]" % (client[0], client[1]))

    while True:
        client_data = link.recv(1024).decode()
        if client_data = "exit":
            print("stop communication with [%s:%s]" % (client[0], client[1]))
        
        link.close()

ip_port = (192.168.1.225, 3456)
socket1 = socket.socket()
socket1.bind(ip_port)
socket1.listen(5)

while True:
    conn, address = socket1.accept()
    t = threading.Thread(target=link_handler, args=(conn,address))
    t.start()