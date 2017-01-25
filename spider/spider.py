# encoding: utf-8

# import urllib2
import requests
from sqlite_wrapper import SQLiteWrapper
import random
# import threading
from bs4 import BeautifulSoup as BS
import time
from xiaoqu_xuequ_query import Querier

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

################
#
#    基础
#
################


def gen_insert_command(info_dict, info_list, table, partial=False):
    t = [info_dict.get(i, '') for i in info_list]
    t = tuple(t)
    if partial:
        return (r"insert into {}({}) values(".format(table, ','.join(info_list)) + ','.join(["?"] * len(info_list)) + ")", t)
    else:
        return (r"insert into {} values(".format(table) + ','.join(["?"] * len(info_list)) + ")", t)


def url_to_soup(url_page):
    try:
        """
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code, 'utf-8')
        soup = BS(plain_text, "html.parser")
        """
        # r = requests.get(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        r = requests.get(url_page)
        r.encoding = 'utf-8'
        soup = BS(r.text, "html.parser")
        return soup
    except Exception, e:
        print e
        exit(-1)


def str_to_int(s):
    try:
        return int(s)
    except:
        return -1


################
#
#    小区: 根据指定的 regions (大区) 来获取对应大区中的所有小区
#
################


def gen_xiaoqu_insert_command(info_dict):
    info_list=[u'url', u'小区名称', u'大区域', u'小区域']
    return gen_insert_command(info_dict, info_list, 'xiaoqu')


def get_xiaoqu_list(url_page=u"http://bj.lianjia.com/xiaoqu/pg1rs%E6%98%8C%E5%B9%B3/"):
    """
    从分页中的一页，取出页面中列出的全部小区信息
    """
    soup = url_to_soup(url_page)
    xiaoqu_list = soup.findAll('li', {'class': 'xiaoquListItem'})
    for xq in xiaoqu_list:
        info_dict = {}
        info_dict.update({u'url': xq.find('div', {'class': 'title'}).find('a').get('href')})
        info_dict.update({u'小区名称': xq.find('div', {'class': 'title'}).find('a').text})
        info_dict.update({u'大区域': xq.find('div', {'class': 'positionInfo'}).find('a', {'district'}).text})
        info_dict.update({u'小区域': xq.find('div', {'class': 'positionInfo'}).find('a', {'bizcircle'}).text})
        yield info_dict


def xiaoqu_spider(db_xq, url_page):
    """ 把单个分页页面中的小区入库 """
    for info_dict in get_xiaoqu_list(url_page):
        command = gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command, 1)


def do_xiaoqu_spider(db_xq, region=u"海淀"):
    """ 给定区域，获取全部分页，然后对所有页面获取小区信息 """
    url = u"http://bj.lianjia.com/xiaoqu/rs" + region + u"/"
    soup = url_to_soup(url)

    d = 'd=' + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    # 此时， d = "d={'totalPage': 56, 'curPage': 1}"，exec(d) 就相当于 eval 这个字符，转为 python 运行
    # 更直观的做法是使用 json
    exec(d)
    total_pages = d['totalPage']
    print "total pages: {}".format(total_pages)

    # threads = []
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/xiaoqu/pg{}rs{}/".format(i + 1, region)
        time.sleep(2 + random.randint(2, 10))
        xiaoqu_spider(db_xq, url_page)
    """
        t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    """


def rebuild_xiaoqu_db():
    print "creating lianjia-xq.db ..."
    command = 'create table if not exists xiaoqu (url TEXT UNIQUE, name TEXT primary key UNIQUE, regionb TEXT, regions TEXT)'
    db_xq = SQLiteWrapper('lianjia-xq.db', command)

    regions=[u"西城", u"海淀", u"东城"]
    # regions=[u"东城"]
    for region in regions:
        print u"starting to crawl xiaoqu in region: {}".format(region)
        do_xiaoqu_spider(db_xq, region)
    print "xiaoqu spider done !"


################
#
#    二手: 根据给定 xuequ 来获取全部学区对应所有小区的二手房信息
#    和上面根据大区查小区不同，这里会有可能在列表页中没有 pager 甚至没有任何记录
#    另外，上面查小区，这个基本不变化，不需要频繁更新，而这里就不同了，需要频繁更新！  删除 TODO
#
################


def gen_ershou_insert_command(info_dict, table, partial=False):
    info_list=[u'url', u'title', u'info', u'floor', u'history', u'tag', u'pricestr', u'price', u'unit', u'xiaoqu']
    return gen_insert_command(info_dict, info_list, table, partial=partial)


def get_ershou_list(url_page, xiaoqu):
    """
    从某个小区的单个分页页面获取全部在售二手房数据，页面 url like http://bj.lianjia.com/ershoufang/c1111027382209/
    """
    soup = url_to_soup(url_page)
    try:
        lists = soup.find('ul', {'class': 'sellListContent'}).findAll('li')
    except:
        # 没有任何记录
        lists = []
    for item in lists:
        info_dict = {}
        titlelink = item.find('div', {'class': 'title'}).find('a')
        info_dict['url'] = titlelink.get('href')
        info_dict['title'] = titlelink.text
        info_dict['info'] = item.find('div', {'class': 'houseInfo'}).text
        info_dict['floor'] = item.find('div', {'class': 'positionInfo'}).text
        info_dict['history'] = item.find('div', {'class': 'followInfo'}).text
        info_dict['tag'] = ' | '.join(map(lambda x: x.text, item.find('div', {'class': 'tag'}).findAll('span')))
        info_dict['pricestr'] = item.find('div', {'class': 'priceInfo'}).find('div', {'class': 'totalPrice'}).text
        info_dict['price'] = str_to_int(info_dict['pricestr'][: -1])
        info_dict['unit'] = item.find('div', {'class': 'priceInfo'}).find('div', {'class': 'unitPrice'}).text
        info_dict['xiaoqu'] = xiaoqu
        yield info_dict


def ershou_spider(db_xq, url_page, xiaoqu):
    """ 把单个分页页面中的在售二手入库 """
    for info_dict in get_ershou_list(url_page, xiaoqu):
        command = gen_ershou_insert_command(info_dict, 'ershou', partial=True)
        db_xq.execute(command, 1)
        command = gen_ershou_insert_command(info_dict, 'ershou_latest', partial=False)
        db_xq.execute(command, 1)


def do_ershou_spider_by_xiaoqu(db_xq, xiaoqu_id, xiaoqu):
    """ 给定区域，获取全部分页，然后对所有页面获取小区信息 """
    url = "http://bj.lianjia.com/ershoufang/" + xiaoqu_id + "/"
    soup = url_to_soup(url)

    try:
        d = 'd=' + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
        exec(d)
        total_pages = d['totalPage']
    # 没有 pager
    except:
        total_pages = 1
    print "total pages for {}: {}".format(xiaoqu_id, total_pages)

    # 先从 ershou_latest 表中清除该小区数据，然后导入
    command = u'delete from ershou_latest where xiaoqu = "{}"'.format(xiaoqu)
    db_xq.execute(command)
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/ershoufang/pg{}{}/".format(i + 1, xiaoqu_id)
        time.sleep(2 + random.randint(4, 9))
        ershou_spider(db_xq, url_page, xiaoqu)


def get_xiaoqu_by_xuequ(db_xq, xuequ):
    q = Querier()
    for regionb, xuequ, school, xiaoqu, year, distance, number in q.query_xuequ(xuequ):
        # 可能会有同名小区的，会返回多个
        xiaoqu = xiaoqu.decode('utf-8')
        sql = u'select url from xiaoqu where name = "{}"'.format(xiaoqu)
        for url in db_xq.fetchall(sql):
            # http://bj.lianjia.com/xiaoqu/1115056607153512/
            print u"-------- {} -----------".format(xiaoqu)
            # 加前缀 c
            yield (xiaoqu, 'c' + url[0].strip('/').split('/')[-1])


def run_ershoufang_info():
    print "creating ershou table in lianjia-xq.db ..."
    command = "create table if not exists ershou (url TEXT primary key UNIQUE, title TEXT, info TEXT, floor TEXT, history TEXT, tag TEXT,  pricestr TEXT, price int, unit TEXT, xiaoqu TEXT, created timestamp not null default (datetime('now', 'localtime')))"
    db_xq = SQLiteWrapper('lianjia-xq.db', command)
    command = 'create table if not exists ershou_latest (url TEXT primary key UNIQUE, title TEXT, info TEXT, floor TEXT, history TEXT, tag TEXT,  pricestr TEXT, price int, unit TEXT, xiaoqu TEXT)'
    db_xq.execute(command)

    # start = False
    xuequs = [u'东四、朝阳门、建国门学区', u'和平里学区', u'北新桥、东直门学区', u'德胜学区', u'月坛学区', u'什刹海学区', u'展览路学区']
    for xuequ in xuequs:
        for xiaoqu, xiaoqu_id in get_xiaoqu_by_xuequ(db_xq, xuequ):
            # if xiaoqu_id != 'c1111027374577' and start == False:
            #     continue
            # if xiaoqu_id == 'c1111027374577':
            #    start = True
            do_ershou_spider_by_xiaoqu(db_xq, xiaoqu_id, xiaoqu)


if __name__ == '__main__':
    # rebuild_xiaoqu_db()
    run_ershoufang_info()
