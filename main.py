import os
import cv2 as cv
import requests
from config import *
from util import *


@timer
def parse_images(deep) -> None:
    if not 1 <= deep <= 7:
        print('[ERROR] deep in out of range')
        return
    for y in range(pow(2, deep - 1)):
        for x in range(pow(2, deep - 1)):
            check = True
            while check:
                global ya_weather_map_token
                url = f'{base_url}/{ya_weather_map_token}/{deep}/{x}_{y}.jpeg'
                data = requests.get(url, headers=headers, stream=True)

                if not os.path.exists(f'./tmp/{deep}'):
                    os.makedirs(f'./tmp/{deep}')

                if data.status_code == 200:
                    print(f'[OK] GET {x} {y}')
                    file = open(f'./tmp/{deep}/{x}-{y}.png', 'wb')
                    file.write(data.content)
                    file.close()
                    check = False
                else:
                    print(f'[ERROR] {x} {y} not found. Search new token ...')
                    ya_weather_map_token = extract_token(chrome_dev_tools_network(ya_weather_map_url))
                    print(f'[INFO] New token - {ya_weather_map_token}')
                    check = True


@timer
def merge_images(deep) -> None:
    h = []
    for x in range(pow(2, deep - 1)):
        v = []
        for y in range(pow(2, deep - 1)):
            v.append(cv.imread(f'./tmp/{deep}/{x}-{y}.png'))
        merge_v = cv.vconcat(v)
        h.append(merge_v)
    merge_h = cv.hconcat(h)
    cv.imwrite(f'./merge-{deep}.png', merge_h)


if __name__ == "__main__":
    deep = 2
    parse_images(deep)
    merge_images(deep)