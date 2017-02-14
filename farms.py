import sqlite3

def test():
	conn1 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	conn2 = sqlite3.connect('db/test.db', isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()
	i = 1
	for row in c2.execute('SELECT * FROM proc'):
		print(row)
		i = i+1
		c1.execute('INSERT INTO stores VALUES (?,?,?,?)', (20+i,20,20,20,) )
	conn1.commit()

if __name__ == "__main__":
	test()