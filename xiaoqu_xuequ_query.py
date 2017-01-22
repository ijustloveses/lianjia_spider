# encoding: utf-8

from sqlite_wrapper import SQLiteWrapper

class Querier(object):
	def __init__(self, path='xiaoqu_xuequ_mapping.db'):
		self.table = 'xiaoqu_xuequ_mapping'
		self.db = SQLiteWrapper(path)
		self.fields = [u'区', u'学区', u'学校', u'小区', u'建筑年份', u'距学校距离', u'对口楼栋数']
	
	def query_school(self, school):
		sql = u'select * from {} where school = "{}"'.format(self.table, school)
		res = self.db.fetchall(sql)
		if len(res) > 0:
			return res
		else:
			sql = u'select * from {} where school like "%{}%"'.format(self.table, school)
			return self.db.fetchall(sql) 
			
	def query_xiaoqu(self, xiaoqu):
		sql = u'select * from {} where xiaoqu = "{}"'.format(self.table, xiaoqu)
		res = self.db.fetchall(sql)
		if len(res) > 0:
			return res
		else:
			sql = u'select * from {} where xiaoqu like "%{}%"'.format(self.table, xiaoqu)
			return self.db.fetchall(sql)

	def query_xuequ(self, xuequ):
		sql = u'select * from {} where xuequ = "{}"'.format(self.table, xuequ)
		res = self.db.fetchall(sql)
		if len(res) > 0:
			return res
		else:
			sql = u'select * from {} where xuequ like "%{}%"'.format(self.table, xuequ)
			return self.db.fetchall(sql)


if __name__ == '__main__':
	q = Querier()
	print "------------------------------"
	print q.query_xiaoqu(u'椿树园')
	print "------------------------------"
	print q.query_xiaoqu(u'椿树')
	print "------------------------------"
	print q.query_school(u'北京第一实验小学')
	print "------------------------------"
	print q.query_xuequ(u'德胜')
