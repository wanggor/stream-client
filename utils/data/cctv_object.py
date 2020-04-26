from collections import OrderedDict
from datetime import datetime, timedelta
import time
import cv2

class Cctv():
    def __init__(self, id, name, image_path = "static/images/camera-not-connected.png", max_iddle = 5):
        self.id                     = str(id)
        self.name                   = str(name)
        self.created                = time.time()
        self.last_update            = time.time()
        self.image_not_connected    = cv2.imread(image_path)
        self.image                  = cv2.imread(image_path)
        self.max_iddle              = max_iddle # second
        self.status                 = f"START | {self.name} | Creating new CCTV"

    def get(self):
        return {"id" : str(self.id),"name" : self.name}
    
    def update_image(self, image = None):
        t = time.time()
        if image is None:
            sec = timedelta(seconds= (t -  self.last_update))
            del_t = str(sec)
            if t -  self.last_update > self.max_iddle :
                self.image      = self.image_not_connected.copy()
                self.status     = f"STOP | {self.name} | CCTV not connected from  "+ del_t
            else:
                self.status     = f"IDDLE | {self.name} | CCTV waiting data from  "+ del_t
        else:
            self.image  = image
            self.last_update  = time.time()
            self.status     = f"RUNNING | {self.name} | CCTV is running"

    def get_id(self):
        return str(self.id)

    def get_status(self):
        return self.status
    def get_image(self):
        return self.image

class Cctv_list():
    def __init__(self, number = 0, prefix = "CCTV"):
        self.prefix = prefix
        self.cctv = { str(i) : Cctv(str(i),prefix + f" {i+1}") for i in range(number)}
        self.cctv = OrderedDict(self.cctv)
    
    def get(self):
        return [ self.cctv[str(i)].get() for i in self.cctv]
    
    def update_cctv(self,id = None,  name= None):
        if name is None:
            index = len(self.cctv)
            name = self.prefix  + f" {index+1}"
        if id is None:
            index = len(self.cctv)
        else:
            index = id
        index = str(index)
        self.cctv[index] = Cctv(index,name)
        return self.cctv[index].get()
    
    def update_image(self, data = {}):
        for id in data:
            if str(id) not in self.cctv:
                self.update_cctv(id = id)
        for i in self.cctv:
            ind = self.cctv[i].get_id()
            if ind in data.keys():  
                self.cctv[i].update_image(data[ind])
            else:
                self.cctv[i].update_image()
    def get_status(self, ind= None):
        if ind is not None:
            return [ {"info" :self.cctv[ind].get(), "status" : self.cctv[ind].get_status()}]
        else:
            return [ {"info" :self.cctv[i].get(), "status" : self.cctv[i].get_status()}  for i in self.cctv]

    def get_image(self, ind= None):
        if ind is not None:
            return [ {"info" :self.cctv[ind].get(), "image" : self.cctv[ind].get_image()}]
        else:
            return [ {"info" :self.cctv[i].get(), "image" : self.cctv[i].get_image()}  for i in self.cctv]
    
    def check_id(self, id):
        return str(id) in self.cctv.keys()
        
    def __repr__(self):
        text = ""
        for i in self.cctv:
            text += (self.cctv[i].get_status()) + "\n"
        text += "\n"
        return text

if __name__ == "__main__":
    cctv_list = Cctv_list(10)
    print(cctv_list.get())
    
    cctv_list.update_cctv()
    print(cctv_list.get())
    
    cctv_list.update_cctv("mycctv")
    print(cctv_list.get())
    
        