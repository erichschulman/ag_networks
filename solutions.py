import string
from gurobipy import *

class Solution_Parser:
	"""converts a solution into a feature"""
	
	def __init__(self, fname):
		self.fname = fname

		open_file = open(self.fname)
		file = open_file.readlines()
		self.flen =len(file)

		#save value of objective
		self.objective = float(file[1][20:-1])

		#save min store

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


def run(bands):
	for b in bands:
		test_sol(b, lambda x,y: x > y,  GRB.GREATER_EQUAL, 'store_', 'gt_max')
		test_sol(b, lambda x,y: x > y, GRB.LESS_EQUAL, 'store_', 'lt_max')
		test_sol(b, lambda x,y: x < y,  GRB.GREATER_EQUAL, 'store_', 'gt_min')
		test_sol(b, lambda x,y: x < y, GRB.LESS_EQUAL, 'store_', 'lt_min')


if __name__ == "__main__":
	run([243,49,66,69])