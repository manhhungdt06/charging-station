import requests
import hashlib
import pymongo
import time
from pymongo import MongoClient
from requests.exceptions import RequestException, Timeout

def calculate_id(*args):
    to_hash = "_".join(str(arg) for arg in args)
    hashed = hashlib.md5(to_hash.encode()).hexdigest()
    return hashed[:24]

def make_request_with_retry(request_func, max_retries=3, timeout=10, retry_delay=5):
    for attempt in range(max_retries):
        try:
            return request_func(timeout=timeout)
        except (RequestException, Timeout) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Request failed: {e}. Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
            time.sleep(retry_delay)
    return None

districts = [
    "Quận Ba Đình",
    "Quận Cầu Giấy",
    "Quận Hoàn Kiếm",
    "Quận Hai Bà Trưng",
    "Quận Hoàng Mai",
    "Quận Đống Đa",
    "Quận Tây Hồ",
    "Quận Thanh Xuân",
    "Quận Bắc Từ Liêm",
    "Quận Hà Đông",
    "Quận Long Biên",
    "Quận Nam Từ Liêm",
    "Huyện Ba Vì",
    "Huyện Chương Mỹ",
    "Huyện Đan Phượng",
    "Huyện Đông Anh",
    "Huyện Gia Lâm",
    "Huyện Hoài Đức",
    "Huyện Mê Linh",
    "Huyện Mỹ Đức",
    "Huyện Phú Xuyên",
    "Huyện Phúc Thọ",
    "Huyện Quốc Oai",
    "Huyện Sóc Sơn",
    "Huyện Thạch Thất",
    "Huyện Thanh Oai",
    "Huyện Thanh Trì",
    "Huyện Thường Tín",
    "Huyện Ứng Hòa",
    "Thị xã Sơn Tây"
]

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'referer': 'https://evcs.vn/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
}

client = MongoClient('mongodb://localhost:27017/')
db = client['evcs_db']
collection = db['charging_stations']

for district in districts:
    cookies = {}
    params = {
        'address': district,
    }
    try:
        response = make_request_with_retry(
            lambda timeout: requests.get('https://evcs.vn/location', params=params, cookies=cookies, headers=headers, timeout=timeout)
        )
        
        if response.status_code != 200:
            print(f"Failed to get locations for {district}: {response.status_code}")
            continue
    except Exception as e:
        print(f"Failed to get locations for {district} after retries: {e}")
        continue
        
    locations_coordinates = response.json()

    for each_location in locations_coordinates:
        addr = each_location['address']
        if ", Hà Nội" in addr[-8:].title():
            lat = each_location['latitude']
            long = each_location['longitude']

            params = {
                'ev': 'cs',
                'nonce': 'bsi9el',  # 1gqpn0rn
            }

            json_data = {
                'latitude': lat,
                'longitude': long,
            }

            try:
                station_response = make_request_with_retry(
                    lambda timeout: requests.post('https://evcs.vn/', params=params, cookies=cookies, headers=headers, json=json_data, timeout=timeout)
                )
                
                if station_response.status_code != 200:
                    print(f"Failed to get station data for {addr}: {station_response.status_code}")
                    continue
            except Exception as e:
                print(f"Failed to get station data for {addr} after retries: {e}")
                continue
                
            station_data = station_response.json()
            
            if 'data' in station_data:
                for item in station_data['data']:
                    if 'media' in item:
                        del item['media']
                    
                    location_id = item.get('locationId', '')
                    station_name = item.get('stationName', '')
                    station_address = item.get('stationAddress', '')
                    latitude = item.get('latitude', 0)
                    longitude = item.get('longitude', 0)
                    
                    current_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    doc_id = calculate_id(current_time, location_id, latitude, longitude)
                    
                    mongodb_doc = {
                        '_id': doc_id,
                        'time': current_time,
                        'district_id': calculate_id(*list(each_location.values())),
                        'district': each_location['address'],
                        'locationId': location_id,
                        'stationName': station_name,
                        'stationAddress': station_address,
                        'latitude': latitude,
                        'longitude': longitude,
                        'isPublic': item.get('isPublic', False),
                        'isFreeParking': item.get('isFreeParking', False),
                        'workingTimeDescription': item.get('workingTimeDescription', ''),
                        'evse': item.get('evse', ''),
                        
                        # change if the investor upgrades, charging stations, also need to be updated continuously
                        'evsePowers': item.get('evsePowers', []),
                        
                        # Important fields need to be updated 30 minutes
                        'numberOfAvailableEvse': item.get('numberOfAvailableEvse', 0),
                        'depotStatus': item.get('depotStatus', ''),
                    }
                    
                    for db_attempt in range(5):
                        try:
                            collection.update_one(
                                {'_id': doc_id},
                                {'$set': mongodb_doc},
                                upsert=True
                            )
                            print(f"Inserted/updated station {location_id}")
                            break
                        except pymongo.errors.DuplicateKeyError:
                            print(f"Station {location_id} already exists in database")
                            break
                        except pymongo.errors.AutoReconnect:
                            if db_attempt < 2:
                                print(f"MongoDB connection error. Retrying in 3 seconds... (Attempt {db_attempt+1}/3)")
                                time.sleep(3)
                            else:
                                print(f"Failed to connect to MongoDB after 3 attempts for station {location_id}")
                        except Exception as e:
                            print(f"Error inserting station {location_id}: {e}")
                            break