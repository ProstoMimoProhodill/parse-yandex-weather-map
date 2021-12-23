from weather_map import *

if __name__ == "__main__":
    wmap = WeatherMap()
    wmap.get_temperature_map(3, grid=False)
    wmap.get_pressure_map(3, grid=False)
    wmap.get_wind_map(3, grid=False)

