CREATE DATABASE  `sanand_greeting` ;
GRANT ALL PRIVILEGES ON  `sanand_greeting` . * TO  'sanand_gr'@'localhost' WITH GRANT OPTION ;

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
`user` INT NOT NULL AUTO_INCREMENT,
`attr` TEXT NOT NULL ,
PRIMARY KEY (  `id` ) ,
INDEX (  `user` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE  `sanand_greeting`.`mobile` (
`mobile` VARCHAR( 250 ) NOT NULL,
`name` VARCHAR( 250 ) NOT NULL,
`password` VARCHAR( 250 ) NOT NULL,
PRIMARY KEY (  `mobile` )
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci ;
