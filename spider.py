# encoding: utf-8

import re
import urllib2
from sqlite_wrapper import SQLiteWrapper
import random
import threading
from bs4 import BeautifulSoup as BS

hds=[{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
     {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
     {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
     {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
     {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},
     {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
     {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
     {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
     {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
     {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
     {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
     {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
     {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}
]

regions=[u"东城", u"西城", u"海淀"]

lock = threading.Lock()


def gen_insert_command(info_dict, info_list, table):
    t = [info_dict.get(i, '') for i in info_list]
    t = tuple(t)
    return (r"insert into {} values(?, ?, ?, ?, ?)".format(table), t)


def gen_xiaoqu_insert_command(info_dict):
    info_list=[u'小区名称', u'大区域', u'小区域', u'小区户型', u'建造时间']
    return gen_insert_command(info_dict, info_list, 'xiaoqu')


def gen_chengjiao_insert_command(info_dict):
    info_list=[u'链接', u'小区名称', u'户型', u'面积', u'朝向', u'楼层', u'建造时间', u'签约时间', u'签约单价', u'签约总价', u'房产类型', u'学区', u'地铁']
    return gen_insert_command(info_dict, info_list, 'chengjiao')


# 单页中全部小区
def get_xiaoqu_list(url_page=u"http://bj.lianjia.com/xiaoqu/pg1rs%E6%98%8C%E5%B9%B3/"):
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code, errors='ignore')
        soup = BS(plain_text, "html.parser")
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exit(-1)
    except Exception, e:
        print e
        exit(-1)

    xiaoqu_list = soup.findAll('div', {'class': 'info-panel'})
    for xq in xiaoqu_list:
        info_dict = {}
        info_dict.update({u'小区名称': xq.find('a').text})
        content=unicode(xq.find('div', {'class': 'con'}).renderContents().strip())
        info=re.match(r".+>(.+)</a>.+>(.+)</a>.+</span>(.+)<span>.+</span>(.+)", content)
        if info:
            info = info.group()
            info_dict.update({u'大区域': info[0]})
            info_dict.update({u'小区域': info[1]})
            info_dict.update({u'小区户型': info[2]})
            info_dict.update({u'建造时间': info[3][:4]})
        yield info_dict


# 单页中全部小区
def xiaoqu_spider(db_xq, url_page):
    for info_dict in get_xiaoqu_list(url_page):
        command = gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command, 1)


# 区域所有页面中的全部小区
def do_xiaoqu_spider(db_xq, region=u"海淀"):
    url=u"http://bj.lianjia.com/xiaoqu/rs" + region + "/"
    try:
        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=5).read()
        plain_text=unicode(source_code, errors='ignore')
        soup = BS(plain_text, "html.parser")
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return
    except Exception, e:
        print e
        return

    d = 'd=' + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    exec(d)
    total_pages = d['totalPage']

    threads = []
    for i in range(total_pages):
        url_page=u"http://bj.lianjia.com/xiaoqu/pg%drs%s/" % (i + 1, region)
        t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print "xiaoqu spider done !"


if __name__ == '__main__':
    command = 'create table if not exists xiaoqu (name TEXT primary key UNIQUE, regionb TEXT, regions TEXT, style TEXT, year TEXT)'
    db_xq = SQLiteWrapper('lianjia-xq.db', command)

    command = 'create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,fangchan_class TEXT, school TEXT, subway TEXT)'
    db_cj = SQLiteWrapper('lianjia-cj.db', command)

    for region in regions:
        do_xiaoqu_spider(db_xq, region)
