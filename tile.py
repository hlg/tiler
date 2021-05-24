import json
import math
from operator import attrgetter
from itertools import groupby
from tileSet import drawTileBySegments
from tileSet import Border
from PIL import Image, ImageDraw

def main():
  with open('simplified/osm-ruegen.geojson') as f:
    geo = json.load(f)
    assert geo['type']=='GeometryCollection'
    assert len(geo['geometries']) == 1
    assert geo['geometries'][0]['type']== 'MultiPolygon'
    simple = geo['geometries'][0]['coordinates']
    test(simple)

def test(multiPoly):
  assert multiPoly[0][0][0] == multiPoly[0][0][-1]
  outline = [GeoPoint(p) for p in reversed(multiPoly[0][0])]
  xmin = min([p.x for p in outline])
  ymin = min([p.y for p in outline])
  xmax = max([p.x for p in outline])
  ymax = max([p.y for p in outline])
  xoff = math.floor(xmin)
  yoff = math.floor(ymin)
  xd = math.floor(xmax)-xoff
  yd = math.floor(ymax)-yoff
  print(f'x:{xmin}-{xmax} / {xoff}+{xd}')
  print(f'y:{ymin}-{ymax} / {yoff}+{yd}')
  tileSet = [[Tile(x,y) for y in range(yd+1)] for x in range(xd+1)]
  for p in outline:
    p.x -= xoff
    p.y -= yoff
    p.tile = tileSet[int(p.x)][int(p.y)]
  outline[-1] = outline[0]
  lines = [Line(s,e,tileSet) for [s,e] in zip(outline[:-1],outline[1:])] 
  for l in lines:
    l.addSegments()
  pointGroups = []
  for tile, points in groupby(outline[:-1], key=attrgetter('tile')):
    pointsInSameTile = list(points)
    pointGroups.append(pointsInSameTile)
    crossIn = pointsInSameTile[0].lineIn.points[-1].cross
    crossOut = pointsInSameTile[-1].lineOut.points[0].cross
    tile.addSegment(Segment(crossIn, crossOut))
  for column in tileSet:
    for tile in column:
        for segment in tile.segments:
          if segment.crossIn.segmentIn.tile == segment.crossOut.segmentOut.tile and (len(tile.segments)>1 or len(segment.crossIn.segmentIn.tile.segments)>2):
            t = segment.crossIn.segmentIn.tile
            print(f'Simplify segement in tile {t} with {len(t.segments)} segments')
            t.removeSegment(segment.crossIn.segmentIn)
            t.removeSegment(segment.crossOut.segmentOut)
            t.addSegment(Segment(segment.crossIn.segmentIn.crossIn, segment.crossOut.segmentOut.crossOut))
            tile.removeSegment(segment)

  img = Image.new(mode="L", size=((xd+1)*30,(yd+1)*30), color=128)
  draw = ImageDraw.Draw(img)
  for x,column in enumerate(tileSet):
    for y,tile in enumerate(column):
      if len(tile.segments) > 2:
        print(f'WARNING: tile {tile} has {len(tile.segments)} segments')
      segments = tuple([tuple([s.crossIn.borderIn, s.crossOut.borderOut]) for s in tile.segments[:2]])
      drawTileBySegments(draw,x,yd-y,segments)
  img.save(f'map.png', "png")
      
        

def printLines(lines):
  for l in lines:
    print(l.start)
    for p in l.points:
      print(p)
    print(l.end)
    print('-----')

class Tile:
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
    return f'{self.x},{self.y}'

class Segment:
  def __init__(self, crossIn, crossOut): # TODO tile needed?
    self.crossIn = crossIn
    self.crossOut = crossOut
    crossIn.segmentOut = self
    crossOut.segmentIn = self
  def __str__(self):
    return f'{self.crossIn.borderIn}-{self.crossOut.borderOut}'

class Cross:
  def __init__(self, borderOut, borderIn):
    self.borderOut = borderOut
    self.borderIn = borderIn

class Line:
  def __init__(self, start, end, tileSet):
    self.start = start
    self.end = end
    start.lineOut = self
    end.lineIn = self
    self.points = []
    def fwdRange(a,b):
      return range(math.ceil(a),math.ceil(b),1)
    def bwdRange(a,b):
      return range(math.floor(a),math.floor(b),-1)
    def innerRange(a,b):
      return fwdRange(a,b) if a<b else bwdRange(a,b)
    def interpolate(x,xs,xe,ys,ye):
      return (x-xs)*(ye-ys)/(xe-xs) + ys
    gridRange = innerRange(self.start.x,self.end.x)
    fromTo = gridRange.step==1 and (-1,0) or (0,-1)
    borders = [{-1: Border.RIGHT, 0: Border.LEFT}[ft] for ft in fromTo]
    for x in gridRange:
      y = interpolate(x, self.start.x, self.end.x, self.start.y, self.end.y)
      self.points.append(BorderPoint(
        x, y, tileSet[x+fromTo[0]][int(y)], tileSet[x+fromTo[1]][int(y)],
        borders[0], borders[1]
      )) 
    gridRange = innerRange(self.start.y,self.end.y)
    fromTo = gridRange.step==1 and (-1,0) or (0,-1)
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
    return f'{self.start}-{self.end}'

class Point:
  def __init__(self,x,y):
    self.x = x
    self.y = y
  def __str__(self):
    return f'({self.x},{self.y}) '

class BorderPoint(Point):
  def __init__(self,x,y,tileOut,tileIn,borderOut,borderIn):
    self.tileOut = tileOut 
    self.tileIn = tileIn
    self.borderOut = borderOut 
    self.borderIn = borderIn
    super().__init__(x,y)
  def __str__(self):
    return super().__str__()+f' [{self.tileOut}-{self.tileIn}] {self.borderOut}-{self.borderIn}'

class GeoPoint(Point):
  def __init__(self,latLong):
      (longitude, latitude) = latLong 
      super().__init__(
        longitude * 111.320 * math.cos(math.radians(latitude)),
        latitude * 110.574
      )
  def addSegment(self):
    crossIn = self.lineIn.points[-1].cross
    print(self.lineOut)
    crossOut = self.lineOut.points[0].cross
    self.tile.addSegment(Segment(crossIn, crossOut))

if __name__ == '__main__':
  main()

