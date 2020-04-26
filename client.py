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
    print(url)
    sender  = imagezmq.ImageSender(connect_to=url,REQ_REP = True)
else:
    sender  = imagezmq.ImageSender(connect_to=f'tcp://{args["url"]}:{args["port"]}', REQ_REP = True)
source  = args["source"]
id      = args["id"]
name    = args["name"]
calibrate = "OK"



a_thermal = 0.0459
b_thermal = - 321

a_vis = (255/24)
b_vis = -16 * (255/24)

parameter_calibrate = False

if source != "None":
    if source == "pi":
        vs = VideoStream(usePiCamera=True).start()
    else:
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
    data2 = {"id" : id, "name": name, "type":"secondary", "process" :args["analitic"]}

    frame2 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    
    if calibrate != "OK":
        print(calibrate)
        H,W = frame2.shape
        respon_hub = calibrate.split("#")
        n = int(respon_hub[1])
        if n != 0:
            h_step = H // n
            h_0 = (H // n) // 2
            w_step = W // n
            w_0 = (W // n) // 2
            data_val = []
            for i in range(n):
                # data_val.append([])
                for j in range(n):
                    x = w_0 + w_step * j
                    y = h_0 + h_step * i
                    val = float(frame2[y,x])
                    data_val.append(val)

            data2["value"] = data_val

        if len(respon_hub) == 6:
            a_thermal = float(respon_hub[0])
            b_thermal = float(respon_hub[1])

            a_vis = float(respon_hub[2])
            b_vis = float(respon_hub[3])

    frame2 = cv2.applyColorMap(frame2, cv2.COLORMAP_JET)
    
    
    if frame1 is not None:
        respon = (sender.send_image_reqrep(data1, frame1))
        respon2 = (sender.send_image_reqrep(data2, frame2))
        calibrate = respon2.decode("utf-8")
    time.sleep(0.05)
vs.stop()