# -*- coding: utf-8 -*-

import unittest, time, json
import requests, pymssql

class ItemQuery():
	def __init__(self):
		self.list_url = 'http://122.112.200.198:8686/chahuo_list/'
		self.result_url = 'http://122.112.200.198:8686/chahuo_result/'
		self.company = 'dongnam'
		self.com_sn = 'dongnam'
		self.sql = """
			SELECT I.cInvName, C.cBatch, C.iQuantity
			FROM  CurrentStock AS C
			JOIN Inventory as I ON I.cInvCode = C.cInvCode
			where I.cInvName like '{}'
			"""
		self.client = pymssql.connect(host='192.168.5.250', user='sa', password='', port=1433, database='UFDATA_002_2018', charset='utf8')	
		self.cur = self.client.cursor()		
		self.flag = True
		self.ses = requests.Session()

	def test_chahuo(self):
		print('--------------------start---------------------------')
		while(self.flag):
			try:
				# self.ses = requests.Session()	
				res = self.ses.post(self.list_url, data = {'c':self.company, 'sn':self.com_sn})
				if res.status_code == 200:
					if res.headers['content-type'] == 'application/json':
						rjson = res.json(encoding='utf8')
						# print('res.json:', rjson)
						for r in rjson:
							# print('type of r: ', type(r))
							model = r.get('model', None)
							pk = r.get('pk', None)
							fields = r.get('fields', None)
							if model != None and pk != None and fields != None:
								print('------sql search-----')
								keyword = fields.get('item')
								q_quantity = fields.get('q_quantity')
								self.cur.execute(self.sql.format(keyword))
								results = self.cur.fetchall()
								if len(results) == 0:
									fields['result_status'] = 0				
								else:
									# print('result from db:', results)
									fields['result_status'] = 1
									maxn = results[0][2]
									for t in results:
										if t[2] >= q_quantity:
											fields['result_status'] = 2
										if t[2] > maxn:
											maxn = t[2]
									fields['s_quantity'] = int(maxn)	
								print('fields from db, then post it back:', fields)
								self.ses.post(self.result_url, data = fields)

				time.sleep(0.3)
				# a = input('Do you want to continue posting. Y/N? ')
				# if a.upper() == 'N':
				# 	self.flag = False
			except:
				print('something is wrong.')
				pass
				

if __name__ == '__main__':
	iq = ItemQuery()
	iq.test_chahuo()
	iq.client.close()