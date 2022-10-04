DROP TABLE IF EXISTS carpark;
DROP TABLE IF EXIST s_carpark;

CREATE TABLE carbays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  carparkname TEXT FOREIGN KEY NOT NULL,
  p1 TEXT NOT NULL,
  p2 TEXT NOT NULL,
  p3 TEXT NOT NULL,
  p4 TEXT NOT NULL,
  status TEXT NOT NULL,
  date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_carpark
      FOREIGN KEY (carparkid)
      REFERENCES carpark (carparkid)
);

CREATE TABLE s_carpark (
  carparkname TEXT PRIMARY KEY,
  imageurl TEXT NOT NULL,
);