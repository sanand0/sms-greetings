CREATE DATABASE  `sanand_greeting` ;

Grant privileges to sanand_gr/sanand to this database

CREATE TABLE  `sanand_greeting`.`greeting` (
`id` INT NOT NULL AUTO_INCREMENT ,
`user` INT NOT NULL ,
`time` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
`mobile` VARCHAR( 250 ) NOT NULL ,
`name` VARCHAR( 250 ) NOT NULL ,
`event` VARCHAR( 250 ) NOT NULL ,
`date` DATE NOT NULL ,
`relation` VARCHAR( 250 ) NOT NULL ,
`message` TEXT NOT NULL ,
PRIMARY KEY (  `id` ) ,
INDEX (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE `sanand_greeting`.`sessions` (
`session_id` CHAR(128) UNIQUE NOT NULL,
`atime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
`data` TEXT
) ENGINE MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE  `sanand_greeting`.`login` (
`id` VARCHAR( 250 ) NOT NULL ,
`user` INT NOT NULL ,
`attr` TEXT NOT NULL ,
PRIMARY KEY (  `id` ) ,
INDEX (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE  `sanand_greeting`.`user` (
`user` INT NOT NULL AUTO_INCREMENT ,
`mobile` VARCHAR(250),
PRIMARY KEY (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;
