
/*initialize farms*/
CREATE TABLE farms ( 
	farmid INTEGER,
	lat REAL,
	lon REAL,
	area INTEGER,
	band INTEGER,
	PRIMARY KEY(farmid) 
);


/*initialize intermediaries (processors)*/
CREATE TABLE procs (
 procid INTEGER,
 lat REAL,
 lon REAL,
 type TEXT,
 PRIMARY KEY(procid) 
 );


/*initialize stores*/
CREATE TABLE stores ( 
	storeid INTEGER,
	lat REAL,
	lon REAL,
    sqftg INTEGER,
	PRIMARY KEY(storeid)
);


/*initialize farm to processor edges*/
CREATE TABLE fp_edges (
	farmid	INTEGER,
	procid	INTEGER,
	routdist	INTEGER,
	FOREIGN KEY(farmid) REFERENCES farms(farmid)
	FOREIGN KEY (procid) REFERENCES proc(procid)
	PRIMARY KEY(farmid, procid)
);

/*store processor edges*/
CREATE TABLE ps_edges (
	storeid	INTEGER,
	procid	INTEGER,
	routdist	INTEGER,
	FOREIGN KEY(storeid) REFERENCES stores(storeid)
	FOREIGN KEY (procid) REFERENCES proc(procid)
	PRIMARY KEY(storeid, procid)
);

/*farm store edges (see other sql file)*/
CREATE TABLE fs_edges (
	storeid	INTEGER,
	procid	INTEGER,
	linedist	INTEGER,
	routdist	INTEGER,
	FOREIGN KEY(storeid) REFERENCES stores(storeid)
	FOREIGN KEY (procid) REFERENCES proc(procid)
	PRIMARY KEY(storeid, procid)
);

