# encoding: utf-8

import requests


url_city = "https://www.amap.com/service/cityList?version=202092419"
url_weather = "https://www.amap.com/service/weather?adcode={}"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
}


def get_city():
    """查询所有城市名称和编号"""
    city = []
    response = requests.get(url=url_city, headers=headers)
    content = response.json()

    if "data" in content:
        cityByLetter = content["data"]["cityByLetter"]
        for k, v in cityByLetter.items():
            city.extend(v)
    return city


def get_weather(adcode, name):
    """根据编号查询天气"""
    item = {}
    item["adcode"] = str(adcode)
    item["name"] = name

    response = requests.get(url=url_weather.format(adcode), headers=headers)
    content = response.json()
    item["weather_name"] = content["data"]["data"][0]["forecast_data"][0]["weather_name"]
    item["min_temp"] = content["data"]["data"][0]["forecast_data"][0]["min_temp"]
    item["max_temp"] = content["data"]["data"][0]["forecast_data"][0]["max_temp"]

    return item


def save(item):
    """保存"""
    print(item)
    with open("./weather.txt","a",encoding="utf-8") as file:
        file.write(",".join(item.values()))
        file.write("\n")


if __name__ == '__main__':
    city_list = get_city()
    for city in city_list:
        item = get_weather(city["adcode"],city["name"])
        save(item)
