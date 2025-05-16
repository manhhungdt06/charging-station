# crawldata/spiders/evcs.py
from crawldata.functions import *
from scrapy import Spider, Request, FormRequest
from crawldata.items import EvcsItem
import json

class EvcsSpider(Spider):
    name = "evcs"
    custom_settings = {
        "LOG_FILE": f"{parent_folder}/log/{parent_folder.name}_{name}.log",
    }

    def __init__(self, *args, **kwargs):
        super(EvcsSpider, self).__init__(*args, **kwargs)
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=1, i",
            "referer": "https://evcs.vn/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        }

    def start_requests(self):
        for district in districts:
            # print(f"Requesting {district}")
            yield Request(
                url="https://evcs.vn/location",
                method="GET",
                headers=self.headers,
                cb_kwargs={"district": district},
                dont_filter=True,
                meta={"address": district},
                # params={"address": district},
            )

    def parse(self, response, district=None):
        # print(response.meta.get("address"))
        data = json.loads(response.text)
        for each_location in data:
            if ", Hà Nội" in each_location["address"][-8:].title():
                lat = each_location["latitude"]
                long = each_location["longitude"]
                meta = {
                    "address": each_location["address"],
                    "latitude": lat,
                    "longitude": long,
                    "district_id": calculate_id(*list(each_location.values())),
                }
                yield FormRequest(
                    url="https://evcs.vn/",
                    method="POST",
                    headers=self.headers,
                    formdata={
                        "ev": "cs",
                        "nonce": "bsi9el",
                    },
                    body=json.dumps({"latitude": lat, "longitude": long}),
                    callback=self.parse_station,
                    meta=meta,
                    dont_filter=True,
                )

    def parse_station(self, response):
        # print(response.meta)
        result = json.loads(response.text)
        # print(len(result.get("data", [])))
        for item in result.get("data", []):
            if "media" in item:
                del item["media"]

            yield EvcsItem(
                _id=calculate_id(CRAWL_DATE, item.get("locationId", ""), item.get("latitude", 0), item.get("longitude", 0)),
                current_time=CRAWL_DATE,
                district=response.meta["address"],
                district_id=response.meta["district_id"],
                locationId=item.get("locationId", ""),
                stationName=item.get("stationName", ""),
                stationAddress=item.get("stationAddress", ""),
                latitude=item.get("latitude", 0),
                longitude=item.get("longitude", 0),
                isPublic=item.get("isPublic", False),
                isFreeParking=item.get("isFreeParking", False),
                workingTimeDescription=item.get("workingTimeDescription", ""),
                evse=item.get("evse", ""),
                evsePowers=item.get("evsePowers", []),
                numberOfAvailableEvse=item.get("numberOfAvailableEvse", 0),
                depotStatus=item.get("depotStatus", ""),
            )
