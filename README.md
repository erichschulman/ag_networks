# Food Networks!
This is the code repo for my Undergraduate Honors Thesis. The goal of the project was to specify optimal transportation problem in New York agriculture using publically avaible GIS data. I plan to solve the problem with the Gurobi Linear Optimizer.

Although, I am not actively developing this project, I may revist it in the future.

## Software Dependencies

These are the software packages you need to run my code.

### Installing OSRM
https://github.com/Project-OSRM/osrm-backend/wiki/Building-OSRM

### Installing Nominatim
http://wiki.openstreetmap.org/wiki/Nominatim/Installation_on_CentOS
http://wiki.openstreetmap.org/wiki/Nominatim/Installation

### Reference for Minimum Cost Maximum Flow with Gurobi
http://www.gurobi.com/documentation/7.0/examples/netflow_py.html

## File System organization

To run the code, you should make an `input` folder where you put the data.

Running the code should create the following folders


1. `db` - stores the databases
2. `maps` - stores the maps created by the program
3. `solutions` - stores the linear program outputs

## Code organization

### `db_create.sql`
This file contains the create statements for the database

### `edges.sql`
This file contains the queries that makes 

### `farms.py`
This file contains the code used for importing the .tif sattelite image into the database

#### Raster Data and QGis
Originally, I planned to import the Raster data with QGis, but this process is fairly tedious and slow, so I automated it with `farms.py`. I wanted to keep track of these instructions, in case I need them later.

1. Start by importing the .tif image. Use the raster calculator in the raster menu raster and select the appropriate band.
2. Use the translate tool to set 0 to no data.
3. Then, polygonize
4. Then, open the attribute table by right clicking the polygon menu. Drop an appropriate number of observations that are too small. Then use:

for area: `$area`

for longitude: `x( transform(centroid( $geometry), 'EPSG:32618', 'EPSG:4326'  ) )`

for latitude: `y( transform(centroid( $geometry), 'EPSG:32618', 'EPSG:4326'  ) )`

### `stores.py`
This file contains the codes that imports the store and intermediary into the database. `stores.py` expects OSRM to be running on the local host with the NYS OSM data. You can also configure the file to use a local instance of nominatim.

#### To start the Nominatim Server
`sudo systemctl start postgresql`

`sudo systemctl start httpd`

#### To start the OSRM Server
(change to the OSRM directory)
`osrm-routed ../maps/new-york-latest.osrm`


### `edges.py`
This file contains the code that populates the database with edges between farms, producers and 


### `transport.py`
This file will eventually specify the transportation problem for the Gurobi Optimizer. Right now, it
just runs an example of the minimum cost maximum flow problem.

### `main.py`
Running this file will eventually does all steps in the project start to finish.

### `maps.py`
Running this file creates maps for each of the different types of crops to better visualize the results. Parsing large .sol files is pretty lame.

### `solutions.py`
This file lets me experiment with solutions to the linear programming problem to check what else might be feasible.

## Data

Below are the data sources that I am using


### Median Property Value Census Data
https://factfinder.census.gov/faces/nav/jsf/pages/download_center.xhtml

To Find the Data through the Portal:

1. Start > Looking for Specific Data set
2. Dataset> American Community Servey, 2010 ACS 5-year Selected Population Tables
3. Topics> Housing, Value of Home
4. Geographies> Census Tract, New York, All Counties

### Tiger SHP Files with Census Tract
For matching Census data with GPS coordinates
https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2010&layergroup=Census+Tracts


### Farm Product Dealers
https://data.ny.gov/Economic-Development/Farm-Product-Dealer-Licenses-Currently-Issued/ehtk-kzxa

### Food Retail Stores
https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj

Describes the store classification codes
 https://data.ny.gov/api/views/6kqu-2c4m/files/UBDP3oW2f-K767I4f51EJaIUO8eNGPrAQQj8tSvBhbo?download=true&filename=NYSDAM_RetailFoodStoresEstablishmentTypeCodes.pdf

### Sattelite Farm Data
http://cugir.mannlib.cornell.edu/bucketinfo.jsp?id=8033

The bands I've selected for my analysis are as follows

1. onions - 49
2. cherries - 66
3. cabbage - 243
4. grapes - 69

### OSM Map of NYS
https://www.geofabrik.de/data/download.html

### Tiger Data with Street Addresses
https://www.census.gov/geo/maps-data/data/tiger-geodatabases.html

### Other useful maps of NYS (for the write up)
http://gis.ny.gov/gisdata/inventories/details.cfm?DSID=927
