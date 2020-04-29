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
    help="CCTV ID", default="1")
ap.add_argument("-s", "--source", type=str,
    help="Video source", default="0")
ap.add_argument("-n", "--name", type=str,
    help="CCTV name", default="My CCTV")
ap.add_argument("-u", "--url", type=str, 
    help="Host server", default="None")
ap.add_argument("-p", "--port", type=str, 
    help="Port server", default="5555")
ap.add_argument("-a", "--analitic", type=str, 
    help="Image processing", default="true")
ap.add_argument("-H", "--height", type=int, 
    help="Height image", default=480)
ap.add_argument("-W", "--width", type=int, 
    help="Width image", default=640)
ap.add_argument("-t", "--type", type=str, 
    help="Type of client", default="single")
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
type_cam    = args["type"]
calibrate = "OK"

process_opsi = ["rgb", "hsv", "grey"]
opsi_active = "rgb"

if source != "None":
    if source == "pi":
        vs = VideoStream(usePiCamera=True).start()
    else:
        if source.isnumeric():
            vs = VideoStream(int(source)).start()
        else:
            vs = VideoStream(source).start()
time.sleep(2.0)

while True:
    if vs is not None:
        frame1 = vs.read()
    else:
        frame1 = np.ones((480,640,3), np.uint8) * random.randint(1,255)
    frame1 = cv2.resize(frame1,(args["width"], args["height"]))

    if opsi_active == "hsv":
        frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    if opsi_active == "grey":
        frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    
    data1 = {"id" : id, "name": name, "type":"primary", "process" :args["analitic"], "type_cam" : type_cam, "process_opsi" : process_opsi, "opsi_active":opsi_active}

    
    if frame1 is not None:
        respon = (sender.send_image_reqrep(data1, frame1)).decode("utf-8").split("|")
        if len(respon) > 1:
            opsi_active = respon[1].split("#")[1]
        
vs.stop()