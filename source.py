import rtsp
import time
import requests as rq
import keyboard
import configparser
import cv2
import math
import operator
from PIL import ImageChops
import functools

# метод сравнения кадров
def compare(image1, image2):
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(functools.reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    return rms

# __не используется__
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None


# получает настройки веб контроллера для vMix из файла Srttings.ini
def GetConfig():
    try:
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        web_address = config.get("Settings", 'web_adress') # адрес контроллера
        input_number = config.get("Settings", 'presentation_input_number') # номер потока презентации в vMix
        presentation_ip = config.get("Settings",'presentation_rtsp_link') # ip презентационного потока
    except:
        web_address = 'http://192.168.100.16:5000'
        input_number = '1'
        presentation_ip = 'rtsp://172.18.200.27/0'
    return web_address, input_number, presentation_ip


#Detecting presentation change
def Presentation_Detect(web_addr, input_num, pr_ip):
    presentation_address = web_addr + '/api/?Function=Cut&Input=' + input_num # api адресс для переключения презентации в эфир
    return_to_address = web_addr + '/api/?Function=Cut&Input=0' # api адресс для переключения обратно в эфир потока на превью
    client = rtsp.Client(rtsp_server_uri=pr_ip) # начало работы с RTSP потоком презентации для сравнения кадров и отслеживания переключения
    image = client.read()
    while not keyboard.is_pressed('shift+q'): # _____необходимо переделать выход из цикла_____
        t0 = time.time() # технические выкладки 
        image1 = client.read() # технические выкладки 
        print(compare(image, image1)) # технические выкладки 
        t1 = time.time() # технические выкладки 
        print(t1-t0) # технические выкладки 
        k = compare(image, image) # коэффициент "изменения" кадра (______надо доработать______)

        if compare(image, image1) > k:
            image = client.read()
            print(rq.get(presentation_address)) # переключение на презентацию и вывод ответа
            time.sleep(5)
            print(rq.get(return_to_address)) # переключение на превью и вывод ответа
            '''
            1xx Informational – the request was received, continuing process
            ___2xx Successful – the request was successfully received, understood and accepted
            3xx Redirection – further action needs to be taken in order to complete the request
            ___4xx Client Error – the request contains bad syntax or cannot be fulfilled
            5xx Server Error – the server failed to fulfill an apparently valid request
            '''


def main():
    a, b, c = GetConfig()
    # print(a,b,c)
    Presentation_Detect(a, b, c)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
