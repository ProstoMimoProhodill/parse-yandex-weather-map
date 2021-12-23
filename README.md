# Парсер карты яндекс погоды
![This is an image](./merge-4.png)

Класс - WeatherMap()  
Доступные методы:  
Температура - get_temperature_map(deep, border, grid)  
Давление - get_pressure_map(deep, border, grid)  
Скорость ветра - get_wind_map(deep, border, grid)  
Методы возвращают путь к построенному изображению  

deep - точность (int от 1 до 7)  
border - границы стран (bool, по умолчанию True)  
grid - сетка элементов, из которых построена карта (bool, по умолчанию True)  

Для работы скрипта необходимо в config.py прописать путь до webdriver.exe (драйвер текущей версии браузера для работы Selenium)

Стоит отметить, что при выставлении deep = 7, может не хватить пропускной способоности интернета, поэтому желательно выставлять меньшую точность  

Используемые библиотеки:  
matplotlib  
selenium  
opencv  
numpy  



