#!/usr/bin/python
from __future__ import print_function
from PIL import Image, ImageDraw
import sys

class Border():
  RIGHT = 1
  BOTTOM = 2
  LEFT = 3
  TOP = 4 

class BorderOrdered():
  R1 = 1
  R2 = 2
  R3 = 3
  B1 = 4
  B2 = 5
  B3 = 6
  L1 = 7
  L2 = 8
  L3 = 9
  T1 = 10
  T2 = 11
  T3 = 12

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
    ((R, T),): ((0,4,6,10,14),),
    ((R, L),): ((0,8,10,14),),
    ((R, B),): ((0,12,14),),
    ((T ,L),): ((4,8,10,14,2),),
    ((T, B),): ((4,12,14,2),),
    ((T, R),): ((4,0,2),),
    ((L, B),): ((8,12,14,2,6),),
    ((L, R),): ((8,0,2,6),),
    ((L, T),): ((8,4,6),),
    ((B, R),): ((12,0,2,6,10),),
    ((B, T),): ((12,4,6,10),),
    ((B, L),): ((12,8,10),),
    # two border segments
    ((T, R),(R, T)): ((1,3,5,15),),
    ((R, T),(T, R)): ((3,1,2),(5,6,10,14,15)),
    ((L,R),(R,T)): ((1,4,6,8,15),),
    ((T,R),(R,L)): ((4,1,2),(8,10,14,15)),
    ((B,R),(R,T)): ((1,4,6,10,12,15),),
    ((T,R),(R,B)): ((4,1,2),(12,14,15)),
    ((R,T),(T,L)): ((0,3,5,8,10,14),),
    ((L,T),(T,R)): ((3,0,2),(5,6,8)),
    ((R,T),(T,B)): ((0,3,5,12,14),),
    ((B,T),(T,R)): ((3,0,2),(5,6,10,12)),
    ((R,T),(L,B)): ((0,4,6,8,12,14),),  # 6
    ((B,L),(T,R)): ((0,4,2),(8,10,12)), # 6
    ((L,R),(R,L)): ((1,7,9,15),),
    ((R,L),(L,R)): ((1,2,6,7),(9,10,14,15)),
    ((B,R),(R,L)): ((1,8,10,12,15),),
    ((L,R),(R,B)): ((1,2,6,8),(15,12,14)),
    ((T,L),(L,R)): ((2,4,7,9,0),),
    ((R,L),(L,T)): ((4,6,7),(9,10,14,0)),
    ((R,L),(L,B)): ((0,7,9,12,14),),
    ((B,L),(L,R)): ((0,2,6,7),(9,10,12)),
    ((B,R),(R,B)): ((1,11,13,15),),  # 11
    ((R,B),(B,R)): ((1,2,6,10,11),(15,13,14)), # 11
    ((B,R),(T,L)): ((0,2,4,8,10,12),),
    ((L,T),(R,B)): ((4,6,8),(0,12,14)),
    ((T,B),(B,R)): ((4,11,13,0,2),),
    ((R,B),(B,T)): ((4,6,10,11),(13,14,0)),
    ((L,B),(B,R)): ((6,8,11,13,0,2),),
    ((R,B),(B,L)): ((8,10,11),(13,14,0)),
    ((T,L),(L,T)): ((5,7,9,3),),
    ((L,T),(T,L)): ((5,6,7),(9,10,14,2,3)),
    ((B,T),(T,L)): ((5,8,10,12,3),), # 16
    ((L,T),(T,B)): ((5,6,8),(12,14,2,3)), #16
    ((T,L),(L,B)): ((4,7,9,12,14,2),),
    ((B,L),(L,T)): ((4,6,7),(9,10,12)),
    ((B,T),(T,B)): ((5,11,13,3),),
    ((T,B),(B,T)): ((5,6,10,11),(13,14,2,3)),
    ((L,B),(B,T)): ((4,6,8,11,13),) ,
    ((T,B),(B,L)): ((8,11,10),(13,14,2,4)),
    ((B,L),(L,B)): ((9,11,13,7),),
    ((L,B),(B,L)): ((9,10,11),(13,14,2,6,7)),
    (): (),
    ((),()): ((2,6,10,14),),
    ((R,R),): ((1,16,19,15),),
    ((T,T),): ((5,17,16,3),),
    ((L,L),): ((9,18,17,7),),
    ((B,B),): ((13,19,18,11),)
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
    tile = segments in self.tilesDict and self.tilesDict[segments] or None
    if tile==None:
      reversedSegments = tuple(reversed(segments))
      tile = reversedSegments in self.tilesDict and self.tilesDict[reversedSegments] or None
    if tile==None:
      if segments != ():
        print('Not found: {segments}'.format(segments=segments), file=sys.stderr)
    else:
      self.drawTile(draw, x, y, tile)

  def drawTile(self, draw, x, y, tile):
    for poly in tile:
      points = [(self.coords[p][0]+x*30, self.coords[p][1]+y*30) for p in poly]
      draw.polygon(points, fill=255, outline=0)

if __name__ == "__main__":
  TileSet().tileSet()

