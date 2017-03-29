import string
import sqlite3
import requests
import os
import json
from solutions import *

class Table_Maker(Solution_Parser):

	def __init__(self, fname):
		Solution_Parser.__init__(self, fname)
		self.avg_store = None
		self.avg_farm = None
		self.avg_proc = None


	def get_extreme_2(self,ltype,compare):
		"""find the use the compare argument to find the max or min (depending on your preference).
		Yes, I think i'm clever...
		This version prevents the answer from being 0"""
		line_index = 0
		result = None, None
		while( line_index < self.flen ):
			name,price = self.parse_line(line_index,ltype)
			#print("%s: name,price - %s,%s"%(line_index,name,price))
			#print("results:%s,%s"%result)
			if(result[0] == None and name!=None):
				result = name,price
			elif((name != None and compare(price,result[1]) and price!=0) 
				or (result[1] == 0 and name!=None)):
				result = name,price 
			line_index = line_index+1
		return result


	def get_avg_store(self):
		if(self.avg_store == None):
			temp = self.sindex
			self.reset_store()
			name, price = self.next_store()
			quotient = 1
			total = 0
			while (name != None):
				total = total + price
				name, price = self.next_store()
				quotient = quotient +1
			self.sindex = temp
			self.avg_store = total/quotient
		return self.avg_store


	def get_avg_proc(self):
		if(self.avg_proc == None):
			temp = self.pindex
			self.reset_proc()
			name, price = self.next_proc()
			quotient = 1
			total = 0
			while (name != None):
				total = total + price
				name, price = self.next_proc()
				quotient = quotient +1
			self.pindex = temp
			self.avg_proc = total/quotient
		return self.avg_proc


	def get_avg_farm(self):
		if(self.avg_farm == None):
			temp = self.findex
			self.reset_farm()
			name, price = self.next_farm()
			quotient = 1
			total = 0
			while (name != None):
				total = total + price
				name, price = self.next_farm()
				quotient = quotient +1
			self.findex = temp
			self.avg_farm = total/quotient
		return self.avg_farm


	def var_store(self):
		temp = self.sindex
		self.reset_store()
		name, price = self.next_store()
		quotient = 1
		total = 0
		avg = self.get_avg_store()
		while (name != None):
			total = total + (avg - price)*(avg - price)
			name, price = self.next_store()
			quotient = quotient +1
		self.sindex = temp
		return total/quotient


	def var_proc(self):
		temp = self.pindex
		self.reset_proc()
		name, price = self.next_proc()
		quotient = 1
		total = 0
		avg = self.get_avg_proc()
		while (name != None):
			total = total + (avg - price)*(avg - price)
			name, price = self.next_proc()
			quotient = quotient +1
		self.pindex = temp
		return total/quotient


	def var_farm(self):
		temp = self.findex
		self.reset_farm()
		name, price = self.next_farm()
		quotient = 1
		total = 0
		avg = self.get_avg_farm()
		while (name != None):
			total = total + (avg - price)*(avg - price)
			name, price = self.next_farm()
			quotient = quotient +1
		self.findex = temp
		return total/quotient


def get_coord(db, name, table):
	"""return the location of this id as a point geometry"""
	query1 = None #set the query based on which table
	if (table == 'stores'):
		query1 = 'SELECT * FROM constores WHERE geoid = ?'
	elif (table == 'farms'):
		query1 = 'SELECT * FROM farms where farmid = ?'
	elif (table == 'procs'):
		query1 = 'SELECT * FROM procs where procid = ?'
	else :
		return None
	conn = sqlite3.connect(db)
	c = conn.cursor()
	c.execute(query1,(name,))
	query_result = c.fetchone()
	return query_result[1],query_result[2]


def reverse_geocode(lat,lon):
	"""reverse geocode finds the county given its lat and lon"""
	req = 'http://nominatim.openstreetmap.org/reverse?format=json&lat=%f&lon=%f&zoom=18&addressdetails=1'%(lat,lon)
	resp = requests.get(req)
	outp = json.loads(resp.text)
	return outp["address"]["county"]


def get_county(db,name,table):
	lat,lon = get_coord(db, name, table)
	return reverse_geocode(lat,lon)


def make_tables(bands,db):
	result = open('solutions/stats.txt', 'w+')
	#result.write('Band,Type,Max,Max County, Min, Min County, Average,Variance,Deviation\n')
	
	for band in bands:	
		solp = Table_Maker('solutions/solution_%s/band_%s.sol'%(band,band))

		#do the calculations for farms
		max_farm_name, max_farm = solp.get_extreme('farm_',lambda x,y: x > y)
		min_farm_name, min_farm = solp.get_extreme('farm_',lambda x,y: x < y)
		max_farm_county = get_county(db, max_farm_name, 'farms')
		min_farm_county = get_county(db, min_farm_name, 'farms')

		avg_farm = solp.get_avg_farm()
		var_farm = solp.var_farm()
		sd_farm = var_farm**(.5)
		#result.write('%s,Farms,%s,%s,%s,%s,%s,%s,%s\n'%(band,max_farm,max_farm_county,min_farm,min_farm_county,avg_farm,var_farm,sd_farm))
		
		#do calculations for stores
		max_store_name, max_store = solp.get_extreme('store_',lambda x,y: x > y)
		min_store_name, min_store = solp.get_extreme_2('store_',lambda x,y: x < y)
		max_store_county = get_county(db, max_store_name, 'stores')
		min_store_county = get_county(db, min_store_name, 'stores')

		avg_store = solp.get_avg_store()
		var_store = solp.var_store()
		sd_store = var_store**(.5)
		#result.write('%s,Store,%s,%s,%s,%s,%s,%s,%s\n'%(band,max_store,max_store_county,min_store,min_store_county,avg_store,var_store,sd_store))
		
		#finally do calcs for procs
		max_proc_name, max_proc = solp.get_extreme('proc_',lambda x,y: x > y)
		min_proc_name, min_proc = solp.get_extreme('proc_',lambda x,y: x < y)
		max_proc_county = get_county(db, max_proc_name, 'procs')
		min_proc_county = get_county(db, min_proc_name, 'procs')

		avg_proc = solp.get_avg_proc()
		var_proc = solp.var_proc()
		sd_proc = var_proc**(.5)
		#result.write('%s,Processors,%s,%s,%s,%s,%s,%s,%s\n'%(band,max_proc,max_proc_county,min_proc,min_proc_county,avg_proc,var_proc,sd_proc))
		
		result.write('\n')
		result.write('\\begin{tabular}{ |c|c|c|c|c| }\n')
		result.write('\hline  \multicolumn{5}{|c|} {Band %d} \\ \n '%band)
		result.write('\hline Type & Max & Max County& Min & Min County \\\\ \n')
		result.write('\hline Farms &%s&%s&%s&%s \\\\ \n'%(max_farm,max_farm_county,min_farm,min_farm_county))
		result.write('\hline Processors &%s&%s&%s&%s \\\\ \n'%(max_proc,max_proc_county,min_proc,min_proc_county))
		result.write('\hline Stores &%s&%s&%s&%s \\\\ \n'%(max_store,max_store_county,min_store,min_store_county))
		result.write('\hline\n')
		result.write('\end{tabular} \n')

		result.write('\n')
		result.write('\\begin{tabular}{ |c|c|c|c| }\n')
		result.write('\hline  \multicolumn{4}{|c|} {Band %d} \\ \n '%band)
		result.write('\hline Type&Average&Variance&Deviation \\\\ \n')
		result.write('\hline Farms &%s&%s&%s\\\\ \n'%(avg_farm,var_farm,sd_farm))
		result.write('\hline Processors &%s&%s&%s \\\\ \n'%(avg_proc,var_proc,sd_proc))
		result.write('\hline Stores &%s&%s&%s \\\\ \n'%(avg_store,var_store,sd_store))
		result.write('\hline\n')
		result.write('\end{tabular} \n')


	result.close()


if __name__ == "__main__":
	make_tables([243,66,69,49],'db/ag_networks2.db')