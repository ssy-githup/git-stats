/******************************************/
/*   DatabaseName = test_mysql   */
/*   TableName = commit_stats   */
/******************************************/
CREATE TABLE `commit_stats` (
  `﻿group` varchar(255) DEFAULT NULL COMMENT 'group/subgroup',
  `project` varchar(255) DEFAULT NULL COMMENT 'project',
  `email` varchar(255) DEFAULT NULL COMMENT 'person email',
  `name` varchar(255) NOT NULL COMMENT 'commit name',
  `author_name` varchar(255) NOT NULL COMMENT 'nick name',
  `additions` varchar(255) NOT NULL COMMENT 'additions code lines',
  `deletions` varchar(255) NOT NULL COMMENT 'deletions code lines',
  `total` varchar(255) NOT NULL COMMENT ' total commit code lines',
  `commit_count` varchar(255) NOT NULL COMMENT 'commit count',
  `start_at` datetime NOT NULL COMMENT 'start of collection time',
  `end_at` datetime NOT NULL COMMENT 'end of collection time',
  `timespan` int(10) unsigned NOT NULL COMMENT 'statistical time',
  KEY `idx_group` (`﻿group`),
  KEY `idx_project` (`project`),
  KEY `idx_name` (`author_name`),
  KEY `idx_time` (`timespan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 AVG_ROW_LENGTH=606 COMMENT='commit statistical infomation'
;





/* -------------------------------------------------------------------
/* -------------- 时间维度 --------------------------------------------
/* -------------------------------------------------------------------


CREATE PROCEDURE `sp_gen_dict_date`()
	DETERMINISTIC

BEGIN
	DECLARE count int default 0;
DECLARE startDay DATE DEFAULT '2020-01-01';
DECLARE endDay DATE DEFAULT '2050-12-31';
DECLARE out_status VARCHAR(200) DEFAULT 'OK';
DECLARE CONTINUE HANDLER  
FOR 1062
SET out_status='Duplicate Entry';
-- 异常处理方式完毕

DROP TABLE IF EXISTS `aa_dict_date`;
CREATE TABLE `aa_dict_date` (
    `add_id` int(8) NOT NULL,
    `add_date` date NOT NULL,
    `add_date_index` int(8) NOT NULL,
    `add_year` int(4) NOT NULL,
    `add_month` int(2) NOT NULL,
    `add_day` int(2) NOT NULL,
    `add_week` int(1) NOT NULL,
    `add_quarter` int(1) NOT NULL,
    `add_day_of_week` int(1) NOT NULL,
    `add_day_of_year` int(3) NOT NULL,
    `add_date_name` CHAR(10) NOT NULL,
    `add_week_name` CHAR(8) NOT NULL,
    `add_month_name` CHAR(7) NOT NULL,
    `add_quarter_name` CHAR(7) NOT NULL,
    `add_year_name` CHAR(4) NOT NULL
)ENGINE=Innodb DEFAULT CHARSET=utf8;

WHILE startDay <= endDay DO
    SET count = count + 1;
    INSERT INTO `aa_dict_date`
    (
        `add_id`,
        `add_date`,
        `add_date_index`,
        `add_year`,
        `add_month`,
        `add_day`,
        `add_week`,
        `add_quarter`,
        `add_day_of_week`,
        `add_day_of_year`,
        `add_date_name`,
        `add_week_name`,
        `add_month_name`,
        `add_quarter_name`,
        `add_year_name`
    )
    VALUES
    (
        count,
        startDay,
        cast(DATE_FORMAT(startDay, '%Y%m%d') AS UNSIGNED),
        YEAR(startDay),
        MONTH(startDay),
        DAY(startDay),
        WEEK(startDay,5),
        QUARTER(startDay),
        WEEKDAY(startDay) + 1,
        DAYOFYEAR(startDay),
        DATE_FORMAT(startDay, '%Y-%m-%d'),
        CONCAT(DATE_FORMAT(startDay, '%Y-W'), LPAD(WEEK(startDay,5) + IF(WEEK(DATE_FORMAT(startDay, '%Y-01-01'),5) = 0, 1, 0), 2, 0)), -- 如果当年的第一周的周数为0，所有周数+1
        CONCAT(DATE_FORMAT(startDay, '%Y-%m')),
        CONCAT(DATE_FORMAT(startDay, '%Y-Q'), QUARTER(startDay)),
        YEAR(startDay)
    );
    SET startDay = DATE_ADD(startDay, INTERVAL 1 DAY);
END WHILE;

ALTER TABLE `aa_dict_date` 
    ADD PRIMARY KEY (`add_id`) USING BTREE,
    ADD KEY `aa_dict_date_n1` (`add_date`) USING BTREE,
    ADD KEY `aa_dict_date_n2` (`add_date_index`) USING BTREE,
    ADD KEY `aa_dict_date_n3` (`add_month`) USING BTREE,
    ADD KEY `aa_dict_date_n4` (`add_day`) USING BTREE,
    ADD KEY `aa_dict_date_n5` (`add_week`) USING BTREE,
    ADD KEY `aa_dict_date_n6` (`add_quarter`) USING BTREE,
    ADD KEY `aa_dict_date_n7` (`add_day_of_week`) USING BTREE,
    ADD KEY `aa_dict_date_n8` (`add_day_of_year`) USING BTREE,
    ADD KEY `aa_dict_date_n9` (`add_year`,`add_month`,`add_day`) USING BTREE;


END

*/
