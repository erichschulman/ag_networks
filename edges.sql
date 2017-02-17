
/*these queries are meant to be run after the database is loaded inorder to do the optimization problem*/

/*this query returns farms and their area as a percentage of the total*/
SELECT farmid, (100*area/tot) as tota FROM
farms, (SELECT CAST(SUM(area) as FLOAT) as tot FROM farms);


/*this query returns stores and their area*census value (by median property value) as percent of total*/
SELECT storeid, (100*value*sqftg/tot) as tota 
FROM
(SELECT * FROM stores AS S, tractvalues AS T
WHERE T.geoid = S.geoid),
(SELECT CAST(sum(value*sqftg) AS FLOAT) as tot
FROM stores AS S, tractvalues AS T


/*this query finds the min, dist between farms including proc id*/
SELECT  A.storeid, A.farmid, B.procid, A.dist
FROM
(SELECT fp_edges.farmid as farmid, ps_edges.storeid as storeid,
MIN(fp_edges.routdist + ps_edges.routdist) as dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid
GROUP BY fp_edges.farmid, ps_edges.storeid) as A,
(SELECT fp_edges.farmid as farmid, ps_edges.storeid as storeid, 
fp_edges.procid as procid, fp_edges.routdist + ps_edges.routdist as dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid) as B
WHERE A.storeid = B.storeid AND A.farmid = B.farmid AND A.dist = B.dist;


/*this query finds the min, dist between farms without proc id*/
SELECT fp_edges.farmid as farmid, ps_edges.storeid as storeid,
MIN(fp_edges.routdist + ps_edges.routdist) as dist
FROM ps_edges, fp_edges
WHERE ps_edges.procid = fp_edges.procid
GROUP BY fp_edges.farmid, ps_edges.storeid;
