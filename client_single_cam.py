import os
import cv2
import time
import numpy as np
import random
import argparse
import imagezmq.imagezmq as imagezmq
from imutils.video import VideoStream, FileVideoStream

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", type=str,
    help="name of CCTV", default="1")
ap.add_argument("-s", "--source", type=str,
    help="name source", default="None")
ap.add_argument("-n", "--name", type=str,
    help="name tempat", default="My CCTV")
ap.add_argument("-u", "--url", type=str, 
    help="height of image output", default="None")
ap.add_argument("-p", "--port", type=str, 
    help="height of image output", default="5555")
ap.add_argument("-a", "--analitic", type=str, 
    help="image processing", default="true")

args = vars(ap.parse_args())

time.sleep(3.0)
if args["url"] == "None":
    host = os.environ.get('HOST_SERVER')
    url = f'tcp://{host}:{args["port"]}'
    sender  = imagezmq.ImageSender(connect_to=url,REQ_REP = True)
else:
    sender  = imagezmq.ImageSender(connect_to=f'tcp://{args["url"]}:{args["port"]}', REQ_REP = True)
source  = args["source"]
id      = args["id"]
name    = args["name"]
calibrate = "OK"

if source != "None":
    vs = VideoStream(int(source)).start()
else:
    vs = None
time.sleep(2.0)

while True:
    if vs is not None:
        frame1 = vs.read()
    else:
        frame1 = np.ones((480,640,3), np.uint8) * random.randint(1,255)

    data1 = {"id" : id, "name": name, "type":"primary", "process" :args["analitic"]}
    
    if frame1 is not None:
        respon = (sender.send_image_reqrep(data1, frame1))
    time.sleep(0.05)
vs.stop()