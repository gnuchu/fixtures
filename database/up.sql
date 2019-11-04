create table fixtures(
  id integer primary key autoincrement,
  gameday int not null, 
  date text not null, 
  time string not null, 
  hometeam text not null, 
  awayteam not null
);