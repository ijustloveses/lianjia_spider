# encoding: utf-8

import codecs
from sqlite_wrapper import SQLiteWrapper

TABLE = "xiaoqu_xuequ_mapping"


def create_mapping_table():
	command = 'create table if not exists ' + TABLE + ' (regionb TEXT key, xuequ TEXT key, school TEXT key, xiaoqu TEXT key, year int key, distance int, number int)'
	db = SQLiteWrapper(TABLE + '.db', command)
	return db


def parse_file(fname):
	"""
		解析 csv，把其中整数部分处理一下
	"""
	def str_to_int(s):
		try:
			return int(s)
		except:
			return -1

	with codecs.open(fname, 'r', 'utf-8') as fp:
		for line in fp:
			parts = line.strip('\n').strip('\r').split(',')
			if len(parts) != 7:
				if len(parts) > 0:
					print u"bad rec: {}".format(line.strip())
				continue
			parts[4] = str_to_int(parts[4])
			parts[5] = str_to_int(parts[5])
			parts[6] = str_to_int(parts[6])
			yield parts


def insert_record(db, parts):
    t = tuple(parts)
    db.execute((r"insert into " + TABLE + " values(" + ','.join(["?"] * 7) + ")", t), 1)


def workflow():
	db = create_mapping_table()
	for rec in parse_file('xq.csv'):
		insert_record(db, rec)


if __name__ == '__main__':
	workflow()
