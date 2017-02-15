from farms import *
from edges import *
from stores import *

def main():
	import_proc("db/test.db","input/ptest.csv")
	import_store("db/test.db","input/stest.csv")
	import_farms('input/test.tif',36,10)
	#proc_edges("db/test.db")
	#proc_edges("db/test.db", farms = True )
	#fp_edges("db/test.db")
	return

if __name__ == "__main__":
	main()