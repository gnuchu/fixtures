import requests
import json
import os.path
from datetime import datetime
from openpyxl import Workbook

def process_date(d):
  datetime_object = datetime.fromisoformat(d)
  date_str = datetime_object.strftime("%d/%m/%Y")
  time_str = datetime_object.strftime("%T")


json_data = {}

if os.path.exists('fixtures.json'):
  print("Loading from file...")
  #Load exitsing fixture to save on api limits.
  #Implement staleness check here.
  with open('fixtures.json') as f:
    json_data = json.load(f)
else:
  print("Loading from web...")
  headers = {}
  headers['x-rapidapi-host'] = 'api-football-v1.p.rapidapi.com'
  headers['x-rapidapi-key'] = 'FsCmAMgX9wmshWzee5mkjIKYDNGup1uXi63jsnaZYcBBNBAg4L'

  url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/team/186"

  method = 'GET'
  response = requests.request(method, url, headers=headers)
  json_data = json.loads(response.text)
  # Save the data off just in case
  f = open('fixtures', 'w')
  f.write(json.dumps(json_data))
  f.close()

i = 0
# Process fixtures
csv = ""
sheetHeaders = "GameDay|Date|Time|HomeTeam|AwayTeam\n"
csv += sheetHeaders

for fixture in json_data['api']['fixtures']:
  league_id = int(fixture['league_id'])
  if league_id != 755:
    continue

  i+=1
  matchdate = fixture['event_date']
  hometeam = fixture['homeTeam']['team_name']
  awayteam = fixture['awayTeam']['team_name']
  date_o = datetime.fromisoformat(matchdate)
  date_str = date_o.strftime("%d/%m/%Y")
  time_str = date_o.strftime("%T")

  csv += f"{i}|{date_str}|{time_str}|{hometeam}|{awayteam}\n"

f = open('fixture.csv', 'w')
f.write(csv)
f.close()

