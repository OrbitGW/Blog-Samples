import requests
import re
import json
from tkinter import *
from PIL import Image,ImageTk
from threading import Thread
from queue import Queue
import time

exit_code = Queue(1)
data = Queue(1)

def u2cc(str):    #Unicode to Chinese Character
    return json.loads('"%s"' %str)

def getData(city):
    url = "https://weathernew.pae.baidu.com/weathernew/pc"
    header = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"}
    query = city + "天气"
    param = {"query":query,"srcid":"4982"}
    response = requests.get(url,params=param,headers=header).text
    #get unicode data
    temperature_u = re.match( r"^.*\"temperature\":\"(.*?)\",", response).group(1) 
    weather_u = re.match( r"^.*\"weather\":\"(.*?)\",", response).group(1)
    wind_direction_u = re.match( r"^.*\"wind_direction\":\"(.*?)\",", response).group(1)
    wind_power_u = re.match( r"^.*\"wind_power\":\"(.*?)\",", response).group(1)
    return [u2cc(temperature_u),u2cc(weather_u),u2cc(wind_direction_u),u2cc(wind_power_u)]


def start_move(self, event):
    self.x = event.x
    self.y = event.y

def stop_move(self, event):
    self.x = None
    self.y = None

def do_move(self, event):
    deltax = event.x - self.x
    deltay = event.y - self.y
    x = self.winfo_x() + deltax
    y = self.winfo_y() + deltay
    self.geometry(f"+{x}+{y}")

def data_update_thread(exit_code,data):
    data.put(getData("重庆"))
    while(exit_code.empty()):
        time.sleep(120)#update once per 2 minutes
        data.empty()
        data.put(getData("重庆"))

class App():
    def __init__(self,exit_code,data):
        self.win = Tk()
        self.win.attributes("-topmost",1)

        self.x, self.y = 0, 0
        self.win_size = '200x150'

        self.win.overrideredirect(True)
        self.win.geometry(f"{self.win_size}")

        self.canvas = Canvas(width=200, height=150, highlightthickness=0, borderwidth=0)
        self.canvas.place(x=0, y=0)

        self.bg = PhotoImage(file = "./imgs/1.bg.gif")
        self.bg_id = self.canvas.create_image(0, 0, image=self.bg, anchor='nw')

        ls_data = data.get()

        self.txt_temperature_id=self.canvas.create_text(10,40, font=("Arial", 32),anchor="nw",fill="white")
        self.canvas.insert(self.txt_temperature_id,1,ls_data[0]+"℃")
        self.txt_weather_id=self.canvas.create_text(120,60, font=("Arial", 16),anchor="nw",fill="white")
        self.canvas.insert(self.txt_weather_id,1,ls_data[1])
        self.txt_wind_direction_id=self.canvas.create_text(10,110, font=("Arial", 16),anchor="nw",fill="white")
        self.canvas.insert(self.txt_wind_direction_id,1,ls_data[2])
        self.txt_wind_power_id=self.canvas.create_text(100,110, font=("Arial", 16),anchor="nw",fill="white")
        self.canvas.insert(self.txt_wind_power_id,1,ls_data[3])


        self.win.bind("<B1-Motion>", self.move)
        self.win.bind("<Button-1>", self.get_point)
        self.win.bind("<Double-Button-1>", self.close)

    def move(self, event):
        new_x = (event.x - self.x) + self.win.winfo_x()
        new_y = (event.y - self.y) + self.win.winfo_y()
        s = f"{self.win_size}+{new_x}+{new_y}"
        self.win.geometry(s)

    def get_point(self, event):
        self.x, self.y = event.x, event.y

    def run(self):
        self.win.mainloop()

    def close(self, event):
        self.win.destroy()
        exit_code.put("quit")

if __name__ == "__main__":
    dut = Thread(target=data_update_thread,args=(exit_code,data))
    dut.start()
    app = App(exit_code,data)
    app.run()
   