earthquake=open("/home/todd/github/road_condition_web/road_condition_web/static/data/earthquake.js","rb+")
earthquake.seek(-3,2)
earthquake.write(b",\n{}\n];")
earthquake.close()