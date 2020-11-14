import requests
import json

def parseList():
    headers = {
    'Host':'www.xiaomiyoupin.com',
    'Connection':'keep-alive',
    'sec-ch-ua':'"Chromium";v="86", "\"Not\\A;Brand";v="99", "Google Chrome";v="86"',
    'X-User-Agent':'channel/youpin platform/youpin.pc',
    'DToken':'',
    'sec-ch-ua-mobile':'?0',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'X-Yp-App-Source':'front-PC',
    'Content-Type':'application/json',
    'Accept':'*/*',
    'Origin':'https://www.xiaomiyoupin.com',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-Mode':'cors',
    'Sec-Fetch-Dest':'empty',
    'Referer':'https://www.xiaomiyoupin.com/search?queryId=3d412d93d144c8db900cf0da872f7402&categoryName=%E6%95%B0%E6%8D%AE%E7%BA%BF&pageFrom=category',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Cookie':'mjclient=PC; youpindistinct_id=17539f333cc8f5-09b05a5d77ac29-c781f38; Hm_lvt_025702dcecee57b18ed6fb366754c1b8=1602995042,1604820631,1605095542; Hm_lpvt_025702dcecee57b18ed6fb366754c1b8=1605099944; youpin_sessionid=175b769a133-00f8cf2afe61da-2085',
            }

    data = '[{},{"baseParam":{"imei":"","clientVersion":"","ypClient":3},"queryId":"3d412d93d144c8db900cf0da872f7402","sortBy":0,"pageIdx":0,"source":"searchPage","filter":null,"requestId":"530749403096026","clientPageId":"3702764629504265","queryString":"数据线"}]'
    re = requests.post('https://www.xiaomiyoupin.com/mtop/market/search/v2/queryIdSearch',
                       headers = headers,
                       data = data.encode('utf-8'))
    if re.status_code == 200:
        re.encoding = 'utf-8'
        list = re.json()['data']['data']['goods']
        ids = []
        for item in list:
            productId = item['data']['goodsInfo']['gid']
            # print(productId)
            ids.append(productId)
        return ids


def parseItem(id):
    headers= {
    'Host':'www.xiaomiyoupin.com',
    'Connection': 'keep-alive',
    'Content-Length': '108',
    'sec-ch-ua': '"Chromium";v="86", "\"Not\\A;Brand";v="99", "Google Chrome";v="86"',
    'X-User-Agent': 'channel/youpin platform/youpin.pc',
    'DToken': '',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'X-Yp-App-Source': 'front-PC',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Origin': 'https://www.xiaomiyoupin.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.xiaomiyoupin.com/detail?gid=125042&spmref=YouPinPC.$SearchFilter$1.search_list.1.93494681',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'mjclient=PC; youpindistinct_id=17539f333cc8f5-09b05a5d77ac29-c781f38; Hm_lvt_025702dcecee57b18ed6fb366754c1b8=1602995042,1604820631,1605095542; youpin_sessionid=175b78c83f2-08131e2c888061-2085; Hm_lpvt_025702dcecee57b18ed6fb366754c1b8=1605102241',

    }

    data = '{"groupName":"details","groupParams":[["' + str(id) + '"]],"methods":[],"version":"1.0.0","debug":false,"channel":""}'
    re = requests.post('https://www.xiaomiyoupin.com/api/gateway/detail',
                       headers = headers,
                       data = data.encode('utf-8'))
    if re.status_code == 200:
        re.encoding = 'utf-8'
        product = re.json()['data']['goods']['goodsInfo']['name']
        print(product)

ids = parseList()
for id in ids:
    parseItem(id)