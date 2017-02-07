import requests


#http://wiki.openstreetmap.org/wiki/Nominatim/Installation_on_CentOS
#http://wiki.openstreetmap.org/wiki/Nominatim/Installation


#https://www.geofabrik.de/data/download.html

if __name__ == "__main__":
	
	#sudo systemctl start postgresql
	#sudo systemctl start httpd
	#

	url_osrm = "http://0.0.0.0:5000/route/v1/driving/-73.81274,42.31105;76.486243,42.440126?steps=true"
	#url_osrm= "http://0.0.0.0:5000/table/v1/driving/42.31105,-73.81274;42.440126,-76.486243"

	print url_osrm
	osrm = requests.get(url_osrm)
	print osrm.text