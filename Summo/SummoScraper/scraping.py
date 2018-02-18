# Thanks http://www.analyze-world.com/entry/2017/10/09/062445
from bs4 import BeautifulSoup
import requests
import time
from tqdm import tqdm
import re
import csv
import random


url_list = []
# url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&sc=13102&sc=13103&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
# url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13104&sc=13105&sc=13113&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
# url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13106&sc=13107&sc=13108&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
# url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13118&sc=13121&sc=13122&sc=13123&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
# url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13109&sc=13110&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13111&sc=13112&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13114&sc=13115&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13120&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13116&sc=13117&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')
url_list.append('https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13119&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=12&pc=50')

for base_url in url_list:


    print("Request start --------------------")
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
    }
    result = requests.get(base_url,headers=headers)

    print("Generate object start ------------")
    c = result.content
    soup = BeautifulSoup(c,"lxml")
    #物件リストの部分を切り出し
    summary = soup.find("div",{'id':'js-bukkenList'})

    print("Parse max page -------------------")
#全ページ数を取得
    body = soup.find("body")
    pages = body.find("div",{'class':'pagination pagination_set-nav'})
    pages_text = str(pages)
    pages_split = pages_text.split('</a></li>\n</ol>')
    pages_split = pages_split[0]
    pages_split = pages_split[-3:]
    pages_split = pages_split.replace('>','')
    pages_split = int(pages_split)
    print("  max page: ",pages_split)


    print("Make page list -------------------")
    urls = []
    urls.append(base_url)
    for i in range(pages_split-1):
        pg = str(i+2)
        url_page =base_url + '&pn=' + pg
        urls.append(url_page)
    print("  page list length: ",len(urls))


    hits = re.search("\">\s+(\d+)<span>",str(body.find("div",{'class':'paginate_set-hit'})))
    hits = int(hits.group(1))
    print("  House: ",int(hits))


    print("Collect informations -------------")
    progress = tqdm(total=hits)

    for url in urls:
        name = [] #マンション名
        address = [] #住所
        locations0 = [] #立地1つ目（最寄駅/徒歩~分）
        locations1 = [] #立地2つ目（最寄駅/徒歩~分）
        locations2 = [] #立地3つ目（最寄駅/徒歩~分）
        age = [] #築年数
        height = [] #建物高さ
        floor = [] #階
        rent = [] #賃料
        admin = [] #管理費
        others = [] #敷/礼/保証/敷引,償却
        floor_plan = [] #間取り
        area = [] #専有面積

        result = requests.get(url)
        c = result.content
        soup = BeautifulSoup(c,"lxml")
        summary = soup.find("div",{'id':'js-bukkenList'})
        if(isinstance(summary,type(None))):
            print(url)
            continue

        #マンション名、住所、立地（最寄駅/徒歩~分）、築年数、建物高さが入っているcassetteitemを全て抜き出し
        cassetteitems = summary.find_all("div",{'class':'cassetteitem'})
        #各cassetteitemsに対し、以下の動作をループ
        for i in range(len(cassetteitems)):
            #各建物から売りに出ている部屋数を取得
            tbodies = cassetteitems[i].find_all('tbody')
            #マンション名取得
            subtitle = cassetteitems[i].find("div",{'class':'cassetteitem_content-title'})
            subtitle = subtitle.get_text()

            #住所取得
            subaddress = cassetteitems[i].find("li",{'class':'cassetteitem_detail-col1'})
            subaddress = subaddress.get_text()

            #部屋数だけ、マンション名と住所を繰り返しリストに格納（部屋情報と数を合致させるため）
            for y in range(len(tbodies)):
                name.append(subtitle)
                address.append(subaddress)


            #立地を取得
            sublocations = cassetteitems[i].find_all("li",{'class':'cassetteitem_detail-col2'})
            #立地は、1つ目から3つ目までを取得（4つ目以降は無視）
            for x in sublocations:
                cols = x.find_all('div')
                for i in range(len(cols)):
                    text = cols[i].find(text=True)
                    for y in range(len(tbodies)):
                        if i == 0:
                            locations0.append(text)
                        elif i == 1:
                            locations1.append(text)
                        elif i == 2:
                            locations2.append(text)

            #築年数と建物高さを取得
            tbodies = cassetteitems[i].find_all('tbody')
            col3 = cassetteitems[i].find_all("li",{'class':'cassetteitem_detail-col3'})
            for x in col3:
                cols = x.find_all('div')
                for i in range(len(cols)):
                    text = cols[i].find(text=True)
                    for y in range(len(tbodies)):
                        if i == 0:
                            age.append(text)
                        else:
                            height.append(text)

            #階、賃料、管理費、敷/礼/保証/敷引,償却、間取り、専有面積が入っているtableを全て抜き出し
            tables = summary.find_all('table')

            #各建物（table）に対して、売りに出ている部屋（row）を取得
            rows = []
            for i in range(len(tables)):
                rows.append(tables[i].find_all('tr'))

            #各部屋に対して、tableに入っているtext情報を取得し、dataリストに格納
            data = []
            for row in rows:
                for tr in row:
                    cols = tr.find_all('td')
                    for td in cols:
                        text = td.find(text=True)
                        data.append(text)

            #dataリストから、階、賃料、管理費、敷/礼/保証/敷引,償却、間取り、専有面積を順番に取り出す
            index = 0
            for item in data:
                if '階' in item:
                    floor.append(data[index])
                    rent.append(data[index+1])
                    admin.append(data[index+2])
                    others.append(data[index+3])
                    floor_plan.append(data[index+4])
                    area.append(data[index+5])
                index +=1
            progress.update(len(tbodies))
        with open('suumo.csv', 'a') as f:
            for i in range(len(name)):
                line = ""
                try:
                    line = name[i]+","+address[i]+","+locations0[i]+","+locations1[i]+","+locations2[i]+","+age[i]+","+height[i]+","+floor[i]+","+rent[i]+","+admin[i]+","+others[i]+","+floor_plan[i]+","+area[i]+"\n"
                except:
                    continue
                f.write(line)
        time.sleep(random.randint(60,100))

    progress.close()

