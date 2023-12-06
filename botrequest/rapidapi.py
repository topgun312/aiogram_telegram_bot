import json
import os
from typing import Dict, List, Union
import aiohttp
from loguru import logger
from config_data.config_reader import config


headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.rapid_api_key.get_secret_value(),
    "X-RapidAPI-Host": config.rapid_api_host.get_secret_value(),
}


@logger.catch
async def request_func(method_endswith: str, qstring: Dict[str, str]):
    """
    Универсальная функция для всех get-запросов и post-запросов к Hotels API.
    :param url: url-ссылка для поиска.
    :param qstring: словарь с заданными парамеирами поиска.
    :return: результат get-запросов.
    """
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    try:
        async with aiohttp.ClientSession() as session:
            if method_endswith == "locations/v3/search":
                async with session.get(
                    url, headers=headers, params=qstring, timeout=10
                ) as response:
                    return await response.text()
            else:
                async with session.post(
                    url, headers=headers, json=qstring, timeout=10
                ) as response:
                    return await response.text()
    except Exception:
        logger.exception(Exception)
        return False


async def search_location(message: str) -> Union[List[Dict[str, str]], bool]:
    """
    Выполнение HTTP-запроса к Hotels API (rapidapi.com) (Поиск локаций (городов)).
    :param message: сообщение от пользователя
    :return: список словарей, содержащих сведения локаций (городов)
    """
    method_endswith = "locations/v3/search"
    querystring = {
        "q": message,
        "locale": "ru_RU",
        "langid": "1033",
        "siteid": "300000001",
    }
    try:
        response = await request_func(method_endswith, querystring)
        result = json.loads(response)
        cities = list()
        for city in result["sr"]:
            city_name = (
                city["regionNames"]["fullName"].split(",")[0]
                + ", "
                + city["regionNames"]["fullName"].split(",")[-1]
            )
            destination_id = city["essId"]["sourceId"]
            cities.append({"city_name": city_name, "destination_id": destination_id})
        return cities
    except Exception:
        logger.exception(Exception)
        return False


async def search_hotels(data: Dict[str, str]) -> Union[Dict[str, int], bool]:
    """
    HTTP-запрос к Hotels API (rapidapi.com) (запрос вариантов размещения отелей).
    :param data: словарь машины состояний с сохраненными параметрами запроса.
    :return: словарь со сведениями вариантов размещения (отелей).
    """
    if data:
        method_endswith = "properties/v2/list"
        (
            location,
            hotels_count,
            check_in,
            check_out,
            adults,
            childrens,
        ) = "{location}:{hotels_count}:{check_in}:{check_out}:{adults}:{childrens}".format(
            **data
        ).split(
            ":"
        )
        check_in_data = str(check_in).split("-")
        check_in_day, check_in_month, check_in_year = (
            int(check_in_data[2]),
            int(check_in_data[1]),
            int(check_in_data[0]),
        )
        check_out_data = str(check_out).split("-")
        check_out_day, check_out_month, check_out_year = (
            int(check_out_data[2]),
            int(check_out_data[1]),
            int(check_out_data[0]),
        )
        child_list = []
        childrens_list = [i for i in childrens if i.isdigit()]
        for i in childrens_list:
            if i != "0":
                child_list.append({"age": int(i)})
            else:
                child_list.clear()

        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {"regionId": location},
            "checkInDate": {
                "day": check_in_day,
                "month": check_in_month,
                "year": check_in_year,
            },
            "checkOutDate": {
                "day": check_out_day,
                "month": check_in_month,
                "year": check_in_year,
            },
            "rooms": [{"adults": int(adults), "children": child_list}],
            "resultsStartingIndex": 0,
            "resultsSize": int(hotels_count),
            "sort": "",
            "filters": {"price": {}},
        }

        if data["user_command"] in ["/lowprice", "🔝 Дешевых отелей 🏠"]:
            price_min = "{price_min}".format(**data)
            payload["sort"] = "PRICE_LOW_TO_HIGH"
            payload.update({"price": {"max": int(price_min[0]), "min": 1}})
        elif data["user_command"] in ["/highprice", "🔝 Дорогих отелей 🏡"]:
            price_max = "{price_max}".format(**data)
            payload["sort"] = sorted("PRICE_LOW_TO_HIGH", reverse=True)
            payload.update({"price": {"max": int(price_max[0]), "min": 1}})
        elif data["user_command"] in ["/bestdeal", "🔝 Наилучшее предложение 🏘"]:
            price_min, price_max = ("{price_min}:{price_max}".format(**data)).split(":")
            payload["sort"] = ["PRICE_LOW_TO_HIGH", "DISTANCE"]
            payload.update(
                {"price": {"max": int(price_max[0]), "min": int(price_min[0])}}
            )

        try:
            response = await request_func(method_endswith, payload)
            result = json.loads(response)
            parsed = result["data"]["propertySearch"]["properties"]
            hotels_dict = {
                hotel["id"]: {
                    "id": hotel.get("id", "-"),
                    "name": hotel.get("name", "-"),
                    "reviews": hotel.get("reviews", {}).get("score", "нет данных"),
                    "loc": hotel["neighborhood"].get("name")
                    if hotel.get("neighborhood", None)
                    else "нет данных",
                    "landmarks": hotel["destinationInfo"][
                        "distanceFromDestination"
                    ].get("value"),
                    "fonfoto": hotel["propertyImage"]["image"]
                    .get("url", "-")
                    .replace("250", "1280")
                    .replace("140", "720")
                    if hotel.get("propertyImage", None)
                    else os.path.join("..", "misc", "img.png"),
                    "price": hotel["price"]["lead"].get("amount")
                    if hotel.get("price", None)
                    else 0,
                    "coordinate": "+".join(
                        map(str, hotel["mapMarker"]["latLong"].values())
                    ),
                }
                for hotel in parsed
            }
            return hotels_dict

        except Exception:
            logger.exception(Exception)
            return False


async def search_photo_hotel(hotei_id):
    """
    Выполнение HTTP-запроса к Hotels API (rapidapi.com) (поиск фото).
    :param hotel_id: id отеля.
    :return: список url-адресов фото варианта размещения (отеля)
    """
    method_endswith = "properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": str(hotei_id),
    }
    try:
        response = await request_func(method_endswith, payload)
        result = json.loads(response)
        parsed = result["data"]["propertyInfo"]
        hotel_images = parsed["propertyGallery"].get("images")
        if hotel_images is not None:
            photo_links = [
                info["image"].get("url").replace("{size}", "w") for info in hotel_images
            ]
            return photo_links
    except Exception:
        logger.exception(Exception)
        return False
