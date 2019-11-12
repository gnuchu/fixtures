# Run pip install -r requirements.txt on first install

import requests
import json
import os.path
from datetime import datetime
from datetime import timedelta
import time
from openpyxl import Workbook
import sqlite3
import yaml
import sys

################
# Functions
################
def read_templates():
  templates = {}
  header = ""
  footer = ""
  thead = ""
  tfoot = ""

  with open('templates/header.html') as f:
    header = f.read()
  with open('templates/footer.html') as f:
    footer = f.read()
  with open('templates/tableheader.html') as f:
    thead = f.read()
  with open('templates/tablefooter.html') as f:
    tfoot = f.read()

  templates['header'] = header
  templates['footer'] = footer
  templates['thead'] = thead
  templates['tfoot'] = tfoot
  return templates

def build_html(json, outputfile):
  templates = read_templates()
  html = ""
  html += templates['header']
  html += templates['thead']
  currentpoints = 0
  i = 0

  for fixture in json_data['api']['fixtures']:
    league_id = int(fixture['league_id'])
    if league_id != 755:
      continue
    
    i += 1

    row = process_fixture(i, fixture, currentpoints)
    gameday = row[0]
    gamedate = row[1]
    gametime  = row[2]
    hometeam = row[3]
    awayteam = row[4]
    homescore = row[5]
    awayscore = row[6]
    result = row[7]
    fixture_id = row[9]

    if result == 'Win':
      currentpoints += 3
    elif result == 'Draw':
      currentpoints += 1
    
    if homescore == '':
      currentpoints = ''

    htmlrow = f"""<tr>
      <td>{gameday}<br/><small>{fixture_id}</small></td>
      <td>{hometeam}</td>
      <td>{homescore}</td>
      <td>{awayscore}</td>
      <td>{awayteam}</td>
      <td>{gamedate}</td>
      <td>{gametime}</td>
      <td>{result}</td>
      <td>{currentpoints}</td>
    </tr>"""
    html+=htmlrow

  html += templates['tfoot']
  html += templates['footer']

  with open(outputfile, 'w') as f:
    f.write(html)

def load_secrets(path):
  if os.path.exists(path) == False:
    print('Need to create secrets file: {path}')
    sys.exit(1)

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
  staleDate = datetime.now() + timedelta(hours=-1)

  if lastModifiedDatetime < staleDate:
    return True

  return False

def get_modified_time(file):
  formatstring = '%d-%m-%Y %H:%M:%S'
  modsSecs = os.path.getmtime(file)
  date_str = time.strftime(formatstring, time.localtime(modsSecs))
  date_o = datetime.strptime(date_str, formatstring)

  return date_o

def calculate_result(homescore, awayscore, homeoraway):
  home = int(homescore)
  away = int(awayscore)
  
  if home == away:
    return 'Draw'
  
  if homeoraway == 'H':
    if home > away:
      return 'Win'
    else:
      return 'Loss'
  else:
    if home > away:
      return 'Loss'
    else:
      return 'Win'

  
def home_or_away(fixture):
  if int(fixture['homeTeam']['team_id']) == int(st_pauli_team_id):
    return 'H'
  else:
    return 'A'

def process_fixture(gameday, fixture, currentpoints):
  matchdate = fixture['event_date']
  hometeam = fixture['homeTeam']['team_name']
  awayteam = fixture['awayTeam']['team_name']
  
  date_o = datetime.fromisoformat(matchdate)
  date_str = date_o.strftime("%d/%m/%Y")
  time_str = date_o.strftime("%H:%M:%S")
  fixture_id = fixture['fixture_id']

  if fixture['score']['fulltime'] == None:
    homescore = ""
    awayscore = ""
    result = ""
  else:
    score = fixture['score']['fulltime']
    (homescore,awayscore) = score.split('-')
    homeoraway = home_or_away(fixture)
    result = calculate_result(homescore, awayscore, homeoraway)

    if result == 'Draw':
      currentpoints += 1
    elif result == 'Win':
      currentpoints += 3
  
  row = [gameday, date_str, time_str, hometeam, awayteam, homescore, awayscore, result, currentpoints, fixture_id]
  return row

def request_new_data(json_file_path):
  headers = {}
  headers['x-rapidapi-host'] = api_host
  headers['x-rapidapi-key'] = api_key

  url_to_get = api_base_url + api_service + st_pauli_team_id
  response = requests.request(api_method, url_to_get, headers=headers)
  j = json.loads(response.text)
  # Save the data off just in case
  f = open(json_file_path, 'w')
  f.write(json.dumps(j))
  f.close()

  return j

def process_fixtures(json_data, xlsx_file_path, conn):
  i = 0
  # Process fixtures
  wb = Workbook()
  ws = wb.active
  ws.title = 'Fixtures'
  currentpoints = 0
  #Write headers
  ws.append(['Game Day', 'Date', 'Time', 'Home', 'Away', 'Home Score', 'Away Score', 'Points'])

  for fixture in json_data['api']['fixtures']:
    league_id = int(fixture['league_id'])
    if league_id != 755:
      continue

    i += 1
    row = process_fixture(i, fixture, currentpoints)
    ws.append(row)
    insert_row(conn, row)

  wb.save(xlsx_file_path)

def run_sql(conn, sql):
  c = conn.cursor()
  c.execute(sql)
  conn.commit()

def drop_database(conn):
  run_sql(conn, 'delete from fixtures')

def insert_row(conn, row):
  gameday = row[0]
  gamedate = row[1]
  gametime  = row[2]
  hometeam = row[3]
  awayteam = row[4]
  homescore = row[5]
  awayscore = row[6]
  result = row[7]
  fixture_id = row[9]

  sql = f'''insert into fixtures(gameday, gamedate, gametime, hometeam, awayteam, homescore, awayscore, result, fixture_id)
           values ('{gameday}', '{gamedate}', '{gametime}', '{hometeam}', '{awayteam}', '{homescore}', '{awayscore}', '{result}', '{fixture_id}')'''

  run_sql(conn, sql)


################
# Start
################
json_data = {}
api_host = 'api-football-v1.p.rapidapi.com'
api_method = 'GET'
api_base_url = 'https://api-football-v1.p.rapidapi.com/v2'
api_service = '/fixtures/team/'
st_pauli_team_id = '186'

secrets_file_path = '.secrets.yaml'
secrets = load_secrets(secrets_file_path)
api_key = secrets['api_key']

json_file_path = 'output/fixtures.json'
html_file_path = 'output/fixtures.html'
xlsx_file_path = 'output/fixtures' + datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'

# database
conn = sqlite3.connect('database/fixtures.db')
drop_database(conn)

if os.path.exists(json_file_path) == True and is_stale(json_file_path) == False:
  with open(json_file_path) as f:
    json_data = json.load(f)
else:
  json_data = request_new_data(json_file_path)

process_fixtures(json_data, xlsx_file_path, conn)
build_html(json_data, html_file_path)
conn.close()


