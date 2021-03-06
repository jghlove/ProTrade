#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#
# Copyright 2017 XavierXia(xiawenxing2010@163.com).
#
# Licensed under GNU General Public License, Version 3.0 (the "License");

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

import tushare as ts
import json

'''
SAVE
http://localhost/md?p=s&p=stock&p=600000&p=D&p=qfq&p=kNil&p=kNil&p=False
Introductions:
	1: action(like:save,get,add,delete,...)
   	2: type, 
   	3: code, 
   	4: stock cycle data(like:M,W,D,60,30,15,5)
   	5: qfq-前复权 hfq-后复权 None-不复权，默认为qfq
   	6: 开始日期 format：YYYY-MM-DD 为空时取当前日期
   	7. 结束日期 format：YYYY-MM-DD
   	8. 是否为指数：默认为False,设定为True时认为code为指数代码
GET
http://localhost/md?p=g&p=stock&p=600000&p=D&p=qfq&p=kNil&p=kNil&p=False
'''
class ManageDataHandler(tornado.web.RequestHandler):
	'''
	def __init__(self):
		self.argsData= {}
		self.arr = ["action","type","code","ktype","autype","start","end","index"]
		self.logger = self.application.logger
		self.logger.info("ManageDataHandler init....")
	'''
	def get(self):

		self.argsData= {}
		self.arr = ["action","type","code","ktype","autype","start","end","index"]
		self.logger = self.application.logger
		self.logger.info("ManageDataHandler init....")

		args = self.get_arguments("p")
		self.logger.info("request args....%s",args)
		self.parseArg(args)
		self.logger.info("self.argsData: %s",self.argsData)

		stockColl = self.application.db.stock
		#self.write({"hao":"111"})
		if self.argsData['action'] == 's':
			self.dealSave(stockColl)
		elif self.argsData['action'] == 'g':
			self.dealGet(stockColl)


	def dealSave(self, stockColl):
		code = self.argsData['code']
		#获取和保存全部历史数据
		if self.argsData['start'] == 'kNil' and self.argsData['end'] == 'kNil':

			sData = ts.get_k_data(code,ktype=self.argsData['ktype'])
			sData = json.loads(sData.to_json(orient='records'))
			self.logger.info("fetch all history data...")

			stockColl.insert({"dCode":code,"dktype":self.argsData['ktype']})
			stockColl.update({"dCode":code,"dktype":self.argsData['ktype']},{"$push":{"dData":{"$each":sData}}})
		#只获取当天的数据
		elif self.argsData['start'] != 'kNil' or self.argsData['end'] != 'kNil':
			sData = ts.get_k_data(code,ktype=self.argsData['ktype'])
			sData = json.loads(sData.to_json(orient='records'))

			self.logger.info("fetch realtime data...")
			stockColl.update({"dCode":code,"dktype":self.argsData['ktype']},{"$push":{"dData":{"$each":sData}}})
		
		for doc in stockColl.find():
			del doc['_id']
		self.write(stockColl)

	def dealGet(self, stockColl):
		code = self.argsData['code']
		doc = stockColl.find({"dCode":code,"dktype":self.argsData['ktype']},{"dData":1,"_id":0})
		self.logger.info("doc: %s",doc)
		#self.write(doc['dData'])
		
	def parseArg(self, args):
		if len(args) == 8:
			for i, v in enumerate(args):
				self.argsData[self.arr[i]] = v
		else:
			self.logger.warn("input args error!")
