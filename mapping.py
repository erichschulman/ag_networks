import requests


#http://wiki.openstreetmap.org/wiki/Nominatim/Installation_on_CentOS
#http://wiki.openstreetmap.org/wiki/Nominatim/Installation


if __name__ == "__main__":
	url_osrm = "http://0.0.0.0:5000/route/v1/driving/41.4427,-73.8213;41.2151,-73.6153?steps=true"
	url_osrm= "http://0.0.0.0:5000/table/v1/driving/41.4427,-73.8213;41.2151,-73.6153?sources=0&destinations=1"
	print url_osrm
	osrm = requests.get(url_osrm)
	print osrm.text