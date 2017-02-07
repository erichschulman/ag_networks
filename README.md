# ag_networks
Code for my Honors Thesis

Software Dependencies

Installing Nominatim
http://wiki.openstreetmap.org/wiki/Nominatim/Installation_on_CentOS
http://wiki.openstreetmap.org/wiki/Nominatim/Installation


Reference for netflow with Gurobi
http://www.gurobi.com/documentation/7.0/examples/netflow_py.html

Data

farm product dealers
https://data.ny.gov/Economic-Development/Farm-Product-Dealer-Licenses-Currently-Issued/ehtk-kzxa

food retail stores
https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj

sattelite farm data
http://cugir.mannlib.cornell.edu/bucketinfo.jsp?id=8033

Describes the store classification codes
 https://data.ny.gov/api/views/6kqu-2c4m/files/UBDP3oW2f-K767I4f51EJaIUO8eNGPrAQQj8tSvBhbo?download=true&filename=NYSDAM_RetailFoodStoresEstablishmentTypeCodes.pdf

OSM map of NYS
https://www.geofabrik.de/data/download.html

Running Code

To run nominatim server
sudo systemctl start postgresql
sudo systemctl start httpd

To run OSRM server (from the osrm directory)
osrm-routed ../maps/new-york-latest.osrm


Todo

1. get a list of farms by using qgis
-update with sizes using qgis
-add up total size
-add percentage size

2. get a list of stores using NY data
-link to size using square footage
-link to costs
-give as percentage of both

3. get a list of intermediate processors

4. use mapquest api to determine edge costs for farm to intermeidate
- use mapquest api to determine edge costs for intermeidate to stores
https://developer.mapquest.com/documentation/directions-api/route-matrix/post/

5. determine optimal routes from farms to stores.

for all f and s
min:si +fi


6. determine prices
(repeat for other crops?)



