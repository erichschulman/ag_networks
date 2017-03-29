/*calculate the varance and average size for each band*/
WITH t AS (SELECT area as val, band FROM farms)
SELECT t.band, SUM(t.val), AVG(t.val), MIN(t.val), MAX(t.val),
AVG((t.val - sub.a) * (t.val - sub.a)) AS Variance
FROM t, 
 (SELECT AVG(val) AS a, band
FROM t GROUP BY band) as sub
WHERE t.band = sub.band
GROUP BY t.band;

/*calculate the varance and average size between stores*/
SELECT AVG(constores.sqftg), MIN(constores.sqftg), MAX(constores.sqftg),
AVG((constores.sqftg - sub.a) * (constores.sqftg - sub.a))/count(constores.geoid) AS Variance 
FROM constores, 
(SELECT AVG(sqftg) AS a FROM constores) AS sub;

/*calculate variance and average for farm processor edges*/
WITH t AS 
(SELECT fp_edges.routdist AS val, farms.band AS band
FROM  farms, fp_edges
WHERE farms.farmid = fp_edges.farmid)
SELECT t.band, AVG(t.val), MIN(t.val), MAX(t.val),
AVG((t.val - sub.a) * (t.val - sub.a)) AS Variance
FROM t, 
 (SELECT AVG(val) AS a, band
FROM t GROUP BY band) as sub
WHERE t.band = sub.band
GROUP BY t.band;

/*calculate variance and average for store processor edges, the only difference between this and the query
above is the with statement*/
WITH t AS 
(SELECT ps_edges.routdist AS val, conprocs.band AS band
FROM  conprocs, ps_edges
WHERE conprocs.procid = ps_edges.procid)
SELECT t.band, AVG(t.val), MIN(t.val), MAX(t.val),
AVG((t.val - sub.a) * (t.val - sub.a)) AS Variance
FROM t, 
 (SELECT AVG(val) AS a, band
FROM t GROUP BY band) as sub
WHERE t.band = sub.band
GROUP BY t.band;

/*see how many different procs there are for each band*/
SELECT band, COUNT(*) FROM conprocs
GROUP BY band; 