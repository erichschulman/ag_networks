
CREATE TABLE farms ( 
	farmid INTEGER,
	lat REAL,
	lon REAL,
	PRIMARY KEY(farmid) 
);

CREATE TABLE proc (
 procid INTEGER,
 lat REAL,
 lon REAL,
 type TEXT,
  PRIMARY KEY(procid) 
 );

CREATE TABLE stores ( 
	storeid INTEGER,
	lat REAL,
	lon REAL,
    sqftg INTEGER,
	PRIMARY KEY(storeid)
);

CREATE TABLE fp_edges (
	farmid	INTEGER,
	procid	INTEGER,
	linedist	INTEGER,
	routdist	INTEGER,
	FOREIGN KEY(farmid) REFERENCES farms(farmid)
	FOREIGN KEY (procid) REFERENCES proc(procid)
	PRIMARY KEY(farmid, procid)
);

CREATE TABLE ps_edges (
	storeid	INTEGER,
	procid	INTEGER,
	linedist	INTEGER,
	routdist	INTEGER,
	FOREIGN KEY(storeid) REFERENCES stores(storeid)
	FOREIGN KEY (procid) REFERENCES proc(procid)
	PRIMARY KEY(storeid, procid)
);