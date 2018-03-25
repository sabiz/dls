import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import csv
import pandas as pd
from geopy.distance import great_circle

map_data = pd.read_csv('map_data.csv')
TOKYO_STATION=(35.681167,139.767052)

print("住所入力")
address=input()
map_record = map_data[map_data['大字町丁目名'] == address]

lat = 0
lon = 0
distance = 0
try:
    lat = map_record.iloc[0]['緯度']
    lon = map_record.iloc[0]['経度']
    distance = great_circle(TOKYO_STATION, (lat,lon)).kilometers
except:
    print("DBにない...")
    exit(-1)
print("lat= ",lat)
print("lot= ",lot)
print("distance= ",distance)
