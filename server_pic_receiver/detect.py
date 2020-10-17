import os

def detect(img_path, save_path="predition.jpg"):
    """
    detect image from img_path, and save the result in save_path,
    and return the result tuple
    """
    output=[]
    command="cd /home/todd/github/darknet && ./darknet detect cfg/yolo-fastest.cfg backup/yolo-fastest_8000.weights " \
            +img_path+" -ext_output "+save_path+" -dont_show"+" -thresh 0.05"
    result = os.popen(command).readlines()
    for i in result:
        if i[0][0]=='D':
            output.append(i)
    return output



#print(detect("/home/todd/github/darknet/test.jpg","data.jpg"))