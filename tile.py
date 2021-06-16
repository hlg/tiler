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
from tileSet import borders
from PIL import Image, ImageDraw

def jsonFromFileOrPolygon(geojson, polygon):
  if geojson != None: 
    return jsonFromFile(geojson)
  elif polygon == None:
    return jsonFromFile('osm-ruegen.geojson')
  else:
    return jsonFromPolygon(polygon)

def jsonFromPolygon(polygon, params=(0.000000,0.001000,0.005000)):
  polygonUrl = "http://polygons.openstreetmap.fr/?id={polygon}".format(polygon=polygon)
  urllib.urlopen(polygonUrl).read()
  if params is None:
    url = "http://polygons.openstreetmap.fr/get_geojson.py?id={polygon}&params=0".format(polygon=polygon)
  else:
    req = urllib2.Request(polygonUrl, 'x={x:.6f}&y={y:.6f}&z={z:.6f}&generate=Submit+Query'.format(x=params[0], y=params[1], z=params[2]))
    urllib2.urlopen(req).read() # throw away it is only human readable HTML
    url = "http://polygons.openstreetmap.fr/get_geojson.py?id={polygon}&params={x:.6f}-{y:.6f}-{z:.6f}".format(polygon=polygon, x=params[0], y=params[1], z=params[2])
  return jsonFromUrl(url)

def jsonFromUrl(geoJsonUrl):
  geoJson = urllib.urlopen(geoJsonUrl).read()
  return json.loads(geoJson)

def jsonFromFile(geoJsonFileName):
  with open(geoJsonFileName) as geoJson:
    return json.load(geoJson)

def multiPolyCoords(geoJson):
  assert geoJson['type']=='GeometryCollection' or geoJson['type']=='MultiPolygon'
  if geoJson['type'] == 'MultiPolygon':
    return geoJson['coordinates']
  else:
    assert len(geoJson['geometries']) == 1
    assert geoJson['geometries'][0]['type']== 'MultiPolygon'
    return geoJson['geometries'][0]['coordinates']

def createMap(geoJson, scale=1):
  return tile(multiPolyCoords(geoJson), scale)

def boundingBox(outline):
  # TODO reverse depending on orientation
  xmin = min([p.x for p in outline])
  ymin = min([p.y for p in outline])
  xmax = max([p.x for p in outline])
  ymax = max([p.y for p in outline])
  return (xmin, ymin, xmax, ymax)

def outlineFromPoly(multiPoly):
  return [GeoPoint(p) for p in reversed(max([poly[0] for poly in multiPoly],key=len))]

def tile(multiPoly, scale):
  outline = outlineFromPoly(multiPoly) 
  (xmin, ymin, xmax, ymax) = boundingBox(outline)
  for p in outline:
    p.x = (p.x -xmin) * scale
    p.y = (p.y -ymin) * scale

  (xmin, ymin, xmax, ymax) = boundingBox(outline)
  xoff = int(math.floor(xmin))
  yoff = int(math.floor(ymin))
  xd = int(math.floor(xmax)-xoff)
  yd = int(math.floor(ymax)-yoff)
  print('x:{xmin}-{xmax} / {xoff}+{xd}'.format(xmin=xmin,xmax=xmax,xoff=xoff,xd=xd), file=sys.stderr)
  print('y:{ymin}-{ymax} / {yoff}+{yd}'.format(ymin=ymin,ymax=ymax,yoff=yoff,yd=yd), file=sys.stderr)

  tileSet = [[Tile(x,y) for y in range(yd+1)] for x in range(xd+1)]
  for p in outline:
    p.tile = tileSet[int(p.x)][int(p.y)]
  print("tile set size:", len(tileSet), len(tileSet[0]))
  assert outline[0].x == outline[-1].x and outline[0].y == outline[-1].y
  outline.pop()
  lastTile = outline[-1].tile
  # assert that not all points in one tile?
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
  ## TODO remove either enumeration or tile.x/y
  onLand = False
  for x,column in enumerate(tileSet):
    for y,tile in enumerate(column):
      if len(tile.segments) > 2:
        l =len(tile.segments) 
        print('WARNING: tile {tile} has {l} segments'.format(tile=tile, l=l), file=sys.stderr)
      for side in [Border.RIGHT, Border.TOP, Border.LEFT, Border.BOTTOM]:
        crosses =  sorted(tile.crossesOnSide(side), key=attrgetter('position'))
        for (c, orderedBorder) in zip(crosses, borders[side]):
          if c.segmentIn.tile == tile:
            c.segmentIn.orderedIn = orderedBorder
          if c.segmentOut.tile == tile:
            c.segmentOut.orderedOut = orderedBorder
      segments = tuple([tuple([s.orderedOut,s.orderedIn]) for s in tile.segments])
      if segments and not onLand and renderer.landToTheRight(segments):
        onLand = True
      if segments and onLand and renderer.seaToTheRight(segments):
        onLand = False
      if not segments and onLand:
        segments = ((),())
      renderer.drawTileBySegments(draw,x,yd-y,segments)
  return img

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
  def crossesOnSide(self, side):
    for s in self.segments:
      if s.crossIn.borderIn == side:
        yield s.crossIn
      if s.crossOut.borderOut == side:
        yield s.crossOut
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
      if p.borderOut in [Border.RIGHT, Border.LEFT]:
        p.cross.position = p.y - int(p.y)
      else:
        p.cross.position = p.x - int(p.x)
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
  parser.add_argument('--scale', help='scale')
  args = parser.parse_args()
  
  img = createMap(jsonFromFileOrPolygon(args.geojson, args.polygon), 1 if args.scale is None else float(args.scale))

  img.save('map.png', "png")
  img.show()


