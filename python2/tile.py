#!/usr/bin/python
from __future__ import print_function
import json
import math
import sys
import argparse
import urllib
import urllib2
import time
from operator import attrgetter
from itertools import groupby
from tileSet import TileSet
from tileSet import Border
from PIL import Image, ImageDraw

def createMapFromUrl(geoJsonUrl):
  geoJson = urllib.urlopen(geoJsonUrl).read()
  return createMap(json.loads(geoJson))

def createMapFromFile(geoJsonFileName):
  with open(geoJsonFileName) as geoJson:
    return createMap(json.load(geoJson))

def createMap(geoJson):
  assert geoJson['type']=='GeometryCollection' or geoJson['type']=='MultiPolygon'
  if geoJson['type'] == 'MultiPolygon':
    return test(geoJson['coordinates'])
  else:
    assert len(geoJson['geometries']) == 1
    assert geoJson['geometries'][0]['type']== 'MultiPolygon'
    return test(geoJson['geometries'][0]['coordinates'])

def test(multiPoly):
  assert multiPoly[0][0][0] == multiPoly[0][0][-1]
  outline = [GeoPoint(p) for p in reversed(max([poly[0] for poly in multiPoly],key=len))]
  # TODO reverse depending on orientation
  xmin = min([p.x for p in outline])
  ymin = min([p.y for p in outline])
  xmax = max([p.x for p in outline])
  ymax = max([p.y for p in outline])
  xoff = int(math.floor(xmin))
  yoff = int(math.floor(ymin))
  xd = int(math.floor(xmax)-xoff)
  yd = int(math.floor(ymax)-yoff)
  print('x:{xmin}-{xmax} / {xoff}+{xd}'.format(xmin=xmin,xmax=xmax,xoff=xoff,xd=xd), file=sys.stderr)
  print('y:{ymin}-{ymax} / {yoff}+{yd}'.format(ymin=ymin,ymax=ymax,yoff=yoff,yd=yd), file=sys.stderr)
  tileSet = [[Tile(x,y) for y in range(yd+1)] for x in range(xd+1)]
  for p in outline:
    p.x -= xoff
    p.y -= yoff
    p.tile = tileSet[int(p.x)][int(p.y)]
  outline.pop() # should be same as first
  lastTile = outline[-1].tile
  while lastTile == outline[0].tile:
    outline.append(outline.pop(0))
  outline.append(outline[0])
  lines = [Line(s,e,tileSet) for [s,e] in zip(outline[:-1],outline[1:])] 
  for l in lines:
    l.addSegments()
  
  for tile, points in groupby(outline[:-1], key=attrgetter('tile')):
    pointsInSameTile = list(points)
    crossIn = pointsInSameTile[0].lineIn.points[-1].cross
    crossOut = pointsInSameTile[-1].lineOut.points[0].cross
    tile.addSegment(Segment(crossIn, crossOut))
  for column in tileSet:
    for tile in column:
        for segment in tile.segments:
          if segment.crossIn.segmentIn.tile == segment.crossOut.segmentOut.tile and (len(tile.segments)>1 or len(segment.crossIn.segmentIn.tile.segments)>2):
            t = segment.crossIn.segmentIn.tile
            l = len(t.segments)
            print('Simplify segement in tile {t} with {l} segments'.format(t=t,l=l), file=sys.stderr)
            t.removeSegment(segment.crossIn.segmentIn)
            t.removeSegment(segment.crossOut.segmentOut)
            t.addSegment(Segment(segment.crossIn.segmentIn.crossIn, segment.crossOut.segmentOut.crossOut))
            tile.removeSegment(segment)

  img = Image.new(mode="L", size=((xd+1)*30,(yd+1)*30), color=128)
  draw = ImageDraw.Draw(img)
  renderer = TileSet()
  for x,column in enumerate(tileSet):
    for y,tile in enumerate(column):
      if len(tile.segments) > 2:
        l =len(tile.segments) 
        print('WARNING: tile {tile} has {l} segments'.format(tile=tile, l=l), file=sys.stderr)
      segments = tuple([tuple([s.crossIn.borderIn, s.crossOut.borderOut]) for s in tile.segments[:2]])
      renderer.drawTileBySegments(draw,x,yd-y,segments)
  return img


def printLines(lines):
  for l in lines:
    print(l.start)
    for p in l.points:
      print(p)
    print(l.end)
    print('-----')

class Tile(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.segments = []
  def addSegment(self, segment):
    self.segments.append(segment)
    segment.tile = self
  def removeSegment(self,segment):
    self.segments.remove(segment)
    segment.tile = None
  def __str__(self):
    return '{self.x},{self.y}'.format(self=self)

class Segment(object):
  def __init__(self, crossIn, crossOut): # TODO tile needed?
    self.crossIn = crossIn
    self.crossOut = crossOut
    crossIn.segmentOut = self
    crossOut.segmentIn = self
  def __str__(self):
    return '{self.crossIn.borderIn}-{self.crossOut.borderOut}'.format(self=self)

class Cross(object):
  def __init__(self, borderOut, borderIn):
    self.borderOut = borderOut
    self.borderIn = borderIn

class Line(object):
  def __init__(self, start, end, tileSet):
    self.start = start
    self.end = end
    start.lineOut = self
    end.lineIn = self
    self.points = []
    def fwdRange(a,b):
      return (range(int(math.ceil(a)),int(math.ceil(b)),1), (-1,0))
    def bwdRange(a,b):
      return (range(int(math.floor(a)),int(math.floor(b)),-1), (0,-1))
    def innerRange(a,b):
      return fwdRange(a,b) if a<b else bwdRange(a,b)
    def interpolate(x,xs,xe,ys,ye):
      return (x-xs)*(ye-ys)/(xe-xs) + ys
    (gridRange, fromTo) = innerRange(self.start.x,self.end.x)
    borders = [{-1: Border.RIGHT, 0: Border.LEFT}[ft] for ft in fromTo]
    for x in gridRange:
      y = interpolate(x, self.start.x, self.end.x, self.start.y, self.end.y)
      self.points.append(BorderPoint(
        x, y, tileSet[x+fromTo[0]][int(y)], tileSet[x+fromTo[1]][int(y)],
        borders[0], borders[1]
      )) 
    (gridRange, fromTo)  = innerRange(self.start.y,self.end.y)
    borders = [{-1: Border.TOP, 0: Border.BOTTOM}[ft] for ft in fromTo]
    for y in gridRange:
      x = interpolate(y, self.start.y, self.end.y, self.start.x, self.end.x)
      self.points.append(BorderPoint(
        x, y, tileSet[int(x)][y+fromTo[0]], tileSet[int(x)][y+fromTo[1]],
        borders[0], borders[1]
      ))
    if self.start.x != self.end.x:  # TODO use direction with larger distance?
      self.points.sort(key=attrgetter('x'),reverse=self.start.x>self.end.x) 
    else:
      self.points.sort(key=attrgetter('y'),reverse=self.start.y>self.end.y) 
  def addSegments(self):
    for p in self.points:
      p.cross = Cross(p.borderOut,p.borderIn)
    for p1,p2 in zip(self.points[:-1],self.points[1:]):
      assert p1.tileIn == p2.tileOut
      p1.tileIn.addSegment(Segment(p1.cross, p2.cross))
      
  def __str__(self):
    return '{self.start}-{self.end}'.format(self=self)

class Point(object):
  def __init__(self,x,y):
    self.x = x
    self.y = y
  def __str__(self):
    return '({self.x},{self.y}) '.format(self=self)

class BorderPoint(Point):
  def __init__(self,x,y,tileOut,tileIn,borderOut,borderIn):
    self.tileOut = tileOut 
    self.tileIn = tileIn
    self.borderOut = borderOut 
    self.borderIn = borderIn
    super(BorderPoint, self).__init__(x,y)
  def __str__(self):
    return super(BorderPoint, self).__str__()+' [{self.tileOut}-{self.tileIn}] {self.borderOut}-{self.borderIn}'.format(self=self)

class GeoPoint(Point):
  def __init__(self,longLat):
      (longitude, latitude) = longLat
      super(GeoPoint, self).__init__(
        longitude * 111.1949, # 6371/360*2pi
        math.log(math.tan(math.radians(latitude)/2 + math.pi/4)) * 6371

      )
  def addSegment(self):
    crossIn = self.lineIn.points[-1].cross
    print(self.lineOut)
    crossOut = self.lineOut.points[0].cross
    self.tile.addSegment(Segment(crossIn, crossOut))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--polygon', help='ID of OSM polygon')
  parser.add_argument('--geojson', help='GeoJson file with polygon')
  args = parser.parse_args()
  
  geoJson = args.geojson != None and args.geojson or 'simplified/osm-ruegen.geojson'
  if args.geojson != None or args.polygon == None:
    img = createMapFromFile(geoJson)
  else:
    polygonUrl = "http://polygons.openstreetmap.fr/?id={polygon}".format(polygon=args.polygon)
    urllib.urlopen(polygonUrl).read()
    req = urllib2.Request(polygonUrl, 'x=0.000000&y=0.001000&z=0.005000&generate=Submit+Query')
    urllib2.urlopen(req).read() # throw away it is only human readable HTML
    geoJsonUrl = "http://polygons.openstreetmap.fr/get_geojson.py?id={polygon}&params=0.000000-0.001000-0.005000".format(polygon=args.polygon)
    img = createMapFromUrl(geoJsonUrl) 

  img.save('map.png', "png")
  img.show()


