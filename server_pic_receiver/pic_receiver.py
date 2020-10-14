import socket, threading, json, pymysql, pygame

def link_handler(link, client):
    conn.settimeout(10)
    conn_end = False
    pack_size = 1024*5
    while True:
        if conn_end:
            break
        img = b""
        jsn = b""
        tmp = b''

        isJson = False
        isImage = False

        while True:
            try:
                client_data = conn.recv(1)
            except socket.timeout:
                conn_end = True
                break
            # JPEG 文件头
            if tmp == b'\xFF' and client_data == b'\xD8':
                img = b'\xFF\xD8'
                isImage = True
                break
            # 自定义的 JSON 字符串开始标识
            elif tmp == b'\x0D' and client_data == b'\x0D':
                isJson = True
                break
            
            tmp = client_data
        
            if isImage == True:    
                while True:
                    try:
                        client_data = conn.recv(4096)
                    except socket.timeout:
                        client_data = None
                        conn_end = True
                    if not client_data:
                        break
                    # print("received data,len:",len(client_data) )
                    img += client_data
                    if img[-2:] == b'\xFF\xD9':
                        break
                    if len(client_data) > pack_size:
                        break
                print("recive end, pic len:", len(img))

                if not img.startswith(b'\xFF\xD8') or not img.endswith(b'\xFF\xD9'):
                    print("image error")
                    continue
                f = open("tmp.jpg", "wb")
                f.write(img)
                f.close()
                
                isImage = False
            
            elif isJson == True:

                try:
                    client_data = conn.recv(512)
                except socket.timeout:
                    client_data = None
                    conn_end = True
                if not client_data:
                    continue
                # print("received data,len:",len(client_data) )
                img += client_data
                if jsn[-2:] != b'\x0D\x0D':
                    print("json format error")
                
                print("recive end, json len:", len(img))

                try:
                    jsn = jsn.decode("ASCII")
                except UnicodeError:
                    print("json decode ASCII error")

                # 去除 json 字符串末尾的两个换行符
                jsn = jsn[:-2]

                dic = json.loads(jsn)

                print(dic)

                isJson = False
                
    conn.close()
    print("receive thread end")

ip_port = ('192.168.1.225', '3456')
socket1 = socket.socket()
socket1.bind(ip_port)
socket1.listen(5)


while True:
    conn, address = socket1.accept()
    t = threading.Thread(target=link_handler, args=(conn,address))
    t.start()