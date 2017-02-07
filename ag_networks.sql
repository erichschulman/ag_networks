
CREATE TABLE `farms` ( 
	`farmid` INTEGER,
	`lat` REAL,
	`long` REAL,
	PRIMARY KEY(`farmid`) 
);

CREATE TABLE `proc` (
 `procid` INTEGER,
 `lat` REAL,
 `long` REAL,
 `type` TEXT,
  PRIMARY KEY(`procid`) 
 );

CREATE TABLE `stores` ( 
	`storeid` INTEGER,
	`lat` REAL,
	`long` REAL,
    `sqftg` INTEGER,
	PRIMARY KEY(`storeid`)
);


CREATE TABLE `` (
	`farmid`	INTEGER,
	`procid`	INTEGER,
	`linedist`	INTEGER,
	`routdist`	INTEGER
	FOREIGN KEY(farmid)
		REFERENCES farms(farmid)
	FOREIGN KEY (procid)
		REFERENCES proc(procid)
);