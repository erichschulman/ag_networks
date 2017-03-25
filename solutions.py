import string
import os
from gurobipy import *

class Solution_Parser:
	"""converts a solution into a feature"""
	
	def __init__(self, fname):
		self.fname = fname

		self.avg_store = None
		self.avg_farm = None
		self.avg_proc = None

		open_file = open(self.fname)
		file = open_file.readlines()
		self.flen =len(file)

		#save value of objective
		self.objective = float(file[1][20:-1])

		#initial values (i.e. first one in solution file)	
		self.farm1 =0
		for line in file:
			if(string.find(line,'farm_')>-1):
				break
			self.farm1 = self.farm1+1

		self.store1 = 0
		for line in file:
			if(string.find(line,'store_')>-1):
				break
			self.store1 = self.store1+1

		self.proc1 = 0
		for line in file:
			if(string.find(line,'proc_')>-1):
				break
			self.proc1 = self.proc1+1
		
		#initial indexes
		self.sindex = self.store1
		self.findex = self.farm1
		self.pindex = self.proc1


	def parse_line(self, line_index, ltype):
		"""use this to parse a line in the solution file"""
		open_file = open(self.fname)
		file = open_file.readlines()
		
		if(line_index < self.flen):
			line = file[line_index]
			index = string.find(line, ltype)
			if index > -1:
				index2 = string.find(line, ' ')
				name = int(line[index+len(ltype):index2])
				price = float(line[1+index2:-1])
				return name,price
		return None, None

	
	def next_store(self):
		"""return the next store in the solution file with geoid, price"""
		result = self.parse_line(self.sindex,'store_')
		self.sindex = self.sindex + 1
		return result


	def next_farm(self):
		"""return the next farm in solution file with farmid, price"""
		result = self.parse_line(self.findex,'farm_')
		self.findex = self.findex + 1
		return result


	def next_proc(self):
		"""return the next proc in the solution file with procid, price"""
		result = self.parse_line(self.pindex,'proc_')
		self.pindex = self.pindex + 1
		return result


	def reset_store(self):
		"""rest to the first store"""
		self.sindex = self.store1


	def reset_farm(self):
		"""reset to the first farm"""
		self.findex = self.farm1


	def reset_proc(self):
		"""reset to the first proc"""
		self.pindex = self.proc1

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
		

	def get_extreme(self,ltype,compare):
		"""find the use the compare argument to find the max or min (depending on your preference).
		Yes, I think i'm clever..."""
		line_index = 0
		result = None, None
		while( line_index < self.flen ):
			name,price = self.parse_line(line_index,ltype)
			#print("%s: name,price - %s,%s"%(line_index,name,price))
			#print("results:%s,%s"%result)
			if(result[0] == None):
				result = name,price
			elif(name != None and compare(price,result[1])):
				result = name,price 
			line_index = line_index+1
		return result


def test_sol(band, compare, sense, ltype, descrip):	
	"""use this to test whether the maximum price is flexible"""
	m = read('solutions/solution_%d/band_%d.lp'%(band,band))

	#add a constraint for complimentary slackness i.e. value of objective function
	filename = 'solutions/solution_%d/band_%d.sol'%(band,band)
	solp = Solution_Parser(filename)
	m.addConstr(m.getObjective() <= solp.objective, "extra_1")

	#add a constraint to test the max value
	name,price = solp.get_extreme(ltype,compare)
	new_var = m.getVarByName(ltype+str(name))

	m.addConstr( new_var, sense, price , "extra_2")

	m.write('solutions/solution_%d/%s_%d.lp'%(band, descrip, band) )
	m.optimize()
	# Print solution
	if m.status == GRB.Status.OPTIMAL:
		m.write('solutions/solution_%d/%s_%d.sol'%(band, descrip, band))


def general_parse_line(line):
	"""a second line parsing helper, for comparing files"""
	index = string.find(line, ' ')
	name,price = None,None
	if(index > -1):
		name = line[:index]
		price = float(line[1+index:-1])
	return name,price


def compare_sol_helper(fname1,fname2,output):
	"""helper that actuall does the comparisons between solution files
	essential ignores differences that are below """
	open_file1 = open(fname1)
	file1 = open_file1.readlines()
		
	open_file2 = open(fname2)
	file2 = open_file2.readlines()
	
	result = open(output+'.csv', 'w+')

	obj1= float(file1[1][20:-1])
	obj2 = float(file1[1][20:-1])

	result.write( 'Objective 1,%f,Objective 2,%f\n\n'%(obj1,obj2) )
	result.write('Name 1,Price 1,Name 2,Price 2\n')
	for line1 in file1[2:]:
		found = False
		name1, price1 = general_parse_line(line1)
		for line2 in file2[2:]:
			name2, price2 = general_parse_line2(line2)
			if ( name1 == name2):
				found = True
				if(price1 != price2):
					result.write("%s,%f,%s,%f \n"%(name1,price1,name2,price2) )
				break

		if(not found):
			result.write("%s,%f,None,None\n"%(name1,price1))
	result.close()


def compare_sol(band):
	"""use this to compare the solution files for each band"""
	band_directory = 'solutions/solution_%d/'%band
	band_solution = 'band_%d.sol'%band

	for file in os.listdir(band_directory):
		if file.endswith(".sol") and file != band_solution:
			print("Starting on %s..."%file)
			output_name = band_directory + file[:-4]
			compare_sol_helper(band_directory + band_solution, band_directory + file, output_name)


def run(bands):
	"""helper function with the relevant checks I want to run against the lp"""
	for b in bands:
		test_sol(b, lambda x,y: x > y,  GRB.GREATER_EQUAL, 'store_', 'gt_max')
		test_sol(b, lambda x,y: x > y, GRB.LESS_EQUAL, 'store_', 'lt_max')
		test_sol(b, lambda x,y: x < y,  GRB.GREATER_EQUAL, 'store_', 'gt_min')
		test_sol(b, lambda x,y: x < y, GRB.LESS_EQUAL, 'store_', 'lt_min')
		compare_sol(b)


def stats(bands):
	result = open('solutions/stats.csv', 'w+')
	result.write('Band,Type,Max,Min,Average,Variance,Deviation\n')
	
	for band in bands:	
		solp = Solution_Parser('solutions/solution_%s/band_%s.sol'%(band,band))

		#do the calculations for farms
		max_farm = solp.get_extreme('farm_',lambda x,y: x > y)[1]
		min_farm = solp.get_extreme('farm_',lambda x,y: x < y)[1]
		avg_farm = solp.get_avg_farm()
		var_farm = solp.var_farm()
		sd_farm = var_farm**(.5)
		result.write('%s,Farms,%s,%s,%s,%s,%s\n'%(band,max_farm,min_farm,avg_farm,var_farm,sd_farm))
		
		#do calculations for stores
		max_store = solp.get_extreme('store_',lambda x,y: x > y)[1]
		min_store = solp.get_extreme('store_',lambda x,y: x < y)[1]
		avg_store = solp.get_avg_store()
		var_store = solp.var_store()
		sd_store = var_store**(.5)
		result.write('%s,Store,%s,%s,%s,%s,%s\n'%(band,max_store,min_store,avg_store,var_store,sd_store))
		
		#finally do calcs for procs
		max_proc = solp.get_extreme('proc_',lambda x,y: x > y)[1]
		min_proc = solp.get_extreme('proc_',lambda x,y: x > y)[1]
		avg_proc = solp.get_avg_proc()
		var_proc = solp.var_proc()
		sd_proc = var_proc**(.5)
		result.write('%s,Processors,%s,%s,%s,%s,%s\n'%(band,max_proc,min_proc,avg_proc,var_proc,sd_proc))

	result.close()





if __name__ == "__main__":
	stats([243,66,69,49])