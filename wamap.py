mapWidth=73
mapHeight=89
tileSize= 32
exit="map.json"


def exitLayer(name, layerId, exitTile, exitCoords, exitUrl, visible=True):
  data = [0] * (mapWidth*mapHeight)
  for (x,y) in exitCoords:
    data[y*mapHeight+x] = exitTile
  layer = tileLayer(name, layerId, data, visible)
  layer["properties"] = [{
      "name":"exitSceneUrl",
      "type":"string",
      "value": exitUrl
  }]
  return layer

def linkLayer(name, layerId, linkTile, linkCoords, linkUrl, visible=True):
  data = [0] * (mapWidth*mapHeight)
  for (x,y) in linkCoords:
    data[y*mapHeight+x] = linkTile
  layer = tileLayer(name, layerId, data, visible)
  layer["properties"] = [{
      "name":"openWebsite",
      "type":"string",
      "value": linkUrl
  }]
  return layer

def tileLayer(name, layerId, data, visible=True):
  layer = baseLayer(name, layerId, "tilelayer", visible)
  layer["data"] = data
  return layer 

def imageLayer(name, layerId, image, visible=True):
  layer = baseLayer(name, layerId, "imageLayer", visible)
  layer["image"] = image
  return layer 

def objectLayer(name, layerId, objects, visible=True):
  layer = baseLayer(name, layerId, "objectgroup", visible)
  layer["objects"] = objects
  return layer

def baseLayer(name, layerId, layerType, visible=True):
  return {
    "name": name,
    "id": layerId,
    "x":0,
    "y":0,
    "width":mapWidth,
    "height":mapHeight,
    "visible": visible,
    "opacity":1,
    "type": layerType
  }

def island(data, start):
  return {
    "compressionlevel":-1,
    "version":1.4,
    "type":"map",
    "width":mapWidth,
    "height":mapHeight,
    "infinite":False,
    "orientation":"orthogonal",
    "renderorder":"right-down",
    "tilewidth":tileSize,
    "tileheight":tileSize,
    "tilesets":[{
      "columns":4,
      "firstgid":1,
      "image":"beachline.png",
      "imageheight":512,
      "imagewidth":128,
      "margin":0,
      "name":"Beachline",
      "spacing":0,
      "tilecount":62,
      "tileheight":tileSize,
      "tilewidth":tileSize,
      "tiles":[{
        "id":0,
        "properties":[{
          "name":"collides",
          "type":"bool",
          "value":True
        }]
      }]
    }],
    "layers": [
      # exitLayer("exit", 2, 1, [], exit),
      # linkLayer("link", 3, 1, (), "https:\/\/hlg.github.io\/wamap\/caleidoscope\/index.html"),
      # imageLayer("image", 4, "..\/..\/Downloads\/Ruegen2.png", visible=False), 
      tileLayer("start", 1, start),
      tileLayer("tiles", 2, data),
      objectLayer("floorLayer", 5, [])
    ]
  }

if __name__ == "__main__":
  import json
  import sys
  dataFile = len(sys.argv)>1 and sys.argv[1] or "island-data-1434381.json"
  with open(dataFile) as dataJson:
    data = json.load(dataJson)
    index = [d+1 for d in data["index"]]
  mapWidth = data["width"]
  mapHeight = data["height"]
  start = [2 if d==2 else 0 for d in index]
  tiled = island(index, start)
  with open(dataFile.replace('data', 'map'),'w') as f:
    json.dump(tiled, f, indent=4)

