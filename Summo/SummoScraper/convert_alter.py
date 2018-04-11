import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import csv
import re
import pandas as pd
from geopy.distance import great_circle

target_files = ['suumo.csv']
ward_list={
'千代田':1,
'中央':2,
'港':3,
'新宿':4,
'文京':5,
'台東':6,
'墨田':7,
'江東':8,
'品川':9,
'目黒':10,
'大田':11,
'世田谷':12,
'渋谷':13,
'中野':14,
'杉並':15,
'豊島':16,
'北':17,
'荒川':18,
'板橋':19,
'練馬':20,
'足立':21,
'葛飾':22,
'江戸川':23
}

route_table={}
route_index=-1
station_table={}
station_index=-1

map_data = pd.read_csv('map_data.csv')
joukou_data = pd.read_csv('joukou_jinin_utf.csv')
TOKYO_STATION=(35.681167,139.767052)


with open('suumo_distance_joukou.csv','w') as out:
    out.write('walk,joukou,rent_admin_cost,area,lat,lon,distance\n')
    for tf in target_files:
        with open(tf, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    #名前
                    name = row[0]

                    #住所
                    row[1] = row[1].replace('東京都','')
                    tmp = row[1].split('区')
                    ward =ward_list[tmp[0]]
                    address = tmp[1]
                    address = address.translate(str.maketrans('１２３４５６７８９','一二三四五六七八九'))
                    address = re.sub('(?P<n>[一二三四五六七八九十])$','\g<n>丁目', address)
                    if re.match(r'(神田三崎町)|(神田猿楽町).+',address):
                        address = address.replace('神田','')
                    if re.match(r'四谷本塩町',address):
                        address = address.replace('四谷','')
                    if '坂町' == address:
                        address = '四谷'+address
                    address = address.replace('ヶ','ケ')
                    map_record = map_data[map_data['大字町丁目名'] == address]
                    lat = 0
                    lon = 0
                    distance = 0
                    try:
                        lat = map_record.iloc[0]['緯度']
                        lon = map_record.iloc[0]['経度']
                        distance = great_circle(TOKYO_STATION, (lat,lon)).kilometers
                    except:
                        print(address)


                    #最寄り駅
                    route1=''
                    joukou=''
                    station1=''
                    walk1=''
                    try:
                        # 車N分は無視
                        tmp = row[2].split(' 歩')
                        route1,station1 = tmp[0].split('/')
                        if station1 == '学芸大学':
                            station1 = '学芸大学駅'

                        if tmp[0].find('バス') > -1 or \
                            re.match(r'^.{1,2}\d\d',route1) or \
                            re.match(r'^.{2}$',route1) or \
                            route1.find('北加平') > -1 or \
                            tmp[0].find('朝日自動車') > -1 or \
                            tmp[0].find('東京都交通局') > -1 or \
                            route1.find('町屋駅') > -1 or \
                            route1.find('王子駅前') > -1 or \
                            route1.find('新小岩') > -1 or \
                            route1.find('玉４・玉５') > -1 or \
                            route1.find('ＪＲ山手線　品川駅') > -1 or \
                            route1.find('一之江') > -1 or \
                            route1.find('南コース') > -1 or \
                            route1.find('赤羽東口行') > -1 or \
                            re.search(r'車\d{1,2}分', station1) \
                            :
                            print('continue...',tmp)
                            continue
                        else:
                            walk1 = tmp[1].replace('分','')
                            joukou_record = joukou_data[joukou_data['駅名'] == station1]
                            joukou = joukou_record.iloc[0]['乗降人員']

                    except :
                        print('pass...')
                        pass

                    #家賃
                    rent = float(row[8].replace('万円',''))

                    #管理費
                    admin_cost = float(row[9].replace('円','').replace('-','0'))

                    #専有面積
                    area = float(row[12].replace('m',''))

                    out.write(\
                            str(walk1) + ',' + \
                            str(joukou) + ',' + \
                            str(int(rent)+int(admin_cost)/10000) + ',' + \
                            str(area)+',' +\
                            str(lat) + ',' +\
                            str(lon) + ',' +\
                            str(distance) + '\n')
                except :
                    import traceback
                    traceback.print_exc()
                    print("error: ",row)
                    continue
