import os
import cv2 as cv
import requests
from util import *
from multiprocessing.dummy import Pool as ThreadPool

# Данные с прогнозом
# https://api.weather.yandex.ru/frontend/nowcast/tile?x=18&y=8&z=5&for_date=1640089200&nowcast_gen_time=1640088438&request_id=1640088904958033-1129672350860912049-sas3-1002-e1c-sas-l7-balancer-8080-BAL&from_client=front&encoded=1


@timer
def parse(deep=1, map_t='temperature', border=False) -> None:
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
def merge(deep=1, map_t='temperature', border=False) -> None:
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

    if border:
        overlay = cv.addWeighted(merge_h_v[0], 0.9, merge_h_v[1], 0.1, 0.1)
        cv.imwrite(f'./{map_t}-{deep}-border.png', overlay)
    else:
        cv.imwrite(f'./{map_t}-{deep}.png', merge_h_v[0])


if __name__ == "__main__":
    deep = 4
    parse(deep, map_t='wind', border=True)
    merge(deep, map_t='wind', border=True)
