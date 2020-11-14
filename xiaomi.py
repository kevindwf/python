#!coding=utf-8
import requests
import re
import random
import time
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  ###禁止提醒SSL警告


###格式化时间戳
def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(int(time_stamp))
    str_date = time.strftime(format_string, time_array)
    return str_date


def de_duplication(lst):  ##去重不改变原数据顺序
    de_du = list(set(lst))
    de_du.sort(key=lst.index)
    return de_du


class xm(object):

    ###  获取分类
    def get_categoryList(self):
        url = 'https://www.xiaomiyoupin.com/app/shopv3/pipe'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '130',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.xiaomiyoupin.com',
            'Origin': 'https://www.xiaomiyoupin.com',
            'Referer': 'https://www.xiaomiyoupin.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36'
        }
        data = {
            'data': '{"result": {"model": "Homepage", "action": "GetGroup2ClassInfo", "parameters": {}}}',
        }
        req = requests.post(url=url, headers=headers, data=data, verify=False).json()
        groups = req['result']['result']['data']['groups']
        df = pd.DataFrame(columns=('一级分类ID', '一级分类', '二级分类ID', '二级分类'))
        x = 0
        for i in groups:
            for j in i:
                class1_name = j['class']['name']  ##一级分类
                ucid1 = j['class']['ucid']  ##一级分类ID
                for k in j['sub_class']:
                    class2_name = k['name']  ##二级分类
                    ucid2 = k['ucid']  # 二级分类ID
                    df.loc[x] = [ucid1, class1_name, ucid2, class2_name]
                    x = x + 1
        # df.to_csv('list.csv',index=False, encoding="GB18030")
        return df

    ##获取商品数据
    def get_items_ID(self):
        s = requests.session()
        df = self.get_categoryList()
        cateList = df['一级分类ID'].values.tolist()
        catename = df['一级分类'].values.tolist()
        cateList = de_duplication(cateList)
        catename = de_duplication(catename)
        df_item = pd.DataFrame(columns=('一级分类ID', '一级分类', '二级分类', '二级分类ID', '商品ID', '商品名称', '商品简介', '商品图片', '上架时间',
                                        '更新时间', '零售价', '商品URL', '评分', '好评率', '评论数', '评论观点'))
        x = 0
        url = 'https://www.xiaomiyoupin.com/app/shopv3/pipe'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '145',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'mjclient=PC; youpindistinct_id=17539f333cc8f5-09b05a5d77ac29-c781f38; Hm_lvt_025702dcecee57b18ed6fb366754c1b8=1602995042,1604820631,1605095542; youpin_sessionid=175b7384830-0323c300e3c10a-2085; Hm_lpvt_025702dcecee57b18ed6fb366754c1b8=1605096721',
            'Host': 'www.xiaomiyoupin.com',
            'Origin': 'https://www.xiaomiyoupin.com',
            'Referer': 'https://www.xiaomiyoupin.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36'
        }
        s.headers.update(headers)
        for i in range(len(cateList)):  ##一级分类目录商品
            data = {
                'data': '{"uClassList": {"model": "Homepage", "action": "BuildHome", "parameters": {"id": "' + str(
                    cateList[i]) + '"}}}'
            }
            req = s.post(url=url, data=data, verify=False).json()
            itemdata = req['result']['uClassList']['data']
            for j in itemdata:
                if 'content' in j:
                    content_name = j['content']['name']  ##二级分类
                    ucid = j['content']['ucid']  # 二级分类ID
                    for k in j['data']:
                        try:
                            gid = k['gid']  ##商品ID
                            name = k['name']  ##商品名称
                            summary = k['summary']  ##商品简介
                            pic_url = k['pic_url']  ##商品图片
                            ctime = timestamp_to_date(k['ctime'])  ##上架时间
                            utime = timestamp_to_date(k['utime'])  ##更新时间
                            price_min = int(k['price_min']) / 100  ##价格
                            itemurl = k['url']  ##商品链接
                            commentdata = self.get_comment(gid)
                            avg_score = commentdata[0]
                            positive_rate = commentdata[1]
                            count = commentdata[2]
                            comment = commentdata[3]
                            df_item.loc[x] = [cateList[i], catename[i], ucid, content_name, gid, name, summary, pic_url,
                                              ctime, utime, price_min, itemurl, avg_score, positive_rate, count,
                                              comment]
                            print(cateList[i], catename[i], ucid, content_name, gid, name, summary, pic_url, ctime,
                                  utime, price_min, itemurl, avg_score, positive_rate, count, comment)
                            x = x + 1
                        except:
                            print(j)

        df_item.to_csv('df_item.csv', index=False, encoding="GB18030")
        return df_item

    ##获取单个商品ID评论数及评论观点数据
    def get_comment(self, id):
        url = 'https://www.xiaomiyoupin.com/app/shopv3/pipe'
        UserAgentlist = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.104',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.5.4000',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',

        ]
        ran = random.randint(0, len(UserAgentlist) - 1)
        UserAgen = UserAgentlist[ran]
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '364',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'youpin.mi.com',
            'Origin': 'https://www.xiaomiyoupin.com',
            'Referer': 'https://www.xiaomiyoupin.com/detail?gid={}'.format(str(id)),
            'User-Agent': UserAgen
        }
        postdata = {
            'data': '{"overView":{"model":"Product","action":"CommentIndexV2","parameters":{"gid":' + str(
                id) + '}},"list":{"model":"Product","action":"CommentListOnly","parameters":{"index_type":0,"gid":' + str(
                id) + ',"pindex":1,"psize":10,"tag_name":null}}}'
        }
        req = requests.post(url=url, data=postdata, headers=headers, verify=False).text
        js = json.loads(req)
        data = js['result']['overView']['data']
        comment = ''
        avg_score = '0'
        positive_rate = '0'
        count = '0'
        if data != []:
            avg_score = data['avg_score']  ##评分
            positive_rate = data['positive_rate']  ####好评率
            count = data['tags'][0]['count']  ##评论数
            for i in data['tags']:
                comment = str(comment) + str(i['name']) + '(' + str(i['count']) + ')'  ##评论观点
        commentdata = [avg_score, positive_rate, count, comment]
        print(commentdata)
        return commentdata


if __name__ == '__main__':
    xm = xm()
    xm.get_items_ID()
