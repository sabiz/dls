import csv
import re

target_files = ['suumo_1.csv','suumo_2.csv']
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

with open('suumo_conv.csv','w') as out:
    out.write('名前,区,住所,最寄り駅1,徒歩1,最寄り駅2,徒歩2,最寄り駅3,徒歩3,'+\
            '築年数,高さ,階,家賃,管理費,敷金,礼金,保証金,敷引,償却,S,DK,K,L,ワンルーム,部屋数,専有面積\n')
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

                    #最寄り駅
                    route1=''
                    route2=''
                    route3=''
                    walk1=''
                    walk2=''
                    walk3=''
                    try:
                        # 車N分は無視
                        tmp = row[2].split(' 歩')
                        route1,station1 = tmp[0].split('/')
                        walk1 = tmp[1].replace('分','')

                        tmp = row[3].split(' 歩')
                        route2,station2 = tmp[0].split('/')
                        walk2 = tmp[1].replace('分','')

                        tmp = row[4].split(' 歩')
                        route3,station3 = tmp[0].split('/')
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

                    out.write(str(name)+','+ \
                            str(ward) + ',' + \
                            str(address) + ',' + \
                            str(route1) + ',' + \
                            str(walk1) + ',' + \
                            str(route2) + ',' + \
                            str(walk2) + ',' + \
                            str(route3) + ',' + \
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
                            str(area)+'\n')
                except :
                    print(sys.exc_info())
                    continue

