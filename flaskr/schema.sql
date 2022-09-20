DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS carpark;

CREATE TABLE device (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE carpark (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pos1 INTEGER NOT NULL,
  pos2 INTEGER NOT NULL,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  colour TEXT NOT NULL,
  stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
);