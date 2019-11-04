import requests
import json
import os.path
from datetime import datetime, timedelta
import time
from openpyxl import Workbook
import sqlite3
import yaml

################
# Functions
################
def load_secrets(path):
  with open(path, 'r') as stream:
    try:
      secrets = yaml.load(stream, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
      print(exc)
  
  return secrets

def is_stale(file):
  # Define stale as not updated since yesterday or not present.
  if os.path.exists(file) == False:
    return True
  
  lastModifiedDatetime = get_modified_time(file)
  staleDate = datetime.now() + timedelta(days=-1)

  if lastModifiedDatetime < staleDate:
    return True

  return False

def get_modified_time(file):
  formatstring = '%d-%m-%Y %H:%M:%S'
  modsSecs = os.path.getmtime(file)
  date_str = time.strftime(formatstring, time.localtime(modsSecs))
  date_o = datetime.strptime(date_str, formatstring)

  return date_o

def process_fixture(gameday, fixture):
  matchdate = fixture['event_date']
  hometeam = fixture['homeTeam']['team_name']
  awayteam = fixture['awayTeam']['team_name']
  
  date_o = datetime.fromisoformat(matchdate)
  date_str = date_o.strftime("%d/%m/%Y")
  time_str = date_o.strftime("%H:%M:%S")

  row = [gameday, date_str, time_str, hometeam, awayteam]
  return row

def request_new_data(json_file_path):
  headers = {}
  headers['x-rapidapi-host'] = api_host
  headers['x-rapidapi-key'] = api_key

  url_to_get = api_base_url + api_service + team_id
  response = requests.request(api_method, url_to_get, headers=headers)
  j = json.loads(response.text)
  # Save the data off just in case
  f = open(json_file_path, 'w')
  f.write(json.dumps(j))
  f.close()

  return j

def process_fixtures(json_data, xlsx_file_path):
  i = 0
# Process fixtures
  wb = Workbook()
  ws = wb.active
  ws.title = 'Fixtures'
  #Write headers
  ws.append(['Game Day', 'Date', 'Time', 'Home', 'Away'])

  for fixture in json_data['api']['fixtures']:
    league_id = int(fixture['league_id'])
    if league_id != 755:
      continue

    i += 1
    row = process_fixture(i, fixture)

    row = [str(i), date_str, time_str, hometeam, awayteam]
    ws.append(row)

  wb.save(xlsx_file_path)
################
# Start
################
json_data = {}
api_host = 'api-football-v1.p.rapidapi.com'
api_method = 'GET'
api_base_url = 'https://api-football-v1.p.rapidapi.com/v2'
api_service = '/fixtures/team/'
team_id = '186'

secrets_file_path = '.secrests.yaml'
secrets = load_secrets(secrets_file_path)
api_key = secrets['api_key']

json_file_path = 'output/fixtures.json'
xlsx_file_path = 'output/fixtures.xlsx'


if os.path.exists(json_file_path) == True and is_stale(json_file_path) == False:
  print("Loading from file...")
  with open(json_file_path) as f:
    json_data = json.load(f)
else:
  print("Loading form Web...")
  json_data = request_new_data(json_file_path)

process_fixtures(json_data, xlsx_file_path)


