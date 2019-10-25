import cv2
import math, operator
import sys
from PIL import Image
from PIL import ImageChops
import functools

def compare(image1,image2):
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(functools.reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    return rms

def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None

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
    #video_cap = cv2.VideoCapture(pr_ip)
    #ret,frame = video_cap.read()
    client = rtsp.Client(rtsp_server_uri=pr_ip)
    image = client.read()
    while 1:
        image1 = client.read()
        print(compare(image,image1))
        if equal(image1, image):
            image = client.read()
            print(rq.get(presentation_address))
            time.sleep(5)
            print(rq.get(return_to_address))
        if keyboard.is_pressed('q'):
            break
        #video_cap.release()

def main():
    a,b,c = GetConfig()
    #print(a,b,c)
    Presentation_Detect(a,b,c)
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()
