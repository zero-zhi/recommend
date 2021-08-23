#! /usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import math
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sqlite3
import re
import jieba
import jieba.analyse


def showMenu():
    """显示菜单"""
    print("=" * 40)
    print("欢迎使用【搜索推荐系统】V1.0")
    print("")
    print("1.文章Id搜索")
    print("2.标题搜索")
    print("3.内容搜索")
    print("4.推荐搜索")
    print("")
    print("0.退出系统")
    print("=" * 40)


def searchId(id_num, db="recommend_sys_db"):
    """搜索内容"""
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "select * from " + db + " where id=?"
    results = cursor.execute(sql, (id_num,))
    results_all = results.fetchall()
    if len(results_all) != 0:
        print("找到如下文章：")
        for r in results_all:
            print("文章ID：" + str(r[0]) + "\n" + "标题：" + r[2] + "\n" + "正文：" + r[3] + "\n" + "发布日期：" + r[1])
            print("-" * 100)
    else:
        print("没有此内容的文章")
    cursor.close()
    conn.close()


def searchTitle(title, db="recommend_sys_db"):
    """搜索标题"""
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "select * from " + db + " where title like '%%%%%s%%%%'" % title
    results = cursor.execute(sql)
    results_all = results.fetchall()
    if len(results_all) != 0:
        print("找到如下文章：")
        for r in results_all:
            print(str(r[0]) + ") 标题：" + r[2] + "\n" + "正文：" + r[3][:50] + "..." + "\n" + "发布日期：" + r[1])
            print("-" * 100)
    else:
        print("没有此标题的文章")
    cursor.close()
    conn.close()


def searchContent(content, db="recommend_sys_db"):
    """搜索内容"""
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "select * from " + db + " where content like '%%%%%s%%%%'" % content
    results = cursor.execute(sql)
    results_all = results.fetchall()
    if len(results_all) != 0:
        print("找到如下文章：")
        for r in results_all:
            print("文章ID：" + str(r[0]) + "\n" + "标题：" + r[2] + "\n" + "正文：" + r[3] + "\n" + "发布日期：" + r[1])
            print("-" * 100)
    else:
        print("没有此内容的文章")
    cursor.close()
    conn.close()


def recommendContent(path, db="recommend_sys_db"):
    """搜索相似度推荐文章"""
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "select * from " + db + " where id"  # 遍历数据库所有文章
    results = cursor.execute(sql)
    results_all = results.fetchall()
    if len(results_all) != 0:
        print("正在搜索并推荐相似文章，请稍等...")
        li = []
        for r in results_all:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    compareContent = f.read()
            except Exception:
                print("请输入正确路径！")
            try:
                s1 = simHash(compareContent)
                s2 = simHash(r[3])
            except Exception as e:
                print("请将stopwords.txt文件放在  " + str(e)[28:] + "路径下！")
                break
            dis = getDistance(s1, s2)
            li.append(dis)
        a, b = [], []
        for x, y in enumerate(li):
            a.append((x, y))

        def takeSecond(elem):
            return elem[1]

        a.sort(key=takeSecond)
        for i in a[:5]:     # 推荐最相关的5篇文章，相关度由强到弱
            print("Hamming Distance：" + str(i[1]) + "(此数值越接近0相似度越高)")
            searchId(i[0] + 1)
    else:
        print("没有此内容的文章")
    cursor.close()
    conn.close()


def getDistance(hashstr1, hashstr2):
    """计算两个simhash的hamming_distance"""
    length = 0
    for index, char in enumerate(hashstr1):
        if char == hashstr2[index]:
            continue
        else:
            length += 1
    return length


def string_hash(source):
    """字符串转hash"""
    if source == "":
        return 0
    else:
        x = ord(source[0]) << 7
        m = 1000003
        mask = 2 ** 128 - 1
        for c in source:
            x = ((x * m) ^ ord(c)) & mask
        x ^= len(source)
        if x == -1:
            x = -2
        x = bin(x).replace('0b', '').zfill(64)[-64:]
        return str(x)


def simHash(content):
    seg = jieba.cut(content)
    jieba.analyse.set_stop_words('stopwords.txt')
    # jieba基于TF-IDF提取关键词
    keyWords = jieba.analyse.extract_tags("|".join(seg), topK=200, withWeight=True)
    keyList = []
    for feature, weight in keyWords:
        # 遍历分词与其对应的权重
        binstr = string_hash(feature)
        temp = []
        for c in binstr:
            weight = math.ceil(weight)
            if c == '1':
                temp.append(int(weight))
            else:
                temp.append(-int(weight))
        keyList.append(temp)
    listSum = np.sum(np.array(keyList), axis=0)
    if not keyList:
        return '00'
    simhash = ''
    for i in listSum:
        if i > 0:
            simhash = simhash + '1'
        else:
            simhash = simhash + '0'
    return simhash


def createTable():
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "create table recommend_sys_db(" \
          "id integer primary key autoincrement," \
          "date message_text," \
          "title message_text," \
          "content message_text," \
          "url message_text)"
    cursor.execute(sql)
    cursor.close()
    conn.close()
    print("新建表")


def insertData(date, title, content, url):
    u = isUrlExist(url)
    if u == 1:
        print("数据已经存在")
        return True
    else:
        conn = sqlite3.connect('crawlerNews.db')
        cursor = conn.cursor()
        sql = "insert into recommend_sys_db(date, title, content, url)" \
              "values " \
              "(?,?,?,?)"
        cursor.execute(sql, (date, title, content, url))
        conn.commit()
        cursor.close()
        conn.close()
        print("插入数据")
        return False


def deleteData(url, title, db="recommend_sys_db"):
    f = isUrlExist(url)
    if f == 0:
        print("没有要删除的数据")
        return
    else:
        conn = sqlite3.connect('crawlerNews.db')
        cursor = conn.cursor()
        sql = "delete from " + db + " where date=?"
        sql2 = "delete from " + db + " where title=?"
        results = cursor.execute(sql, (url,))
        results2 = results.execute(sql2, (title,))
        conn.commit()
        results2.close()
        conn.close()
        print("删除数据")


def isUrlExist(url, db="recommend_sys_db"):  # 判断是否存在目标数据
    conn = sqlite3.connect('crawlerNews.db')
    cursor = conn.cursor()
    sql = "select * from " + db + " where url=?"
    results = cursor.execute(sql, (url,))
    results_all = results.fetchall()
    cursor.close()
    conn.close()
    if results_all:
        return 1
    else:
        return 0


def getArticle(url):
    html = urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, features='lxml')
    publishDate = ''
    title = ''
    content = ''
    try:
        h2_title_con = soup.find_all('h2', {"class": "title_con"})
        title = h2_title_con[-1].get_text().replace("<br>", '')  # 文章标题
        if len(title) == 0:
            regTitle = r'<h2 class="title_con">(.*?)</h2>'
            urlListTitle = re.findall(regTitle, html)
            title = str(urlListTitle[0]).strip().replace("<BR>", '').replace("<P>", '').replace("</P>", '')
        else:
            pass
        div_TRS_Editor = soup.find_all('div', {"class": "TRS_Editor"})
        content = div_TRS_Editor[-1].get_text()  # 文章内容
        div_docreltime = soup.find_all('div', {"class": "docreltime"})
        div_laiyuan = soup.find_all('div', {"class": "laiyuan"})
        if len(div_docreltime) == 0:
            for m in div_laiyuan:
                publishDate = m.get_text()[5:]  # 获取文章发布日
        else:
            for m in div_docreltime:
                publishDate = m.get_text()[8:]  # 获取文章发布日
    except Exception:
        publishDate = "温馨提示：您访问的页面不存在或已删除"
        title = "温馨提示：您访问的页面不存在或已删除"
        content = "温馨提示：您访问的页面不存在或已删除"
    return publishDate, title, content


def crawl_data():
    """爬取数据并建立数据库"""
    try:
        createTable()
    except Exception as e:
        print(e)

    baseUrl = "http://www.mof.gov.cn/zhengwuxinxi/zhengcefabu/"
    x = False  # 判断是否爬取过，若爬取过则直接跳出循环
    for i in range(0, 20):
        tail = "index_" + str(i) + ".htm"
        if i == 0:
            html = urlopen(baseUrl).read().decode('utf-8')
            soup = BeautifulSoup(html, features='lxml')
            all_href = soup.find_all('a')
            for text in all_href:
                if "http://" and ".htm" in text['href']:
                    if "jiucuo.html?" not in text['href']:
                        if "mof.gov.cn" not in text['href']:
                            text['href'] = "http://www.mof.gov.cn/zhengwuxinxi/zhengcefabu" + text['href'][1:]
                            data = getArticle(text['href'])
                            x = insertData(data[0].strip(), data[1], data[2].strip(), text['href'])
                            if x is True:
                                break  # todo 应该是检查数据库是否存在
                        else:
                            data = getArticle(text['href'])
                            x = insertData(data[0].strip(), data[1], data[2].strip(), text['href'])
                            if x is True:
                                break
        else:
            if x is True:
                break
            else:
                html = urlopen(baseUrl + tail).read().decode('utf-8')
                soup = BeautifulSoup(html, features='lxml')
                all_href = soup.find_all('a')
                for text in all_href:
                    if "http://" and ".htm" in text['href']:
                        if "jiucuo.html?" not in text['href']:
                            if "mof.gov.cn" not in text['href']:
                                text['href'] = "http://www.mof.gov.cn/zhengwuxinxi/zhengcefabu" + text['href'][1:]
                                data = getArticle(text['href'])
                                x = insertData(data[0].strip(), data[1], data[2].strip(), text['href'])
                            else:
                                data = getArticle(text['href'])
                                x = insertData(data[0].strip(), data[1], data[2].strip(), text['href'])
