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
TOKYO_STATION=(35.681167,139.767052)


with open('suumo_conv.csv','w') as out:
    # out.write('名前,区,住所,路線1,最寄り駅1,徒歩1,路線2,最寄り駅2,徒歩2,路線3,最寄り駅3,徒歩3,'+\
    #         '築年数,高さ,階,家賃,管理費,敷金,礼金,保証金,敷引,償却,S,DK,K,L,ワンルーム,部屋数,専有面積\n')
    # out.write('区,住所,路線1,最寄り駅1,徒歩1,路線2,最寄り駅2,徒歩2,路線3,最寄り駅3,徒歩3,'+\
    #         '築年数,高さ,階,家賃,管理費,敷金,礼金,保証金,敷引,償却,S,DK,K,L,ワンルーム,部屋数,専有面積\n')
    out.write('ward,address,route1,station1,walk1,route2,station2,walk2,route3,station3,walk3,'+\
            'years,height,floor,rent,admin_cost,deposit,gratuity,sec,shikibiki,amortization,'+\
            'S,DK,K,L,one_room,room,area,lat,lon,distance\n')
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
                    route2=''
                    route3=''
                    station1=''
                    station2=''
                    station3=''
                    walk1=''
                    walk2=''
                    walk3=''
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
                            : #最寄りがバス停もしくは車でN分のものは除外
                            route1='-1'
                            station1='-1'
                            walk1 = '100'
                        else:
                            try:
                                route1=route_table[route1]
                            except KeyError:
                                route_index=route_index+1
                                route_table[route1]=route_index
                                route1=route_index
                            try:
                                station1=station_table[station1]
                            except KeyError:
                                station_index=station_index+1
                                station_table[station1]=station_index
                                station1=station_index
                            walk1 = tmp[1].replace('分','')

                        tmp = row[3].split(' 歩')
                        route2,station2 = tmp[0].split('/')
                        if station2 == '学芸大学':
                            station2 = '学芸大学駅'
                        if tmp[0].find('バス') > -1 or \
                            re.match(r'^.{1,2}\d\d',route2) or \
                            re.match(r'^.{2}$',route2) or \
                            route2.find('北加平') > -1 or \
                            tmp[0].find('朝日自動車') > -1 or \
                            tmp[0].find('東京都交通局') > -1 or \
                            route2.find('町屋駅') > -1 or \
                            route2.find('王子駅前') > -1 or \
                            route2.find('新小岩') > -1 or \
                            route2.find('玉４・玉５') > -1 or \
                            route2.find('南コース') > -1 or \
                            route2.find('ＪＲ山手線　品川駅') > -1 or \
                            route2.find('一之江') > -1 or \
                            route2.find('赤羽東口行') > -1 or \
                            re.search(r'車\d{1,2}分', station2) \
                            : #最寄りがバス停のものは除外
                            route2='-1'
                            station2='-1'
                            walk2 = '100'
                        else:
                            try:
                                route2=route_table[route2]
                            except KeyError:
                                route_index=route_index+1
                                route_table[route2]=route_index
                                route2=route_index
                            try:
                                station2=station_table[station2]
                            except KeyError:
                                station_index=station_index+1
                                station_table[station2]=station_index
                                station2=station_index
                            walk2 = tmp[1].replace('分','')

                        tmp = row[4].split(' 歩')
                        route3,station3 = tmp[0].split('/')
                        if station3 == '学芸大学':
                            station3 = '学芸大学駅'
                        if tmp[0].find('バス') > -1 or \
                            re.match(r'^.{1,2}\d\d',route3) or \
                            re.match(r'^.{2}$',route3) or \
                            route3.find('北加平') > -1 or \
                            tmp[0].find('朝日自動車') > -1 or \
                            tmp[0].find('東京都交通局') > -1 or \
                            route3.find('町屋駅') > -1 or \
                            route3.find('新小岩') > -1 or \
                            route3.find('王子駅前') > -1 or \
                            route3.find('一之江') > -1 or \
                            route3.find('ＪＲ山手線　品川駅') > -1 or \
                            route3.find('南コース') > -1 or \
                            route3.find('玉４・玉５') > -1 or \
                            route3.find('赤羽東口行') > -1 or \
                            re.search(r'車\d{1,2}分', station3) \
                            : #最寄りがバス停のものは除外
                            route3='-1'
                            station3='-1'
                            walk3 = '100'
                        else:
                            try:
                                route3=route_table[route3]
                            except KeyError:
                                route_index=route_index+1
                                route_table[route3]=route_index
                                route3=route_index
                            try:
                                station3=station_table[station3]
                            except KeyError:
                                station_index=station_index+1
                                station_table[station3]=station_index
                                station3=station_index
                            walk3 = tmp[1].replace('分','')
                    except :
                        pass

                    #築年数
                    built = re.search(r'築(\d+)年', row[5])
                    built = built.group(1) if built else  '1' #新築

                    #高さ
                    high = re.search(r'(\d+)階建', row[6])
                    high = high.group(1) if high else '1' #平屋

                    #回数
                    floor = row[7].replace('階','')
                    floor = floor.split('-')[0]
                    floor = floor.replace('B','-')

                    #家賃
                    rent = float(row[8].replace('万円',''))

                    #管理費
                    admin_cost = float(row[9].replace('円','').replace('-','0'))

                    #敷金/礼金/保証金/敷引/償却
                    tmp = row[10].split('/')
                    deposit = float(tmp[0].replace('万円','').replace('-','0'))
                    gratuity = float(tmp[1].replace('万円','').replace('-','0'))
                    sec = float(tmp[2].replace('万円','').replace('-','0'))
                    tmp = tmp[3].split('・')
                    shikibiki = float(tmp[0].replace('万円','').replace('-','0').replace('実費','0'))
                    amortization = float(tmp[1].replace('万円','').replace('-','0')) if 1 < len(tmp) else 0.0

                    #間取り
                    one_room = 1 if 0 <= row[11].find('ワンルーム') else 0
                    row[11] = row[11].replace('ワンルーム','')
                    service_room = 1 if 0 <= row[11].find('S') else 0
                    row[11] = row[11].replace('S','')
                    dining_kitchen = 1 if 0<= row[11].find('DK') else 0
                    row[11] = row[11].replace('DK','')
                    kitchen = 1 if 0<= row[11].find('K') else 0
                    row[11] = row[11].replace('K','')
                    living = 1 if 0<= row[11].find('L') else 0
                    row[11] = row[11].replace('L','')
                    room = int(row[11]) if 0 < len(row[11]) else 0

                    #専有面積
                    area = float(row[12].replace('m',''))

                    out.write(\
                            # str(name)+','+ \
                            str(ward) + ',' + \
                            str(address) + ',' + \
                            str(route1) + ',' + \
                            str(station1) + ',' + \
                            str(walk1) + ',' + \
                            str(route2) + ',' + \
                            str(station2) + ',' + \
                            str(walk2) + ',' + \
                            str(route3) + ',' + \
                            str(station3) + ',' + \
                            str(walk3) + ',' + \
                            str(built) + ',' + \
                            str(high) + ',' + \
                            str(floor) + ',' + \
                            str(rent) + ',' + \
                            str(admin_cost) + ',' + \
                            str(deposit) + ',' + \
                            str(gratuity) + ',' + \
                            str(sec) + ',' + \
                            str(shikibiki) + ',' + \
                            str(amortization) + ',' + \
                            str(service_room) + ',' + \
                            str(dining_kitchen) + ',' + \
                            str(kitchen) + ',' + \
                            str(living) + ',' + \
                            str(one_room) + ',' + \
                            str(room) + ',' +\
                            str(area)+',' +\
                            str(lat) + ',' +\
                            str(lon) + ',' +\
                            str(distance) + '\n')
                except :
                    import traceback
                    traceback.print_exc()
                    print("error: ",row)
                    continue
with open('route_table.txt','w') as out:
    out.write(str(route_table).replace(',',',\n'))
with open('station_table.txt','w') as out:
    out.write(str(station_table).replace(',',',\n'))
