# crawldata/functions.py
from datetime import datetime
from pathlib import Path
import hashlib

PROJECT = Path(__file__).resolve().parent.parent
NOW = datetime.now()
CRAWL_DATE = NOW.strftime('%Y-%m-%d %H:%M')

from sys import path
path.append(str(PROJECT.absolute()))
parent_folder = Path(__file__).parent.resolve().parent

def calculate_id(*args):
    to_hash = "_".join(str(arg) for arg in args)
    hashed = hashlib.md5(to_hash.encode()).hexdigest()
    return hashed[:24]

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
