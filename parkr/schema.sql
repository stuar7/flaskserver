CREATE TABLE s_carpark (
  carparkname TEXT PRIMARY KEY,
  imageurl TEXT NOT NULL,
);

CREATE TABLE carbays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  carparkname TEXT NOT NULL,
  p1 TEXT NOT NULL,
  p2 TEXT NOT NULL,
  p3 TEXT NOT NULL,
  p4 TEXT NOT NULL,
  status TEXT NOT NULL,
  date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_carpark
      FOREIGN KEY (carparkname)
      REFERENCES carpark (carparkname)
);

CREATE TABLE sensorlog (
	logid	INTEGER,
	carparkname	TEXT NOT NULL,
	status	TEXT NOT NULL,
	date	TEXT NOT NULL,
	PRIMARY KEY(logid AUTOINCREMENT)
);