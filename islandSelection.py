from tile import jsonFromPolygon, jsonFromFile, multiPolyCoords, createMap, scaleFor, createTileIndex
import os, math, json, wamap

class Island:
  def __init__(self, name, zoom, polygon):
    self.name = name
    self.zoom = zoom 
    self.polygon = polygon

islands = [
  # Island("New Guinea", 6, 3986076), # downloaded, but segmentation fails
  # Island("Borneo", 6, 3986083), # extent 0?
  # Island("Great Britain", 6, 6038068), # broken
  Island("Sulawesi", 6, 3986124),
  # Island("North Island NZ", 6, 6571744), # segmentation fails
  Island("Ireland", 7, 7681896),
  Island("Cuba", 7, 7117025), # segmentation fails
  Island("Iceland", 7, 7681889),
  Island("Hokkaido", 7, 6679920),
  Island("Sardinia", 8, 6847723),
  Island("Tasmania", 8, 4097659), # tile index range
  Island("Taiwan", 8, 7219605), # tile index range
  Island("Hainan", 9, 4094778), # tile index range
  Island("Sicilia", 9, 6197225),
  Island("Hawaii", 9, 3403603),
  Island("Corsica", 9, 7112309),
  Island("Sjaelland", 9, 5175856),
  Island("Jamaica", 9, 7117041),
  Island("West Falkland", 9, 3182529),
  Island("Tenerife", 10, 2108882),
  Island("Majorca", 10, 6803636),
  Island("Falster", 10, 5178556),
  Island("Ruegen", 10, 1434381),
  Island("Bali", 10, 2130352),
  Island("Long Island", 10, 3955977),
  Island("Fischland", 11, 10650535),
  Island("Usedom", 11, 3791269),
  Island("Bornholm", 11, 5176019),
  Island("Maui", 11, 3403431),
  Island("Bintan", 11, 6561978),
  Island("Moen", 11, 5175925), 
  Island("Sylt", 11, 1576925),
  Island("La Gomera", 12, 2214684),
  Island("Elba", 12, 3259001),
  Island("Singapore", 12, 1769123),
  Island("Hiddensee", 12, 3790660),
  Island("Amrum", 12, 3787117),
  Island("Molokai", 12, 1082120),
  # Island("Ummanz", 13, 3791309), # segmentation issue
  Island("Poel", 13, 3790804),
  Island("Borkum", 13, 3788971),
  Island("Ubin", 14, 2243165),
  Island("Vilm", 14, 3791270),
  Island("Helgoland", 15, 3787052)
]

def downloadList():
  for island in islands:
    print(island.name)
    geoJson = download(island.name, island.polygon)
    downloadSimplified(geoJson, island.name, island.polygon)

def downloadSimplifiedList():
  for island in islands:
    print(island.name)
    geoJson = jsonFromFile("selectedIslands/"+island.name.replace(" ","")+"_original.json")
    downloadSimplified(geoJson, island.name, island.polygon)

def downloadOriginal(name, polygon):
    if not os.path.exists("selectedIslands"):
      try:
        os.makedirs("selectedIslands")
      except OSError as exc:
        if exc.errno != errno.EEXIST:
          raise 
    geoJson = jsonFromPolygon(polygon, params=None)
    with open("selectedIslands/"+name.replace(" ","")+"_original.json", "w") as geoJsonFile:
      json.dump(geoJson, geoJsonFile) 
    return geoJson

def downloadSimplified(geoJson, name, polygon):
    ext = latLongExtension(geoJson)/750
    geoJsonSimplified = jsonFromPolygon(polygon, params=(0.,ext,ext))
    with open("selectedIslands/"+name.replace(" ","")+"_simplified.json", "w") as geoJsonFile:
      json.dump(geoJsonSimplified, geoJsonFile) 

def latLongExtension(geoJson):
    multiPoly = multiPolyCoords(geoJson)
    outlineLongLat = max([poly[0] for poly in multiPoly],key=len)
    maxLong = max([longLat[0] for longLat in outlineLongLat])
    minLong = min([longLat[0] for longLat in outlineLongLat])
    maxLat = max([longLat[1] for longLat in outlineLongLat])
    minLat = min([longLat[1] for longLat in outlineLongLat])
    return max([maxLong-minLong, maxLat-minLat])

def readAndMap(action):
 for island in islands:
    shortIslandName = island.name.replace(" ","")
    geoJson = jsonFromFile("selectedIslands/"+shortIslandName+"_simplified.json")
    print("==============")
    print(island.name, island.zoom, scaleFor(geoJson))
    print("simplification factor: ", latLongExtension(geoJson)/750)
    action(geoJson, shortIslandName)

def image(geoJson, shortIslandName):
  img = createMap(geoJson)
  img.save('selectedIslands/'+shortIslandName+".png")
   
def tileIndex(geoJson, shortIslandName):
  data = createTileIndex(geoJson)
  wamap.mapWidth = data["width"]
  wamap.mapHeight = data["height"]
  index = [d+1 for d in data["index"]]
  start = [2 if d1==2 and d2>2  else 0 for (d1,d2) in zip(index[:-1],index[1:])] + [0]
  mapJson = wamap.island(index, start)
  with open('selectedIslands/'+shortIslandName+'-map.json', 'w') as f:
    json.dump(mapJson, f)

def islandIndex():
  for island in islands:
    shortIslandName = island.name.replace(" ","")
    print('* {name}: [WA graphic]({wa}), [WA sand]({sand}), [OSM]({osm}), [Wikipedia]({wiki})'.format(
      name=island.name, 
      wa='islands/abstract/'+shortIslandName+'-map.json',
      sand='islands/sand/'+shortIslandName+'-map.json',
      osm='https://www.openstreetmap.org/relation/'+str(island.polygon),
      wiki='https://en.wikipedia.org/wiki/'+island.name
    ))

if __name__ == "__main__":
  readAndMap(tileIndex)
  # readAndMap(image)
  # downloadSimplifiedList()
 
