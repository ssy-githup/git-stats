import requests


if __name__ == '__main__':

    url_city = "https://www.amap.com/service/cityList?version=202092419"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }

    city = []
    response = requests.get(url=url_city, headers=headers)
    content = response.json()
    print(content)


