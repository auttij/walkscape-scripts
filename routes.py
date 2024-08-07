from file_utils import read_json

def route_lengths():
  route_data = read_json('data/routes.json')
  parsed = {}

  distances = { 
    'veryShort': 450, 
    'short': 550, 
    'extremelyNear': 160, 
    'veryNear': 280, 
    'near': 390, 
    'lowModerate': 650, 
    'moderate': 800, 
    'moderateHigh': 1000, 
    'lowHigh': 1300,
  }

  for route in route_data:
    dist = distances[route['distance']]
    name = " to ".join(route['id'].split('-')[1:3])
    parsed[name] = int(dist * route['distanceModifier'])

  s = dict(sorted(parsed.items(), key=lambda item: item[1]))
  for name, dist in s.items():
    print(name, dist)


def main():
  route_lengths()
  pass

if __name__ == '__main__':
  main()