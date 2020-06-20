-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: bookstore
-- ------------------------------------------------------
-- Server version	8.0.20

/*!40101 SET @OLD_CHARACTER_SET_CLIENT = @@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS = @@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION = @@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE = @@TIME_ZONE */;
/*!40103 SET TIME_ZONE = '+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0 */;
/*!40101 SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES = @@SQL_NOTES, SQL_NOTES = 0 */;

--
-- Table structure for table `addmembers`
--

DROP TABLE IF EXISTS `addmembers`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addmembers`
(
    `MNo`  bigint                                                 NOT NULL,
    `IDNo` char(18)                                               NOT NULL,
    `Name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Img`  varchar(100) DEFAULT NULL,
    PRIMARY KEY (`MNo`),
    CONSTRAINT `MNo` FOREIGN KEY (`MNo`) REFERENCES `members` (`MNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addmembers`
--

LOCK TABLES `addmembers` WRITE;
/*!40000 ALTER TABLE `addmembers`
    DISABLE KEYS */;
INSERT INTO `addmembers`
VALUES (100001, '352230199606161202', '萧一', NULL),
       (100002, '352230200107161204', '张二', NULL),
       (100003, '352230197704141001', '李三', NULL);
/*!40000 ALTER TABLE `addmembers`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin`
(
    `ANo`  bigint                                                 NOT NULL AUTO_INCREMENT,
    `IDNo` char(18)                                               NOT NULL,
    `Name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Code` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Img`  varchar(100) DEFAULT NULL,
    PRIMARY KEY (`ANo`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 4
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin`
    DISABLE KEYS */;
INSERT INTO `admin`
VALUES (1, '352230199803030024', '张三', '123456', NULL),
       (2, '352230198806160310', '张璐', '654321', NULL),
       (3, '352230198210100013', '范范', 'ABCDEFG', NULL);
/*!40000 ALTER TABLE `admin`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `buybook`
--

DROP TABLE IF EXISTS `buybook`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buybook`
(
    `BuyNo`   char(20)       NOT NULL,
    `BuyDate` datetime       NOT NULL,
    `MNo`     bigint         NOT NULL,
    `BNo`     char(17)       NOT NULL,
    `BuyNum`  smallint       NOT NULL,
    `BPay`    decimal(10, 2) NOT NULL,
    PRIMARY KEY (`BuyNo`),
    KEY `BNo` (`BNo`),
    KEY `MNo` (`MNo`),
    CONSTRAINT `BNo` FOREIGN KEY (`BNo`) REFERENCES `newbook` (`BNo`),
    CONSTRAINT `buybook_ibfk_1` FOREIGN KEY (`MNo`) REFERENCES `members` (`MNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buybook`
--

LOCK TABLES `buybook` WRITE;
/*!40000 ALTER TABLE `buybook`
    DISABLE KEYS */;
INSERT INTO `buybook`
VALUES ('B20200101000001', '2020-01-01 10:45:26', 100001, '9787040379105', 2, 66.00),
       ('B20200101000002', '2020-01-01 10:45:30', 100002, '9787040541410', 1, 59.00),
       ('B20200211000001', '2020-02-11 10:45:33', 100002, '9787108063106', 1, 28.00),
       ('B20200211000002', '2020-02-11 10:45:36', 100002, '9787040541410', 1, 59.00),
       ('B20200313000001', '2020-03-13 10:45:38', 100003, '9787302556831', 2, 90.00),
       ('B20200316000001', '2020-03-16 10:45:40', 100003, '9787302556619', 1, 20.00),
       ('B20200416000001', '2020-04-16 10:45:44', 100004, '9787576005141', 3, 75.00),
       ('B20200416000002', '2020-04-16 10:45:46', 100004, '9787559612236', 1, 50.00),
       ('B20200513000001', '2020-05-13 10:45:52', 100001, '9787540487645', 1, 42.00),
       ('B20200513000002', '2020-05-13 10:45:54', 100005, '9787544291170', 2, 100.00),
       ('B20200613000002', '2020-06-13 10:45:59', 100006, '9787544288590', 1, 40.00);
/*!40000 ALTER TABLE `buybook`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leasebook`
--

DROP TABLE IF EXISTS `leasebook`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leasebook`
(
    `LNo`    char(20)              NOT NULL,
    `LDate`  datetime              NOT NULL,
    `MNo`    bigint                NOT NULL,
    `BNo`    char(17)              NOT NULL,
    `RDate`  datetime       DEFAULT NULL,
    `LState` enum ('在借','已还','逾期') NOT NULL,
    `LPay`   decimal(10, 2) DEFAULT NULL,
    PRIMARY KEY (`LNo`),
    KEY `MNo` (`MNo`),
    KEY `BNo` (`BNo`),
    CONSTRAINT `leasebook_ibfk_1` FOREIGN KEY (`MNo`) REFERENCES `members` (`MNo`),
    CONSTRAINT `leasebook_ibfk_2` FOREIGN KEY (`BNo`) REFERENCES `oldbook` (`BNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leasebook`
--

LOCK TABLES `leasebook` WRITE;
/*!40000 ALTER TABLE `leasebook`
    DISABLE KEYS */;
INSERT INTO `leasebook`
VALUES ('L20200101000001', '2020-01-01 10:36:38', 100001, '9787040312102', '2020-06-20 10:36:38', '已还', 4.40),
       ('L20200201000001', '2020-02-01 10:43:25', 100002, '9787107346415', '2020-06-20 15:41:52', '逾期', 25.00),
       ('L20200201000002', '2020-02-01 16:42:01', 100002, '9787108063106', '2020-06-20 16:42:01', '逾期', 28.00),
       ('L20200322000001', '2020-03-22 10:38:24', 100003, '9787519201906', '2020-07-22 10:38:24', '在借', NULL),
       ('L20200322000002', '2020-03-22 10:39:41', 100004, '9787517839040', '2020-07-22 10:39:41', '在借', NULL),
       ('L20200521000001', '2020-05-21 13:40:22', 100005, '9787530215593', '2020-06-05 10:40:43', '已还', 2.80),
       ('L20200606000001', '2020-06-06 12:44:07', 100006, '9787538760743', '2020-06-13 10:44:28', '已还', 3.52),
       ('L20200606000002', '2020-06-06 15:54:46', 100005, '9787108063106', '2020-09-06 10:54:46', '在借', NULL);
/*!40000 ALTER TABLE `leasebook`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members`
(
    `MNo`  bigint                                                 NOT NULL AUTO_INCREMENT,
    `IDNo` char(18)                                               NOT NULL,
    `Name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Tel`  char(20)                                               NOT NULL,
    `Img`  varchar(100)                                                    DEFAULT NULL,
    `CNo`  smallint                                               NOT NULL DEFAULT '0',
    `Addr` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    PRIMARY KEY (`MNo`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 100014
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members`
    DISABLE KEYS */;
INSERT INTO `members`
VALUES (100001, '352230196702150021', '萧萧', '15861165153', NULL, 202, '聚湖路12号3#703'),
       (100002, '352230197811010721', '张颖', '13859657478', NULL, 876, '石城路16号'),
       (100003, '352230199908182102', '李鹏', '15160574321', NULL, 456, '四砖公路24号外一环303'),
       (100004, '320623199812120023', '陈丽', '15861165562', NULL, 778, '橡树湾一栋A602'),
       (100005, '440882199902251342', '林绕晴', '15861161590', NULL, 590, '理想大道B102'),
       (100006, '512568199910062341', '文雯', '17315114526', NULL, 526, '理想大道B103'),
       (100007, '123456789123456789', '向瀚淋', '15961165153', 'D:\\Python\\bookstore_flask\\static\\photo\\管理员.jpg', 0, 'M87星云');
/*!40000 ALTER TABLE `members`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newbook`
--

DROP TABLE IF EXISTS `newbook`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `newbook`
(
    `BNo`    char(17)                                               NOT NULL,
    `BName`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Author` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Press`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Price`  decimal(10, 2)                                         NOT NULL,
    `Stock`  smallint                                               NOT NULL,
    PRIMARY KEY (`BNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newbook`
--

LOCK TABLES `newbook` WRITE;
/*!40000 ALTER TABLE `newbook`
    DISABLE KEYS */;
INSERT INTO `newbook`
VALUES ('9787040312102', '概率论与数理统计教程', '茆诗松', '高等教育出版社', 55.40, 15),
       ('9787040379105', '高等代数', '北京大学数学系前代数小组', '高等教育出版社', 33.00, 23),
       ('9787040541410', '智能之门', '胡晓武', '高等教育出版社', 59.00, 4),
       ('9787108063106', '我们仨', '杨绛', '生活.读书.新知三联书店', 28.00, 30),
       ('9787201088945', '皮囊', '蔡崇达', '天津人民出版社', 49.80, 45),
       ('9787302556619', '机器人学', '贾瑞清', '清华大学出版社', 20.00, 0),
       ('9787302556831', '软件项目管理', '夏辉、徐鹏', '清华大学出版社', 45.00, 23),
       ('9787502289669', '长难句解密', '何凯文', '中国原子能出版社', 38.00, 20),
       ('9787506380263', '人间失格', '太宰治', '作家出版社', 25.00, 22),
       ('9787512007468', '从容彼岸是生活', '林清玄', '线装书局', 29.80, 5),
       ('9787513919524', '乌合之众 : 大众心理研究', ' 古斯塔夫·勒庞', '民主与建设出版社', 26.00, 27),
       ('9787519201906', '英语四级词汇', '伍乐其', '世界图书出版公司', 49.80, 0),
       ('9787530215593', '活着', '余华', '北京十月文艺出版社', 35.00, 17),
       ('9787538760743', '罗生门', '芥川龙之介', '时代文艺出版社', 44.00, 6),
       ('9787540485214', '偷影子的人', '马克·李维', '湖南文艺出版社', 39.80, 20),
       ('9787540487645', '云边有个小卖部', '张嘉佳', '湖南文艺出版社', 42.00, 0),
       ('9787544288590', '窗边的小豆豆', '黑柳彻子', '南海出版公司', 39.50, 12),
       ('9787544291170', '百年孤独', '加西亚·马尔克斯 ', '南海出版公司', 55.00, 29),
       ('9787559442017', '你有风情，亦有风骨', '张蔚然', '江苏凤凰文艺出版社', 45.00, 22),
       ('9787559442628', '古代人的日常生活', '讲历史的王老师', '江苏凤凰文艺出版社', 69.90, 32),
       ('9787559612236', '女孩们', '艾玛·克莱因', '北京联合出版有限公司', 49.80, 7),
       ('9787559634511', '流浪图书馆', '大卫 怀特豪斯', '北京联合出版有限公司', 49.80, 22),
       ('9787576005141', '智慧之旅', '朱邦复', '华东师范大学出版社', 25.00, 6);
/*!40000 ALTER TABLE `newbook`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oldbook`
--

DROP TABLE IF EXISTS `oldbook`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `oldbook`
(
    `BNo`    char(17)                                               NOT NULL,
    `BName`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Author` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Press`  varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    `Price`  decimal(10, 0)                                         NOT NULL,
    `Stock`  smallint                                               NOT NULL,
    PRIMARY KEY (`BNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oldbook`
--

LOCK TABLES `oldbook` WRITE;
/*!40000 ALTER TABLE `oldbook`
    DISABLE KEYS */;
INSERT INTO `oldbook`
VALUES ('9787040312102', '概率论与数理统计', '茆诗松', '高等教育出版社', 55, 5),
       ('9787107346415', '陀螺', '高洪波', '人民教育出版社', 25, 3),
       ('9787108063106', '我们仨', '杨绛', '生活.读书.新知三联书店', 28, 6),
       ('9787302556831', '软件项目管理', '夏辉、徐鹏', '清华大学出版社', 45, 2),
       ('9787506380263', '人间失格', '太宰治', '作家出版社', 25, 6),
       ('9787517839040', '现代流通科学研究方法', '张德纯、王兴亮', '浙江工商大学出版社', 69, 2),
       ('9787519201906', '英语四级词汇', '伍乐其', '世界图书出版公司', 50, 0),
       ('9787530215593', '活着', '余华', '北京十月文艺出版社', 35, 9),
       ('9787538760743', '罗生门', '芥川龙之介', '时代文艺出版社', 44, 2),
       ('9787559442017', '你有风情，亦有风骨', '张蔚然', '江苏凤凰文艺出版社', 45, 7),
       ('9787559442628', '古代人的日常生活', '讲历史的王老师', '江苏凤凰文艺出版社', 70, 7),
       ('9787576005141', '智慧之旅', '朱邦复', '华东师范大学出版社', 25, 4);
/*!40000 ALTER TABLE `oldbook`
    ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderbook`
--

DROP TABLE IF EXISTS `orderbook`;
/*!40101 SET @saved_cs_client = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderbook`
(
    `ONo`   char(20)       NOT NULL,
    `ODate` datetime       NOT NULL,
    `MNo`   bigint         NOT NULL,
    `BNo`   char(17)       NOT NULL,
    `ONum`  smallint       NOT NULL,
    `OPay`  decimal(10, 2) NOT NULL,
    PRIMARY KEY (`ONo`),
    KEY `MNo` (`MNo`),
    KEY `BNo` (`BNo`),
    CONSTRAINT `orderbook_ibfk_1` FOREIGN KEY (`MNo`) REFERENCES `members` (`MNo`),
    CONSTRAINT `orderbook_ibfk_2` FOREIGN KEY (`BNo`) REFERENCES `newbook` (`BNo`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderbook`
--

LOCK TABLES `orderbook` WRITE;
/*!40000 ALTER TABLE `orderbook`
    DISABLE KEYS */;
INSERT INTO `orderbook`
VALUES ('O20200201000001', '2020-02-01 15:46:14', 100006, '9787302556619', 1, 20.00),
       ('O20200422000001', '2020-04-22 10:47:56', 100001, '9787302556619', 2, 40.00),
       ('O20200422000002', '2020-04-22 11:48:06', 100002, '9787519201906', 1, 50.00),
       ('O20200513000001', '2020-05-13 12:48:55', 100003, '9787538760743', 8, 352.00),
       ('O20200611000001', '2020-06-11 10:50:03', 100004, '9787108063106', 2, 100.00),
       ('O20200611000002', '2020-06-11 11:50:48', 100003, '9787502289669', 40, 1520.00),
       ('O20200611000003', '2020-06-11 14:21:49', 100005, '9787040541410', 5, 295.00);
/*!40000 ALTER TABLE `orderbook`
    ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE = @OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE = @OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT = @OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS = @OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION = @OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES = @OLD_SQL_NOTES */;

-- Dump completed on 2020-06-21  0:02:00
