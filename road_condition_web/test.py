import json
import execjs
with open('./static/data/earthquake.js', 'r', encoding='utf-8') as f:
    a=f.read()
print(a[17:len(a)-1])
