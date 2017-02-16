
/*associate bands with names using input/band.txt*/
CREATE TABLE bands (
	band INTEGER,
	name TEXT,
	PRIMARY KEY(band)
);


/*import tract values for census*/
CREATE TABLE tractvalues (
	geoid INTEGER,
	value INTEGER,
	PRIMARY KEY(geoid)
);


/*initialize farms*/
CREATE TABLE farms ( 
	farmid INTEGER,
	lat REAL,
	lon REAL,
	area INTEGER,
	band INTEGER,
	PRIMARY KEY(farmid)
	FOREIGN KEY (band) REFERENCES bands(band)
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
    geoid INTEGER,
	PRIMARY KEY(storeid)
	FOREIGN KEY (geoid) REFERENCES tract_values(geoid)
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