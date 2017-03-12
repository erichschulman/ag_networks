
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

/*These views are used to make building edeges easier*/

/*This query creates a list of store edges that need to be created, using the processors 
inolved with store edges*/
CREATE VIEW conprocs AS 
SELECT procs.procid, procs.lat, procs.lon, bands.band
FROM procs, farms, bands
WHERE farms.band = bands.band AND /*associate each band with a type of produce (band)*/
(instr(procs.type, bands.name) > 0 OR instr(procs.type, 'Vegetable') > 0 OR instr(procs.type, 'Fruit'))
GROUP BY procs.procid, procs.lat, procs.lon, bands.band;


/*list possible edges between farms producers as an intermediate step before routing*/
CREATE VIEW farm_proc_bands AS
SELECT procs.procid, procs.lat, procs.lon, farms.farmid, farms.lat, farms.lon,
bands.band, bands.name, procs.type
FROM procs, farms, bands
WHERE farms.band = bands.band AND /*associate each band with a type of produce (band)*/
(instr(procs.type, bands.name) > 0 OR instr(procs.type, 'Vegetables') > 0 OR instr(procs.type, 'Fruit'));


/*list out the edges that need to be made based on what farms actually connect to intermediaries*/
CREATE VIEW ps_list AS
SELECT conprocs.procid, conprocs.lat, conprocs.lon, 
constores.geoid, constores.lat, constores.lon
FROM (SELECT conprocs.procid, conprocs.lat, conprocs.lon
FROM conprocs
GROUP BY conprocs.procid, conprocs.lat, conprocs.lon) AS conprocs , constores;

/*list out the edges that need to be made based on what farms actually connect to intermediaries
(only don't group by census tracts)*/
CREATE VIEW ps_list2 AS
SELECT conprocs.procid, conprocs.lat, conprocs.lon, 
stores.geoid, stores.lat, stores.lon
FROM (SELECT conprocs.procid, conprocs.lat, conprocs.lon
FROM conprocs
GROUP BY conprocs.procid, conprocs.lat, conprocs.lon) AS conprocs ,stores;

/*These set of queries are for building capacities in the linear program*/

/*this query returns farms and their area AS a percentage of the total*/
CREATE VIEW farm_percents AS
SELECT A.farmid, (100*area/tot) AS percent, A.band
FROM farms AS A, 
(SELECT CAST(SUM(area) AS FLOAT) AS tot, band FROM farms GROUP BY BAND) AS B
WHERE A.band = B.band;


/*this query returns stores and their area*census value (by median property value) AS percent of total*/
CREATE VIEW store_percents AS
SELECT storeid, (100*value*sqftg/tot) as tota FROM
(SELECT * FROM stores AS S, tractvalues AS T 
WHERE T.geoid = S.geoid), 
(SELECT CAST(sum(value*sqftg) AS FLOAT) as tot 
FROM stores AS S, tractvalues AS T 
WHERE T.geoid = S.geoid);


/*this query groups the stores by census district (i.e. consolidated stores)*/
CREATE VIEW constores AS 
SELECT tractvalues.geoid AS geoid, avg(stores.lat) AS lat, avg(stores.lon) AS lon, sum(stores.sqftg) AS sqftg, tractvalues.value AS value
FROM stores, tractvalues
WHERE stores.geoid = tractvalues.geoid
GROUP BY tractvalues.geoid, tractvalues.value;


/*this query returns census tracts (i.e. consolidated stores) as percent of total*/
CREATE VIEW constore_percents AS
SELECT T.geoid, T.value*T.sqftg/tot as tota
FROM constores as T, 
(SELECT CAST(sum(value*sqftg) AS FLOAT) as tot 
FROM constores);


/*I wrote these, but it turned out that they weren't useful*/


/*this query finds the min, dist between farms. It only considers edges where the
band matches the processor type. Does not return a proc id*/
CREATE VIEW fs_edges AS 
SELECT fp_edges.farmid AS farmid, ps_edges.storeid AS storeid,
MIN(fp_edges.routdist + ps_edges.routdist) AS dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid
GROUP BY fp_edges.farmid, ps_edges.storeid;


/*this query finds the min, dist between farms including proc id (may not work if using 
consolidate stores)*/
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


