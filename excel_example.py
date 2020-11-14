import csv


def readFile(file):
    with open(file, encoding='utf8') as f:
        return f.readlines()

def find(row, allLines):
    for line in allLines:
        if row['id'] in line:
            print('found by id:'+row['id'])
            return True

        title = row['title'].strip()
        if title in line:
            print('found by title: {}, line: {}'.format(row['title'], line))
            return True
        if len(title)>4 and title[0: int(len(title)*0.7)] in line:
            print('found by title: {}, line: {}'.format(row['title'], line))
            return True

        if row['no'] == '':
            continue
        no = row['no']
        if 'FC2-PPV-' in no:
            no = no.replace('FC2-','')
        if no in line:
            print('found by no:{}, line:{}'.format(row['no'], line))
            return True
        if no.replace(' ', '-') in line:
            print('found by no:{}, line:{}'.format(row['no'], line))
            return True
        if no.replace(' ', '_') in line:
            print('found by no:{}, line:{}'.format(row['no'], line))
            return True


allMovies = readFile('movielist.txt')

# 读取csv至字典
csvFile = open("douban_top2500.csv", "r", encoding="utf8")

with open('douban_top2500.csv','r', encoding="utf8") as csvinput:
    with open('output.csv', 'w', encoding="utf8", newline='') as csvoutput:
        writer = csv.writer(csvoutput)

        reader = csv.reader(csvinput)

        dict = {}
        # 建立空字典
        for row in reader:
            # 忽略第一行
            # if reader.line_num == 1:
            #     continue
            dict['id'] = row[0]
            dict['title'] = row[5]
            dict['no'] = row[8]
            # print(dict)
            isFind = False
            if find(dict, allMovies):
                isFind = True
                # print('found:'+ dict['title'])
            link='https://cn.ad101.org/watch?v={}'.format(dict['id'])
            writer.writerow(row + [isFind] + [link])



        csvFile.close()
