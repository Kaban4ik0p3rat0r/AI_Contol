import rtsp as r
import time
import requests as rq
import keyboard
import configparser
import cv2
import numpy as np



#Getting ur VMix Web Controller IP from config
def GetConfig():
    try:
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        web_address = config.get("Settings", 'web_adress')
        input_number = config.get("Settings", 'presentation_input_number')
        presentation_ip = config.get("Settings",'presentation_rtsp_link')
    except:
        web_address = 'http://192.168.100.16:5000'
        input_number = '1'
        presentation_ip = 'rtsp://172.18.200.27/0'
    return web_address, input_number, presentation_ip
#Detecting presentation change
def Presentation_Detect(web_addr, input_num, pr_ip):
    presentation_address = web_addr + '/api/?Function=Cut&Input=' + input_num
    return_to_address = web_addr + '/api/?Function=Cut&Input=0'
    video_cap = cv2.VideoCapture(pr_ip)
    ret,frame = video_cap.read()
    while 1:
        ret1,frame1 = video_cap.read()
        if np.any(frame != frame1):
            print(rq.get(presentation_address))
            time.sleep(5)
            print(rq.get(return_to_address))
            ret,frame = video_cap.read()
        if keyboard.is_pressed('shift + s'):
            video_cap.release()
            break
def main():
    a,b,c = GetConfig()
    #print(a,b,c)
    Presentation_Detect(a,b,c)
if __name__ == '__main__':
    main()
