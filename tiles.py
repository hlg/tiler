from enum import Enum
from itertools import groupby

class Borders(Enum):
  W = (0, (False,))
  L = (1, (True,))
  WL = (2, (False, True))
  LW = (3, (True, False))
  WLW = (4, (False, True, False))
  LWL = (5, (True, False, True))

  def __init__(self, ordinal, landWater):
    self.ordinal = ordinal
    self.landWater = landWater

  def __str__(self):
    return str(self.ordinal) + '-' +''.join(['L' if lw else 'W' for lw in  self.landWater])
  def __repr__(self):
    return self.__str__()

def countSegments(bl):
  lwLine = [lw for b in bl for lw in b.landWater]
  lwLine.append(lwLine[0])
  return int(sum([1 for lw1, lw2 in zip(lwLine[:-1], lwLine[1:]) if lw1!=lw2])/2)
for b in list(Borders):
  print(b)

def borderLine(edges, head = []):
  if edges == 0:
    if head == [] or head[-1].landWater[-1] == head[0].landWater[0]:
      return [head]
    else:
      return []
  result = []
  for b in list(Borders):
      if head == [] or b.landWater[0] == head[-1].landWater[-1]:
        result += borderLine(edges-1, head = head+[b])
  return result
    
for bl in borderLine(4):
  print(bl, int(countSegments(bl)))

blSorted = sorted(borderLine(4), key=countSegments)
for s,bl in groupby(blSorted, key=countSegments):
  blList = list(bl)
  print(s, len(blList))
  for b in blList:
    print(b)
  
# LW WL LW WL is ambiguous without segments
# LWL L LWL L / WLW W WLW W and similar are ambiguous with segments only

