from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['evcs_db']
collection = db['charging_stations']

# Đếm số phần tử có current_time = "2025-05-02 14:30"   # 916
time_ = "2025-05-05 16:00"
count = collection.count_documents({"current_time": time_})

# In ra kết quả
print(f"Số phần tử có current_time = '{time_}': {count}")


# Tìm các giá trị current_time duy nhất
unique_times = collection.distinct("current_time")

# In ra kết quả
print("Các giá trị current_time duy nhất:")
for time in unique_times:
    print(time)


# 0 */1 * * * cd /home/hung/Documents/DEMO/charging-station/test && /home/hung/.local/share/virtualenvs/works-4wnlDAsI/bin/python evcs_data_collector.py