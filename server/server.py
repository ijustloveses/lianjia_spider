# encoding=utf-8
from bottle import route, run, request, response, default_app
import sys
sys.path.append('../spider/')
from xiaoqu_xuequ_query import Querier
from info_query import Querier as InfoQuerier
import json


@route('/regionb')
def regionb():
    response.set_header('Access-Control-Allow-Origin', '*')
    return u'{"regionb": ["西城", "东城"]}'


@route('/xuequ')
def xuequ():
    regionb = request.query.regionb
    response.set_header('Access-Control-Allow-Origin', '*')
    if regionb == u'西城':
        return u'{"xuequ": ["德胜学区", "月坛学区", "什刹海学区", "展览路学区"]}'
    elif regionb == u'东城':
        return u'{"xuequ": ["东四、朝阳门、建国门学区", "和平里学区", "北新桥、东直门学区"]}'
    else:
        return u'{"xuequ": []}'


@route('/xiaoqu')
def xiaoqu():
    xuequ = request.query.xuequ
    q = Querier('../spider/xiaoqu_xuequ_mapping.db')
    xiaoqu = []
    for xq in q.query_xuequ(xuequ):
        xiaoqu.append(xq[3])
    response.set_header('Access-Control-Allow-Origin', '*')
    return u'{"xiaoqu": [' + u','.join([u'"{}"'.format(xq.decode('utf-8')) for xq in xiaoqu]) + u']}'


@route('/ershou')
def ershou():
    xiaoqu = request.query.xiaoqu
    q = InfoQuerier('../spider/lianjia-xq.db')
    ershou = []
    for url, title, info, floor, history, tag, pricestr, _, unit, _ in q.get_ershou_by_xiaoqu(xiaoqu):
        ershou.append([title, info, floor, history, tag, pricestr, unit, url])
    response.set_header('Access-Control-Allow-Origin', '*')
    return json.dumps({"ershou": ershou})


app = default_app()

if __name__ == '__main__':
    run(host='0.0.0.0', port=80, debug=True, reloader=False)
