#!/usr/bin/python
from __future__ import print_function
from PIL import Image, ImageDraw
import sys

class Border():
  RIGHT = 1
  TOP = 2 
  LEFT = 3
  BOTTOM = 4

class BorderOrdered():
  R1 = 1
  R2 = 2
  R3 = 3
  T1 = 4 
  T2 = 5 
  T3 = 6 
  L1 = 7
  L2 = 8
  L3 = 9
  B1 = 10
  B2 = 11
  B3 = 12

R=Border.RIGHT
L=Border.LEFT
T=Border.TOP
B=Border.BOTTOM

R1=BorderOrdered.R1
R2=BorderOrdered.R2
R3=BorderOrdered.R3
L1=BorderOrdered.L1
L2=BorderOrdered.L2
L3=BorderOrdered.L3
T1=BorderOrdered.T1
T2=BorderOrdered.T2
T3=BorderOrdered.T3
B1=BorderOrdered.B1
B2=BorderOrdered.B2
B3=BorderOrdered.B3

borders = {R: (R1,R2,R3), T: (T1,T2,T3), L: (L1,L2,L3), B: (B1,B2,B3)}

class TileSet(object):
  coords = (
    (30,15),(30,10),(30,0),(20,0),(15,0),(10,0),(0,0),(0,10),
    (0,15),(0,20),(0,30),(10,30),(15,30),(20,30),(30,30),(30,20),
    (20,10),(10,10),(10,20),(20,20)
  )
  tilesDict = {
    # one border segment
    ((R1, T1),): ((0,4,6,10,14),),
    ((R1, L1),): ((0,8,10,14),),
    ((R1, B1),): ((0,12,14),),
    ((T1 ,L1),): ((4,8,10,14,2),),
    ((T1, B1),): ((4,12,14,2),),
    ((T1, R1),): ((4,0,2),),
    ((L1, B1),): ((8,12,14,2,6),),
    ((L1, R1),): ((8,0,2,6),),
    ((L1, T1),): ((8,4,6),),
    ((B1, R1),): ((12,0,2,6,10),),
    ((B1, T1),): ((12,4,6,10),),
    ((B1, L1),): ((12,8,10),),
    # two border segments
    ((R2,T2),(T1,R1)): ((1,3,5,15),),
    ((R1,T1),(T2,R2)): ((1,2,3),(5,6,10,14,15)),
    ((R2,T1),(L1,R1),): ((1,4,6,8,15),),
    ((R1,L1),(T1,R2)): ((4,1,2),(8,10,14,15)),
    ((R2,T1),(B1,R1)): ((1,4,6,10,12,15),),
    ((R1,B1),(T1,R2)): ((4,1,2),(12,14,15)),
    ((R1,T2),(T1,L1)): ((0,3,5,8,10,14),),
    ((T2,R1),(L1,T1)): ((3,0,2),(5,6,8)),
    ((R1,T2),(T1,B1)): ((0,3,5,12,14),),
    ((T2,R1),(B1,T1)): ((3,0,2),(5,6,10,12)),
    ((R1,T1),(L1,B1)): ((0,4,6,8,12,14),),  # 6
    ((T1,R1),(B1,L1)): ((0,4,2),(8,10,12)), # 6
    ((R2,L2),(L1,R1)): ((1,7,9,15),),
    ((R1,L1),(L2,R2)): ((1,2,6,7),(9,10,14,15)),
    ((R2,L1),(B1,R1)): ((1,8,10,12,15),),
    ((R1,B1),(L1,R2)): ((1,2,6,8),(15,12,14)),
    ((T1,L2),(L1,R1)): ((2,4,7,9,0),),
    ((R1,L1),(L2,T1)): ((4,6,7),(9,10,14,0)),
    ((R1,L2),(L1,B1)): ((0,7,9,12,14),),
    ((L2,R1),(B1,L1)): ((0,2,6,7),(9,10,12)),
    ((R2,B1),(B2,R1)): ((1,11,13,15),),  # 11
    ((R1,B2),(B1,R2)): ((1,2,6,10,11),(15,13,14)), # 11
    ((T1,L1),(B1,R1)): ((0,2,4,8,10,12),),
    ((R1,B1),(L1,T1)): ((4,6,8),(0,12,14)),
    ((T1,B1),(B2,R1)): ((4,11,13,0,2),),
    ((R1,B2),(B1,T1)): ((4,6,10,11),(13,14,0)),
    ((L1,B1),(B2,R1)): ((6,8,11,13,0,2),),
    ((R1,B2),(B1,L1)): ((8,10,11),(13,14,0)),
    ((T1,L2),(L1,T2)): ((5,7,9,3),),
    ((T2,L1),(L2,T1)): ((5,6,7),(9,10,14,2,3)),
    ((T1,L1),(B1,T2)): ((5,8,10,12,3),), # 16
    ((T2,B1),(L1,T1)): ((5,6,8),(12,14,2,3)), #16
    ((T1,L2),(L1,B1)): ((4,7,9,12,14,2),),
    ((L2,T1),(B1,L1)): ((4,6,7),(9,10,12)),
    ((T1,B1),(B2,T2)): ((5,11,13,3),),
    ((T2,B2),(B1,T1)): ((5,6,10,11),(13,14,2,3)),
    ((L1,B1),(B2,T1)): ((4,6,8,11,13),) ,
    ((T1,B2),(B1,L1)): ((8,11,10),(13,14,2,4)),
    ((L1,B1),(B2,L2)): ((9,11,13,7),),
    ((L2,B2),(B1,L1)): ((9,10,11),(13,14,2,6,7)),
    (): (),
    ((),()): ((2,6,10,14),),
    ((R2,R1),): ((1,16,19,15),),
    ((R1,R2),): ((15,19,16,1,2,6,10,14),),
    ((T1,T2),): ((5,17,16,3),),
    ((T2,T1),): ((3,16,17,5,6,10,14,2),),
    ((L1,L2),): ((9,18,17,7),),
    ((L2,L1),): ((7,17,18,9,10,14,2,6),),
    ((B2,B1),): ((13,19,18,11),),
    ((B1,B2),): ((11,18,19,13,14,2,6,10),)
  }

  tiles = list(tilesDict.values())

  def tileSet(self):
    img = Image.new(mode="L", size=(6*30,12*30), color=128)
    draw = ImageDraw.Draw(img)
    for i, tile in enumerate(self.tiles):
        self.drawTile(draw,i%6,int(i/6),tile)
    img.save('tiles.png', "png")

  def drawTileByNumber(self, draw, x, y, tileNo):
    self.drawTile(draw, x, y, self.tiles[tileNo])

  def drawTileBySegments(self, draw, x, y, segments):
    sortedSegments = tuple(sorted(segments))
    if not sortedSegments in self.tilesDict:
      if segments != ():
        print('Not found: {segments}'.format(segments=segments), file=sys.stderr)
    else:
      tile = self.tilesDict[sortedSegments]
      self.drawTile(draw, x, y, tile)

  def landToTheRight(self, segments):
    sortedSegments = tuple(sorted(segments))
    if sortedSegments in self.tilesDict:
      tile = self.tilesDict[sortedSegments]
      return any((all((p in poly for p in (2,6))) for poly in tile))

  def seaToTheRight(self, segments):
    sortedSegments = tuple(sorted(segments))
    if sortedSegments in self.tilesDict:
      tile = self.tilesDict[sortedSegments]
      return all((not any((p in poly for p in (2,3,4,5,6))) for poly in tile))

  def drawTile(self, draw, x, y, tile):
    for poly in tile:
      points = [(self.coords[p][0]+x*30, self.coords[p][1]+y*30) for p in poly]
      draw.polygon(points, fill=255, outline=0)

if __name__ == "__main__":
  TileSet().tileSet()

