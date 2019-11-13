import rtsp
import time
import requests as rq
import configparser
import cv2
import threading
import random
from PIL import Image
from PIL import ImageChops


# получает настройки веб контроллера для vMix из файла Settings.ini
def GetConfig():
    try:
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        web_address = config.get("Settings", 'web_adress')  # адрес контроллера
        input_number = config.get("Settings", 'presentation_input_number')  # номер потока презентации в vMix
        presentation_ip = config.get("Settings", 'presentation_rtsp_link')  # ip презентационного потока
    except:
        web_address = 'http://192.168.100.16:5000'
        input_number = '1'
        presentation_ip = 'rtsp://172.18.200.27/0'
    return web_address, input_number, presentation_ip


#Detecting presentation change
def Presentation_Detect(web_addr, input_num, pr_ip):
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
    presentation_address = web_addr + '/api/?Function=Cut&Input=' + input_num  # api адресс для переключения презентации в эфир
    return_to_address = web_addr + '/api/?Function=Cut&Input=0'  # api адресс для переключения обратно в эфир потока на превью
    client = rtsp.Client(rtsp_server_uri=pr_ip)  # начало работы с RTSP потоком презентации для сравнения кадров и отслеживания переключения
    image = client.read()
    image.save(open('IMG_Compare\First.bmp', 'wb'))  # сохранение "начлаьного" кадра в каталог IMG_Compare
    random.seed()
    im = Image.open('IMG_Compare\First.bmp')
    i = 0
    while 1:
        time_crowd = random.randint(5, 15)  # время кадра на экране для аудитории
        time_speaker = random.randint(15, 35)  # время кадра на экране для докладчика
        image1 = client.read()
        t1 = time.time()
        image1.save(open('IMG_Compare\Second.bmp', 'wb'))  # сохранение текущего кадра в каталог IMG_Compare
        im1 = Image.open('IMG_Compare\Second.bmp')
        image_d = ImageChops.difference(im, im1)
        image_d.save(open('IMG_Compare\Diff.bmp', 'wb'))  # разница "начального" и текущего кадров
        print(image_d.getpalette())  # попытка получить палитру для .jpg (__у меня постоянно выводит None__)

        image_d2 = image_d.convert("P", palette=Image.ADAPTIVE, colors=256)  # первый параметр по умолчанию = RGB
        # при использовании convert("RGB", palette=Image.ADAPTIVE, colors=256) палитра не добавляется
        print(image_d2.getpalette())
        image_d2.save(open('IMG_Compare\Diff_1.bmp', 'wb'))

        print(time.time() - t1)  # время обработки

        if not image_d2.getpalette().count(0) == len(image_d2.getpalette()):  # сравнение количества нулей (не измененных элементов) и длины палитры
            im = Image.open('IMG_Compare\Second.bmp')  # обновление "начального" кадра
            print('Переключение на презентацию ', rq.get(url=presentation_address))  # переключение на презентацию и вывод ответа
            time.sleep(5)  # время презентации в эфире
            print('Переключение с презентации ', rq.get(url=return_to_address))  # переключение на превью и вывод ответа
        else:
            change_to = web_addr + '/api/?Function=Cut&Input=' + number[i]  # выбор камеры на которую переключиться
            print('Переключение между камерами ', rq.get(url=change_to))
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
