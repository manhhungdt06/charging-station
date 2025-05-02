- remove unused fields {'media' inner each child item of 'data'}
- get the remaining "keys" (aka fields) of each 'child item' in 'data'

```python
import hashlib


def calculate_id(*args):
    to_hash = "_".join(str(arg) for arg in args)
    hashed = hashlib.md5(to_hash.encode()).hexdigest()
    return hashed[:24]
```

```mongodb
{
    '_id': calculate_id(locationId, latitude, longitude),
    'locationId': 'C.HNO1161', 
    'stationName': 'Nhượng Quyền Tư Nhân Nguyễn Đức Toàn', 
    'stationAddress': 'Đội Nhân, Vĩnh Phúc, Ba Đình, Hà Nội', 
    'latitude': 21.041803, 
    'longitude': 105.81366, 
    'evsePowers': [
        {
            'type': 22000, 'numberOfAvailableEvse': 1, 'totalEvse': 1
        }
    ], 
    'numberOfAvailableEvse': 1, 
    'isPublic': True, 
    'isFreeParking': True, 
    'workingTimeDescription': '24/7', 
    'depotStatus': 'Available', 
    'evse': 'VinFast',
    'dictrict': ... # this is the group by field - please fill this using "each_location"  variable
}
```

- push localhost mongodb