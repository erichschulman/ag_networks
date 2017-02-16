# Food Networks!
This is the code repo for my Honors Thesis. Depending on who you ask, it's more interesting than Chopped. I'm trying to specify a transportation problem using NYS's publically available GIS data. I plan to solve the problem with the Gurobi Optimizer. Most of the code/data I'm using is open source or open access. Gurobi is not (but is free with an academic license).

Email me at ehs82@cornell.edu if you're interested!

##Software Dependencies

These are the software packages you need to run my code.

###Installing OSRM
https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM

###Installing Nominatim
http://wiki.openstreetmap.org/wiki/Nominatim/Installation_on_CentOS
http://wiki.openstreetmap.org/wiki/Nominatim/Installation

###Reference for Minimum Cost Maximum Flow with Gurobi
http://www.gurobi.com/documentation/7.0/examples/netflow_py.html

##Code organization

###`db_create.sql`
This file contains the create statements for the database

###`edges.sql`
This file contains the queries that makes 

###`farms.py`
This file contains the code used for importing the .tif sattelite image into the database

####Raster Data and QGis
Originally, I planned to import the Raster data with QGis, but this process is fairly tedious and slow, so I automated it with `farms.py`. I wanted to keep track of these instructions, in case I need them later.

1. start by importing the tif image. Use the raster calculator in the raster menu raster and select the appropriate band
2. use the translate tool to set 0 to no data
3. then polygonize
4. then open the attribute table by right clicking the polygon menu. drop an appropriate number of observations that are too small. Then use:
for area: `$area`
for longitude: `x( transform(centroid( $geometry), 'EPSG:32618', 'EPSG:4326'  ) )`
for latitude: `y( transform(centroid( $geometry), 'EPSG:32618', 'EPSG:4326'  ) )`


###`stores.py`
This file contains the codes that imports the store and intermediary into the database. `stores.py` expects OSRM to be running on the local host with the NYS OSM data. You can also configure the file to use a local instance of nominatim.

####To run nominatim server
`sudo systemctl start postgresql`

`sudo systemctl start httpd`

####To run OSRM server (from the osrm directory)
`osrm-routed ../maps/new-york-latest.osrm`


###`edges.py`
This file contains the code that populates the database with edges between farms, producers and 


###`transport.py`
This file will eventually specify the transportation problem for the gurobi optimizer. Right now, it
just runs an example of the minimum cost maximum flow problem.

###`main.py`
Running this file will eventually do all the steps in the project start to finish. I may include flags
to break things up.

##Data

Below are the data sources that I am using

###Farm Product Dealers
https://data.ny.gov/Economic-Development/Farm-Product-Dealer-Licenses-Currently-Issued/ehtk-kzxa

###Food Retail Stores
https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj

Describes the store classification codes
 https://data.ny.gov/api/views/6kqu-2c4m/files/UBDP3oW2f-K767I4f51EJaIUO8eNGPrAQQj8tSvBhbo?download=true&filename=NYSDAM_RetailFoodStoresEstablishmentTypeCodes.pdf

###Sattelite Farm Data
http://cugir.mannlib.cornell.edu/bucketinfo.jsp?id=8033


###OSM Map of NYS
https://www.geofabrik.de/data/download.html

###Tiger Data with Street Addresses
https://www.census.gov/geo/maps-data/data/tiger-geodatabases.html

