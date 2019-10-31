import rtsp
import time
import requests as rq
import configparser
import cv2
import math
import operator
import functools
import threading
import random

# метод сравнения кадров
def compare(image1, image2):
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(functools.reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    return rms


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
    random.seed()
    # Настройки vMix таковы:
    # 1: презентация
    # 2: rtsp://172.18.200.51:554/Streaming/Channels/1
    # 3: rtsp://172.18.200.52:554/Streaming/Channels/1
    # 4: rtsp://172.18.200.53:554/Streaming/Channels/1
    # 5: rtsp://172.18.200.54:554/Streaming/Channels/1
    # 6: rtsp://172.18.200.55:554/Streaming/Channels/1
    # 7: rtsp://172.18.200.56:554/Streaming/Channels/1
    # В списке numbers - номера потоков камер в vMix.
    # Переключение происходит именно в таком порядке. Закольцованно.
    number = ['2', '7', '4', '3', '6', '5']
    i = 0
    while 1:
        time_crowd = random.randint(5, 15) # время кадра на экране для аудитории
        time_speaker = random.randint(15, 35) # время кадра на экране для докладчика
        image1 = client.read()
        print(compare(image, image1))
        k = compare(image, image) # коэффициент "изменения" кадра (______надо доработать______)
        if compare(image, image1) > k:
            image = client.read()
            print(rq.get(presentation_address)) # переключение на презентацию и вывод ответа
            time.sleep(5)
            print(rq.get(return_to_address)) # переключение на превью и вывод ответа
        else:
            change_to = web_addr + '/api/?Function=Cut&Input=' + number[i] # 
            print('Переключение камер ', rq.get(url=change_to))
            if (i % 2) == 0:
                time.sleep(time_crowd)
            else:
                time.sleep(time_speaker)
            i = i + 1
            if i == 6:
                i = 0
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
    # Presentation_Detect(a, b, c)
    threading.Thread(target=Presentation_Detect, args=[a, b, c], daemon=True).start()
    input('Press <Enter> to exit.\n')
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
