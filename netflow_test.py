from gurobipy import *


if __name__ == "__main__":
	#actually get this from the db
	nodes = ['farm1', 'farm2', 'store1', 'store2', 'store3']

	edges, costs = multidict({
		('farm1', 'store1'): 100,
		('farm1', 'store2'):  80,
		('farm1', 'store3'):  120,
		('farm2',  'store1'):   120,
		('farm2',  'store2'): 120,
		('farm2',  'store3'):  120 })

	flows = {'store1':20,
		'store2':20,
		'store3':20,
		'farm1':-30,
		'farm2':-30}

	# Create optimization model
	m = Model('transportation')

	# Create prices
	prices = m.addVars(nodes, lb=0.0, obj=flows, name="prices")

	# add arbitrage constraint constraints
	m.addConstrs( (prices[v]-prices[w]  <= costs[v,w] for v,w in edges),
 		"arbitrage")

	m.write('test.lp')

	# Compute optimal solution
	m.optimize()

	# Print solution


	if m.status == GRB.Status.OPTIMAL:
		#solution = m.getAttr('prices')
		#print(solution)
		m.write('test.sol')