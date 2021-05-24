from PIL import Image, ImageDraw
import sys
from enum import IntEnum

class Border(IntEnum):
  RIGHT = 1
  BOTTOM = 2
  LEFT = 3
  TOP = 4

coords = (
  (30,12),(30,0),(18,0),(12,0),(0,0),(0,12),
  (0,18),(0,30),(12,30),(18,30),(30,30),(30,18),
  (18,12),(12,12),(12,18),(18,18)
)
R=Border.RIGHT
L=Border.LEFT
T=Border.TOP
B=Border.BOTTOM
tileByBorder = {
  # one border segment
  ((R, T),): ((0,2,4,7,10),),
  ((R, L),): ((0,5,7,10),),
  ((R, B),): ((0,8,10),),
  ((T ,L),): ((3,5,7,10,1),),
  ((T, B),): ((3,8,10,1),),
  ((T, R),): ((3,11,1),),
  ((L, B),): ((6,8,10,1,4),),
  ((L, R),): ((6,11,1,4),),
  ((L, T),): ((6,2,4),),
  ((B, R),): ((9,11,1,4,7),),
  ((B, T),): ((9,2,4,7),),
  ((B, L),): ((9,5,7),),
  # two border segments
  ((T, R),(R, T)): ((0,2,3,11),),
  ((R, T),(T, R)): ((2,0,1),(3,4,7,10,11)),
  ((L,R),(R,T)): ((0,2,4,6,11),),
  ((T,R),(R,L)): ((3,0,1),(5,7,10,11)),
  ((B,R),(R,T)): ((0,2,4,7,9,11),),
  ((T,R),(R,B)): ((3,0,1),(8,10,11)),
  ((R,T),(T,L)): ((0,2,3,5,7,10),),
  ((L,T),(T,R)): ((2,11,1),(3,4,6)),
  ((R,T),(T,B)): ((0,2,3,8,10),),
  ((B,T),(T,R)): ((2,11,1),(3,4,7,9)),
  ((R,T),(L,B)): ((0,2,4,6,8,10),),  # 6
  ((B,L),(T,R)): ((11,3,1),(5,7,9)), # 6
  ((L,R),(R,L)): ((0,5,6,11),),
  ((R,L),(L,R)): ((0,1,4,5),(6,7,10,11)),
  ((B,R),(R,L)): ((0,5,7,9,11),),
  ((L,R),(R,B)): ((0,1,4,6),(11,8,10)),
  ((T,L),(L,R)): ((1,3,5,6,11),),
  ((R,L),(L,T)): ((2,4,5),(6,7,10,0)),
  ((R,L),(L,B)): ((0,5,6,8,10),),
  ((B,L),(L,R)): ((11,1,4,5),(6,7,9)),
  ((B,R),(R,B)): ((0,8,9,11),),  # 11
  ((R,B),(B,R)): ((0,1,4,7,8),(11,9,10)), #11
  ((B,R),(T,L)): ((11,1,3,5,7,9),),
  ((L,T),(R,B)): ((2,4,6),(0,8,10)),
  ((T,B),(B,R)): ((3,8,9,11,1),),
  ((R,B),(B,T)): ((2,4,7,8),(9,10,0)),
  ((L,B),(B,R)): ((4,6,8,9,11,1),),
  ((R,B),(B,L)): ((5,7,8),(9,10,0)),
  ((T,L),(L,T)): ((3,5,6,2),),
  ((L,T),(T,L)): ((3,4,5),(6,7,10,1,2)),
  ((B,T),(T,L)): ((3,5,7,9,2),), # 16
  ((L,T),(T,B)): ((3,4,6),(8,10,1,2)), #16
  ((T,L),(L,B)): ((3,5,6,8,10,1),),
  ((B,L),(L,T)): ((2,4,5),(6,7,9)),
  ((B,T),(T,B)): ((2,3,8,9),),
  ((T,B),(B,T)): ((3,4,7,8),(9,10,1,2)),
  ((L,B),(B,T)): ((2,4,6,8,9),) ,
  ((T,B),(B,L)): ((5,8,7),(9,10,1,3)),
  ((B,L),(L,B)): ((6,8,9,5),),
  ((L,B),(B,L)): ((6,7,8),(9,10,1,4,5)),
  (): (),
  ((),()): ((1,4,7,10),),
  ((R,R),): ((0,12,15,11),),
  ((T,T),): ((3,13,12,2),),
  ((L,L),): ((6,14,13,5),),
  ((B,B),): ((9,15,14,8),)
}

tiles = list(tileByBorder.values())

def tileSet():
  img = Image.new(mode="L", size=(6*30,9*30), color=128)
  draw = ImageDraw.Draw(img)
  for y in range(9):
    for x in range(6):
        drawTileByNumber(draw,x,y,y*6+x)
  img.save(f'tiles.png', "png")

def drawTileByNumber(draw, x, y, tileNo):
  drawTile(draw, x, y, ttiles[tileNo])

def drawTileBySegments(draw, x, y, segments):
  tile = segments in tileByBorder and tileByBorder[segments] or None
  if tile==None:
    reversedSegments = tuple(reversed(segments))
    tile = reversedSegments in tileByBorder and tileByBorder[reversedSegments] or None
  if tile==None:
    if segments != ():
      print(f'Not found: {segments}')
  else:
    drawTile(draw, x, y, tile)

def drawTile(draw, x, y, tile):
  for poly in tile:
    points = [(coords[p][0]+x*30, coords[p][1]+y*30) for p in poly]
    draw.polygon(points, fill=255, outline=0)

if __name__ == "__main__":
  tileSet()

