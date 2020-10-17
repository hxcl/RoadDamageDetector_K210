#!/usr/bin/env python3
# coding:utf-8
import socket
import time
import threading
import datetime
import pygame
import json
from detect import detect
import os,math
from pygame.locals import QUIT, KEYDOWN, K_f, K_F11, FULLSCREEN

damagetype={"D00":"裂缝","D01":"裂缝","D10":"裂缝","D11":"裂缝","D20":"大面积开裂","D40":"坑洼","D43":"标线模糊","D44":"标线模糊"}

def wgs84togcj02(lng, lat):
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return mglng, mglat

def transformlat(lng, lat):
    PI = 3.1415926535897932384626
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * \
          lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret

def transformlng(lng, lat):
    PI = 3.1415926535897932384626
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


local_ip = ""
local_port = 3456
width = 320
height = 240

# jpeg 20 fps
# esp32 spi dma temp buffer MAX Len: 4k


def receiveThread(conn):
    conn.settimeout(10)
    conn_end = False
    pack_size = 1024*5
    while True:
        if conn_end:
            break
        img = b""
        tmp = b''
        while True:
            try:
                client_data = conn.recv(1)
            except socket.timeout:
                conn_end = True
                break
            if tmp == b'\xFF' and client_data == b'\xD8':
                img = b'\xFF\xD8'
                break
            tmp = client_data
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

        jsn_start = img.index(b'\x0D\x0D\x0D\x0D', 2000)

        jsn = img[jsn_start+4:]

        img = img[:jsn_start]

        if not img.startswith(b'\xFF\xD8') or not img.endswith(b'\xFF\xD9'):
            print("image error")
            continue
        f = open("tmp.jpg", "wb")
        f.write(img)
        f.close()

        #detect("/home/todd/github/road_condition_web/tmp.jpg","data.jpg")

        jsn = jsn.decode("ASCII")
        print(json.loads(jsn)[0])

        lat=json.loads(jsn)[0]['latitude'].split(' ')
        lat=float(lat[0])+float(lat[1])/60.0
        lng=json.loads(jsn)[0]['longtitude'].split(' ')
        lng=float(lng[0])+float(lng[1])/60.0
        lng,lat=wgs84togcj02(lng,lat)
        classes=json.loads(jsn)[0]['classes']
        condition=""
        for damage in classes:
            condition+=(damagetype[damage]+'/')
        time=str(datetime.datetime.now())
        time=time[0:4]+time[5:7]+time[8:10]+time[11:13]+time[14:16]+time[17:19]+time[20:22]
        newline=",\n{"+ \
                "\"lng\": "+str(lng)+","+ \
                "\"lat\": "+str(lat)+","+ \
                "\"time\": "+time+","+ \
                "\"condition\": \""+condition+"\""+ \
                "}\n];"
        print(newline)
        newline=newline.encode('utf-8')

        with open("/home/todd/github/road_condition_web/road_condition_web/static/data/earthquake.js","rb+") as earthquake:
            earthquake.seek(-3,2)
            earthquake.write(newline)
            earthquake.close()

        command="cp "+" /home/todd/github/road_condition_web/tmp.jpg "+ \
            "/home/todd/github/road_condition_web/road_condition_web/static/data/"+ \
                time+"_"+str(lng)+"_"+str(lat)+".jpg"
        os.popen(command).readlines()

        try:
            surface = pygame.image.load("tmp.jpg").convert()
            screen.blit(surface, (0, 0))
            pygame.display.update()
            print("recieve ok")
        except Exception as e:
            print(e)
    conn.close()
    print("receive thread end")


pygame.init()
screen = pygame.display.set_mode((width, height), 0, 32)
pygame.display.set_caption("pic from client")

ip_port = (local_ip, local_port)
sk = socket.socket()
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind(ip_port)
sk.listen(50)
print("accept now,wait for client")


def server():
    while True:
        conn, addr = sk.accept()
        print("hello client,ip:")
        print(addr)
        t = threading.Thread(target=receiveThread, args=(conn,))
        t.setDaemon(True)
        t.start()


tmp = threading.Thread(target=server, args=())
tmp.setDaemon(True)
tmp.start()

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
