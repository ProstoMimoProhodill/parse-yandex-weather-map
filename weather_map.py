import os
import time

import cv2 as cv
import requests
import matplotlib.pyplot as plt
import numpy as np
from util import *
from multiprocessing.dummy import Pool as ThreadPool

# Данные с прогнозом
# https://api.weather.yandex.ru/frontend/nowcast/tile?x=18&y=8&z=5&for_date=1640089200&nowcast_gen_time=1640088438&request_id=1640088904958033-1129672350860912049-sas3-1002-e1c-sas-l7-balancer-8080-BAL&from_client=front&encoded=1


class WeatherMap:
    def get_temperature_map(self, deep=1, border=True, grid=True) -> str:
        self.__parse(deep, map_t='temperature', border=border)
        return self.__merge(deep, map_t='temperature', border=border, grid=grid)

    def get_pressure_map(self, deep=1, border=True, grid=True) -> str:
        self.__parse(deep, map_t='pressure', border=border)
        return self.__merge(deep, map_t='pressure', border=border, grid=grid)

    def get_wind_map(self, deep=1, border=True, grid=True) -> str:
        self.__parse(deep, map_t='wind', border=border)
        return self.__merge(deep, map_t='wind', border=border, grid=grid)

    def show_map(self, path) -> None:
        img = cv.imread(path)
        n_labels = 5

        # labels
        label_x = np.arange(-180, 180)
        label_y = np.arange(90, -90, -1)
        label_nx = label_x.shape[0]
        label_ny = label_y.shape[0]
        label_step_x = int(label_nx / (n_labels - 1))
        label_step_y = int(label_ny / (n_labels - 1))
        label_x_pos = label_x[::label_step_x]
        label_y_pos = label_y[::label_step_y]

        # image
        h, w, _ = img.shape
        x = np.arange(0, w)
        y = np.arange(0, h)
        nx = x.shape[0]
        ny = y.shape[0]
        step_x = int(nx / (n_labels - 1))
        step_y = int(ny / (n_labels - 1))
        x_pos = np.arange(0, nx, step_x)
        y_pos = np.arange(0, ny, step_y)

        plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
        plt.xticks(x_pos, label_x_pos)
        plt.yticks(y_pos, label_y_pos)

        def mouse_press(event):
            y = -((180 * event.ydata / h) - 90)
            x = (360 * event.xdata / w) - 180
            print(f'Coordinates y: {y} x: {x}')

        plt.connect('button_press_event', mouse_press)
        plt.show()

    @timer
    def __parse(self, deep=1, map_t='temperature', border=False) -> None:
        tasks = [map_t]

        if not 1 <= deep <= 7:
            print('[ERROR] deep in out of range')
            return

        if map_t not in map_type.keys():
            print('[ERROR] unknown map type')
            return

        if not os.path.exists(f'./tmp/{map_t}/{deep}'):
            os.makedirs(f'./tmp/{map_t}/{deep}')

        if border:
            tasks.append('border')
            if not os.path.exists(f'./tmp/border/{deep}'):
                os.makedirs(f'./tmp/border/{deep}')

        for task in tasks:
            check = True
            while check:
                if task == 'border':
                    if os.path.exists(f'./tmp/{task}/{deep}/0-0.png'):
                        return

                token = extract_token(map_type[task], chrome_dev_tools_network(url_type[task]))
                print(f'[INFO] Token ({task}) - {token}')

                urls = list()
                for y in range(pow(2, deep - 1)):
                    for x in range(pow(2, deep - 1)):
                        if task == 'border':
                            url = f'{base_url}/{map_type[task]}/{token}/{deep}/{x}_{y}.png'
                        else:
                            url = f'{base_url}/{map_type[task]}/{token}/{deep}/{x}_{y}.jpeg'
                        urls.append(url)

                x, y = 0, 0
                with ThreadPool(pow(4, deep - 1)) as pool:
                    responses = list(pool.map(requests.get, urls))
                for response in responses:
                    if response.status_code == 200:
                        file = open(f'./tmp/{task}/{deep}/{x}-{y}.png', 'wb')
                        file.write(response.content)
                        file.close()
                        check = False
                    else:
                        print(f'[ERROR] {x} {y} not found. Data is not exist')
                        return
                    x += 1
                    if x == pow(2, deep-1):
                        x = 0
                        y += 1

    @timer
    def __merge(self, deep=1, map_t='temperature', border=False, grid=False) -> str:
        if not os.path.exists(f'./tmp/{map_t}/{deep}/0-0.png'):
            print('[ERROR] Data is not exist')
            return

        merge_h_v = []
        tasks = [map_t]

        if border:
            tasks.append('border')

        for task in tasks:
            h = []
            for x in range(pow(2, deep - 1)):
                v = []
                for y in range(pow(2, deep - 1)):
                    v.append(cv.imread(f'./tmp/{task}/{deep}/{x}-{y}.png'))
                merge_v = cv.vconcat(v)
                h.append(merge_v)
            merge_h = cv.hconcat(h)
            merge_h_v.append(merge_h)

        id = "".join(list(map(str, time.localtime()[:6])))
        if border:
            path = f'./{id}-{map_t}-{deep}-b.png'
            overlay = cv.addWeighted(merge_h_v[0], 0.9, merge_h_v[1], 0.1, 0.1)
            if grid:
                for x in range(512, overlay.shape[1], 512):
                    img = cv.line(overlay, (x, 0), (x, overlay.shape[1]), (0, 0, 0), 5)
                for y in range(512, overlay.shape[0], 512):
                    img = cv.line(overlay, (0, y), (overlay.shape[0], y), (0, 0, 0), 5)
                overlay = img
                path = f'./{id}-{map_t}-{deep}-bg.png'
            cv.imwrite(path, overlay)
        else:
            path = f'./{map_t}-{deep}.png'
            if grid:
                for x in range(512,  merge_h_v[0].shape[1], 512):
                    img = cv.line(merge_h_v[0], (x, 0), (x,  merge_h_v[0].shape[1]), (0, 0, 0), 5)
                for y in range(512,  merge_h_v[0].shape[0], 512):
                    img = cv.line(merge_h_v[0], (0, y), (merge_h_v[0].shape[0], y), (0, 0, 0), 5)
                merge_h_v[0] = img
                path = f'./{id}-{map_t}-{deep}-g.png'
            cv.imwrite(path, merge_h_v[0])
        return path
