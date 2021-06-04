#!/usr/bin/python
import cgitb
cgitb.enable()

import cgi
import sys
from tile import createMapFromUrl
import urllib2
import urllib

query=cgi.FieldStorage()
polygon = ("polygon" in query) and query['polygon'].value or str(1434381) 

polygonUrl = "http://polygons.openstreetmap.fr/?id={polygon}".format(polygon=polygon)
urllib.urlopen(polygonUrl).read()
req = urllib2.Request(polygonUrl, 'x=0.000000&y=0.001000&z=0.005000&generate=Submit+Query')
urllib2.urlopen(req).read() # throw away it is only human readable HTML

geoJsonUrl = "http://polygons.openstreetmap.fr/get_geojson.py?id={polygon}&params=0.000000-0.001000-0.005000".format(polygon=polygon)
geoJsonFile = "osm-ruegen.geojson"

print("Content-Type:image/png\n")
img = createMapFromUrl(geoJsonUrl)
img.save(sys.stdout, "png")

