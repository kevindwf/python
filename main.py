import requests
from lxml import etree
import csv
import re
import time
import random
from datetime import date
from datetime import datetime
import os

# 豆瓣top250网址
DOMAIN = 'https://cn.ad101.org'
IMAGECOVER = 'https://m2.afast.ws/{}/images/cover.jpg'
_pageIndex = 0
_counter = 0



def getHtml(url):
    html = sendRequest(url)
    if html:
        return html

    retry = 1
    while retry < 10:
        print('url access failed: {}, sleep for {}s'.format(url, 60 * retry))
        time.sleep(60 * retry)
        html = sendRequest(url)
        if html:
            return html
        else:
            retry += 1

    print('url access failed after retries: ' + url)
    saveLog('url access failed after retries: ' + url)
    raise Exception('url access failed after retries: ' + url)


# 获取网页源码
def sendRequest(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    try:
        start = datetime.now()
        print('Access url: ' + url + ', at: ' + str(start))
        response = requests.get(url, headers=headers, timeout=120)
        end = datetime.now()
        diff = (end - start).total_seconds()
        print('time used: ' + str(diff))

        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
    except:
        return None


def parseList(html):
    selector = etree.HTML(html)
    links = selector.xpath('/html/body/section/div/div[2]/ul/li/a/@href')

    movieList = []
    for link in links:
        # print(link)
        id = re.split('v=', link)[1]
        # sleep for 0-60s
        sleepTime = random.random() * 30
        print('------------------{} start---------------------'.format(id))
        print('sleep for {}s to get new movie'.format(sleepTime))
        time.sleep(sleepTime)
        detailHtml = getHtml(DOMAIN + link)

        if detailHtml:
            movie = parseDetail(id, detailHtml)
            movieList.append(movie)
            print('------------------{} end-----------------------'.format(id))

    print('page handle finished, movies count: {}', len(movieList))
    return movieList


def parseDetail(id, html):
    selector = etree.HTML(html)
    title = selector.xpath('/html/body/section/article/div[1]/h1/text()')
    tags = selector.xpath('/html/body/section/article/div[1]/h1/span/text()')
    like = selector.xpath('//*[@id="user-num-like"]/text()')[0]
    view = selector.xpath('//*[@id="flike"]/div[1]/p/text()')[0]
    # properties = selector.xpath('normalize-space(//*[@id="flike"]/div[3]/ul)')
    # print(selector.xpath('string(//*[@id="flike"]/div[3]/ul)'))
    # print(selector.xpath('normalize-space(//*[@id="flike"]/div[3]/ul)'))
    # print('\n'.join(selector.xpath('//*[@id="flike"]/div[3]/ul')[0].itertext()))
    cover = selector.xpath('//*[@id="my-player"]/@poster')[0]

    movie = {'id': id,
             'page': _pageIndex,
             # 'title': ''.join(title),
             'tags': '|'.join(tags),
             'like': like,
             'view': view.replace('临幸数：', '')}

    lis = selector.xpath('//*[@id="flike"]/div[3]/ul/li')
    for li in lis:
        name = li.xpath('span/text()')[0]
        value = ''

        if name == '片名':
            value = li.xpath('p/text()')[0]
        elif name == '女优':
            value = li.xpath('normalize-space(h2)').replace(' 、 ', '|')
        elif name == '关键字':
            value = li.xpath('normalize-space(h3)').replace(' 、 ', '|')
        elif name == '番号':
            value = li.xpath('h2/a/text()')[0]
        elif name == '其他信息':
            # 上传人: morr***，上传日期: 2020-10-21
            text = li.xpath('div/text()')[0]
            value = text
            parts = re.split('，', text)
            for p in parts:
                a = re.split(': ', p)
                movie[a[0]] = a[1]
        else:
            saveLog("new key name found, id:" + id + " ,name:" + name)

        if name != '其他信息':
            movie[name] = value

        movie['抓取时间'] = date.today()

        # print(name+": "+value)

    global _counter
    _counter += 1
    print('index: {}, counter: {}, title: {}'.format(_pageIndex, _counter, movie['片名']))

    saveImage(cover, id)

    # print(list(movie))
    # print(movie)
    return movie


# 保存数据
def writeData(movieList):
    fileName = 'douban_top2500.csv'
    with open(fileName, 'a+', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'page', 'tags', 'like', 'view', '片名', '女优', '关键字', '番号', ' 上传人',
                                               '上传日期', '抓取时间'])
        # writer.writeheader()  # 写入表头
        for each in movieList:
            # writer = csv.DictWriter(f, fieldnames=list(each))
            writer.writerow(each)

        print('save to excel succeed')


def saveLog(msg):
    with open('error', 'a') as f:
        f.write(msg+'\n')


def saveIndex(index):
    with open('index', 'w') as f:
        f.write(str(index))


def readIndex():
    try:
        with open('index') as f:
            return int(f.read())
    except:
        return 0


def saveImage(url, fileName):
    retry = 0
    res = None
    while retry < 6 and res is None:
        try:
            res = requests.get(url, stream=True, timeout=120)
            if res.ok:
                with open('covers/{}.jpg'.format(fileName), 'wb') as f:
                    for chunk in res.iter_content():
                        f.write(chunk)

                print('Save image succeed, {}'.format(fileName))
                return
        except:
            pass

        res = None
        retry += 1
        print('save image failed, sleep for {}s to start next try'.format(retry*60))
        time.sleep(retry*60)

    print('image save failed after retries: ' + url)
    saveLog('image save failed after retries: ' + url)


# 启动
if __name__ == "__main__":
    if not os.path.exists('covers'):
        os.mkdir('covers')

    start = readIndex() + 1
    end = start + 2000
    for i in range(start, end):
        movieList = []
        _pageIndex = i

        pageLink = DOMAIN + '/?page={}'.format(i)
        print('start new page: {}'.format(pageLink))
        source = getHtml(pageLink)
        movieList = parseList(source)

        writeData(movieList)
        saveIndex(i)

    # html = getHtml('https://cn.ad101.org/watch?v=OQZyP6ae81z')
    # print(html)
    # parseDetail('OQZyP6ae81z', html)
