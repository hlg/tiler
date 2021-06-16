#!/usr/bin/python
import cgitb; cgitb.enable()
import cgi
import sys
from tile import createMap, jsonFromFileOrPolygon
import urllib2
import urllib

query=cgi.FieldStorage()
polygon = ("polygon" in query) and query['polygon'].value or None

print("Content-Type:image/png\n")
img = createMap(jsonFromFileOrPolygon(None, polygon))
img.save(sys.stdout, "png")

