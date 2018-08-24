-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS post;

CREATE DATABASE `test` DEFAULT CHARACTER SET latin1 COLLATE latin1_general_ci;    
USE `test`;    

create table `POLYGON` (
	`POLY_ID` int NOT NULL,
	-- `POLY_STRING` varchar(255) NOT NULL,
	`POLY_NAME` varchar(255) NOT NULL,
	`TYPE` varchar(255) NOT NULL,
	-- `PROPERTY` varchar(255) NOT NULL,   	
	primary key (`POLY_ID`)
);


CREATE TABLE `POINTS` (
	`POLY_ID` int,
	`POINT_ID` int NOT NULL,
	`COORD_X` float NOT NULL,
	`COORD_Y` float NOT NULL,
	primary key(`POINT_ID`),
	FOREIGN KEY (`POLY_ID`) REFERENCES POLYGON(`POLY_ID`)
);

create table POINTS_OF_INTEREST (
	`POINT_INTEREST_ID` int NOT NULL,
	`COORD_X` float NOT NULL,
	`COORD_Y` float NOT NULL,
	primary key(`POINT_INTEREST_ID`)
);

-- INSERT INTO `POLYGON` VALUES (1,
-- 					"[123.825, -107.185],[191.123, -71.766],[125.346, -85.035]",
-- 					"root");

-- INSERT INTO `POINTS` VALUES (1,10.0,20.0, 1);
-- INSERT INTO `POINTS` VALUES (2,20.0,40.0, 2);

-- INSERT INTO `POLYGON` VALUES (2,
-- 					"[123.825, -107.185],[191.123, -71.766],[125.346, -85.035]",
-- 					"root");

