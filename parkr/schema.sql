CREATE TABLE carparkregistry (
  carparkname TEXT PRIMARY KEY,
  imageurl TEXT NOT NULL,
);

CREATE TABLE "carpark" (
	"id"	NUMERIC,
	"p1"	TEXT NOT NULL,
	"p2"	TEXT NOT NULL,
	"p3"	TEXT NOT NULL,
	"p4"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	PRIMARY KEY("id")
)

CREATE TABLE "snapshot" (
	"carparkname"	TEXT,
	"BAYS_EMPTY"	INTEGER NOT NULL,
	"BAYS_FULL"	INTEGER NOT NULL,
	"BAYS_UNKNOWN"	INTEGER NOT NULL,
	"date"	INTEGER,
	PRIMARY KEY("carparkname","date")
);

CREATE TABLE "sensorlog" (
	"logid"	INTEGER,
	"carparkname"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	"date"	TEXT NOT NULL,
	"id"	INTEGER NOT NULL,
	PRIMARY KEY("logid" AUTOINCREMENT)
)