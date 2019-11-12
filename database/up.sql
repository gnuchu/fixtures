create table fixtures(
  id integer primary key autoincrement,
  gameday int not null, 
  gamedate text not null, 
  gametime string not null, 
  hometeam text not null, 
  awayteam not null,
  homescore int,
  awayscore int,
  result text,
  fixture_id text
);