# encoding: utf-8

from sqlite_wrapper import SQLiteWrapper


class Querier(object):
    def __init__(self, path='lianjia-xq.db'):
        self.table = 'ershou_latest'
        self.db = SQLiteWrapper(path)

    def get_ershou_by_xiaoqu(self, xiaoqu):
        sql = u'select * from {} where xiaoqu = "{}"'.format(self.table, xiaoqu)
        res = self.db.fetchall(sql)
        if len(res) > 0:
            return res
        else:
            sql = u'select * from {} where xiaoqu like "%{}%"'.format(self.table, xiaoqu)
            return self.db.fetchall(sql)


if __name__ == '__main__':
    q = Querier()
