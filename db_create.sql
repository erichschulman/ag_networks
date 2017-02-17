
/*Associate bands with names using input/band.txt*/
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


/*this query returns farms and their area AS a percentage of the total*/
CREATE VIEW farm_percents AS
SELECT A.farmid, (100*area/tot) AS percent, A.band
FROM farms AS A, 
(SELECT CAST(SUM(area) AS FLOAT) AS tot, band FROM farms GROUP BY BAND) AS B
WHERE A.band = B.band;


/*this query returns stores and their area*census value (by median property value) AS percent of total*/
CREATE VIEW store_percents AS
SELECT storeid, (100*value*sqftg/tot) AS percent
FROM
(SELECT * FROM stores AS S, tractvalues AS T
WHERE T.geoid = S.geoid),
(SELECT CAST(sum(value*sqftg) AS FLOAT) AS tot
FROM stores AS S, tractvalues AS T);


/*this query finds the min, dist between farms without proc id*/
CREATE VIEW fs_edges AS 
SELECT fp_edges.farmid AS farmid, ps_edges.storeid AS storeid,
MIN(fp_edges.routdist + ps_edges.routdist) AS dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid
GROUP BY fp_edges.farmid, ps_edges.storeid;


/*this query finds the min, dist between farms including proc id*/
CREATE VIEW fps_edges AS 
SELECT  A.storeid, A.farmid, B.procid, B.fp_dist, B.ps_dist
FROM
(SELECT fp_edges.farmid AS farmid, ps_edges.storeid AS storeid,
MIN(fp_edges.routdist + ps_edges.routdist) AS dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid
GROUP BY fp_edges.farmid, ps_edges.storeid) AS A,
(SELECT fp_edges.farmid AS farmid, ps_edges.storeid AS storeid, 
fp_edges.procid AS procid, fp_edges.routdist + ps_edges.routdist AS dist,
fp_edges.routdist AS fp_dist, ps_edges.routdist AS ps_dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid) AS B
WHERE A.storeid = B.storeid AND A.farmid = B.farmid AND A.dist = B.dist;
