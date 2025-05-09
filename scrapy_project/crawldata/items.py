# crawldata/items.py
from scrapy import Item, Field

class EvcsItem(Item):
    _id = Field()
    current_time = Field()
    district_id = Field()
    district = Field()
    locationId = Field()
    stationName = Field()
    stationAddress = Field()
    latitude = Field()
    longitude = Field()
    isPublic = Field()
    isFreeParking = Field()
    workingTimeDescription = Field()
    evse = Field()
    evsePowers = Field()
    numberOfAvailableEvse = Field()
    depotStatus = Field()
