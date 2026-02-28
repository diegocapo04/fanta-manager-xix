-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: fantamanagerxix
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `competizioni`
--

DROP TABLE IF EXISTS `competizioni`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `competizioni` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Nome` varchar(50) NOT NULL,
  `Stagione` varchar(9) NOT NULL DEFAULT '2025/2026',
  `Tipo` enum('Campionato','Coppa') NOT NULL DEFAULT 'Campionato',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_competizione_stagione` (`Nome`,`Stagione`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `competizioni`
--

LOCK TABLES `competizioni` WRITE;
/*!40000 ALTER TABLE `competizioni` DISABLE KEYS */;
INSERT INTO `competizioni` VALUES (1,'Campionato','2025/2026','Campionato'),(2,'Champions League','2025/2026','Coppa'),(3,'Europa League','2025/2026','Coppa'),(4,'Coppa Italia','2025/2026','Coppa');
/*!40000 ALTER TABLE `competizioni` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configurazione`
--

DROP TABLE IF EXISTS `configurazione`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configurazione` (
  `Chiave` varchar(50) NOT NULL,
  `Valore` varchar(50) NOT NULL,
  PRIMARY KEY (`Chiave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configurazione`
--

LOCK TABLES `configurazione` WRITE;
/*!40000 ALTER TABLE `configurazione` DISABLE KEYS */;
INSERT INTO `configurazione` VALUES ('stagione_corrente','2025/2026');
/*!40000 ALTER TABLE `configurazione` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contratti`
--

DROP TABLE IF EXISTS `contratti`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contratti` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `SquadraID` int NOT NULL,
  `GiocatoreID` int NOT NULL,
  `StagioneFirma` varchar(9) NOT NULL,
  `AnniDurata` int NOT NULL DEFAULT '1',
  `Stipendio` decimal(10,2) NOT NULL DEFAULT '0.00',
  `CostoAcquisto` decimal(10,2) NOT NULL DEFAULT '0.00',
  `PrimaSquadra` tinyint(1) NOT NULL DEFAULT '1',
  `SettoreGiovanile` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `SquadraID` (`SquadraID`,`GiocatoreID`),
  KEY `GiocatoreID` (`GiocatoreID`),
  CONSTRAINT `contratti_ibfk_1` FOREIGN KEY (`SquadraID`) REFERENCES `fantasquadre` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `contratti_ibfk_2` FOREIGN KEY (`GiocatoreID`) REFERENCES `giocatori` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `fk_contratti_squadra` FOREIGN KEY (`SquadraID`) REFERENCES `fantasquadre` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=316 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contratti`
--

LOCK TABLES `contratti` WRITE;
/*!40000 ALTER TABLE `contratti` DISABLE KEYS */;
INSERT INTO `contratti` VALUES (1,1,1,'2025/2026',3,2.00,16.00,1,0),(2,1,2,'2025/2026',3,0.60,2.00,1,0),(3,1,3,'2025/2026',3,1.00,11.00,1,0),(4,1,4,'2025/2026',3,3.50,52.00,1,0),(5,1,5,'2025/2026',3,1.50,1.00,1,0),(6,1,6,'2025/2026',3,1.00,3.00,1,0),(7,1,7,'2025/2026',3,0.65,1.00,1,0),(8,1,8,'2025/2026',3,1.50,8.00,1,0),(9,1,9,'2025/2026',3,0.85,12.00,1,0),(10,1,10,'2025/2026',5,0.10,76.00,0,1),(11,1,11,'2025/2026',3,0.15,2.00,1,0),(12,1,12,'2025/2026',3,0.60,7.00,1,0),(13,1,13,'2025/2026',3,3.50,9.00,1,0),(14,1,14,'2025/2026',3,0.30,1.00,1,0),(15,1,15,'2025/2026',3,0.50,2.00,1,0),(16,1,16,'2025/2026',3,2.00,2.00,1,0),(17,1,17,'2025/2026',3,2.50,2.00,1,0),(18,1,18,'2025/2026',2,0.60,1.00,1,0),(19,1,19,'2025/2026',3,2.50,3.00,1,0),(20,1,20,'2025/2026',3,1.80,19.00,1,0),(21,1,21,'2025/2026',3,1.50,12.00,1,0),(22,1,22,'2025/2026',3,1.80,27.00,1,0),(23,1,23,'2025/2026',3,1.00,1.00,1,0),(24,1,24,'2025/2026',3,5.00,39.00,1,0),(25,1,25,'2025/2026',3,1.20,1.00,1,0),(26,1,26,'2025/2026',3,2.50,40.00,1,0),(27,1,27,'2025/2026',3,1.70,15.00,1,0),(28,1,28,'2025/2026',3,1.40,11.00,1,0),(29,1,29,'2025/2026',3,0.70,4.00,1,0),(30,1,30,'2025/2026',3,2.00,11.00,1,0),(31,1,31,'2025/2026',3,0.40,2.00,1,0),(32,1,32,'2025/2026',3,1.80,1.00,1,0),(33,1,33,'2025/2026',3,0.01,1.00,1,0),(34,1,34,'2025/2026',3,2.00,95.00,1,0),(35,2,35,'2025/2026',1,2.80,12.00,1,0),(36,2,36,'2025/2026',1,2.20,1.00,1,0),(37,2,37,'2025/2026',3,5.00,36.00,1,0),(38,2,38,'2025/2026',3,3.50,33.00,1,0),(39,2,39,'2025/2026',3,2.50,30.00,1,0),(40,2,40,'2025/2026',1,1.00,9.00,1,0),(41,2,41,'2025/2026',3,3.00,23.00,1,0),(42,2,42,'2025/2026',1,0.25,1.00,1,0),(43,2,43,'2025/2026',1,2.20,7.00,1,0),(44,2,44,'2025/2026',5,0.10,1.00,0,1),(45,2,45,'2025/2026',1,0.24,3.00,1,0),(46,2,46,'2025/2026',1,0.35,1.00,1,0),(47,2,47,'2025/2026',1,1.20,6.00,1,0),(48,2,48,'2025/2026',1,1.80,1.00,1,0),(49,2,49,'2025/2026',3,3.50,132.00,1,0),(50,2,50,'2025/2026',3,0.90,12.00,1,0),(51,2,51,'2025/2026',1,0.50,15.00,1,0),(52,2,52,'2025/2026',1,0.25,2.00,1,0),(53,2,53,'2025/2026',1,0.15,1.00,1,0),(54,2,54,'2025/2026',3,1.00,13.00,1,0),(55,2,55,'2025/2026',1,0.40,17.00,1,0),(56,2,56,'2025/2026',1,2.20,1.00,1,0),(57,2,57,'2025/2026',1,0.25,1.00,1,0),(58,2,58,'2025/2026',3,2.50,116.00,1,0),(59,2,59,'2025/2026',1,1.70,10.00,1,0),(60,2,60,'2025/2026',1,0.10,1.00,1,0),(61,2,61,'2025/2026',3,2.00,22.00,1,0),(62,2,62,'2025/2026',1,0.70,6.00,1,0),(63,2,63,'2025/2026',1,0.30,5.00,1,0),(64,2,64,'2025/2026',1,0.80,1.00,1,0),(65,3,65,'2025/2026',3,0.40,1.00,1,0),(66,3,66,'2025/2026',2,0.32,1.00,1,0),(67,3,67,'2025/2026',3,0.10,1.00,1,0),(68,3,68,'2025/2026',3,2.00,18.00,1,0),(69,3,69,'2025/2026',5,0.10,6.00,0,1),(70,3,70,'2025/2026',3,1.20,1.00,1,0),(71,3,71,'2025/2026',5,0.10,23.00,0,1),(72,3,72,'2025/2026',3,2.40,24.00,1,0),(73,3,73,'2025/2026',3,0.50,1.00,1,0),(74,3,74,'2025/2026',3,0.70,1.00,1,0),(75,3,75,'2025/2026',3,0.45,3.00,1,0),(76,3,76,'2025/2026',2,3.00,5.00,1,0),(77,3,77,'2025/2026',3,2.00,1.00,1,0),(78,3,78,'2025/2026',3,1.40,1.00,1,0),(79,3,79,'2025/2026',1,0.40,2.00,1,0),(80,3,80,'2025/2026',3,0.15,3.00,1,0),(81,3,81,'2025/2026',3,0.75,6.00,1,0),(82,3,82,'2025/2026',2,0.45,2.00,1,0),(83,3,83,'2025/2026',3,2.50,6.00,1,0),(84,3,84,'2025/2026',2,0.40,7.00,1,0),(85,3,85,'2025/2026',3,1.20,10.00,1,0),(86,3,86,'2025/2026',3,1.20,23.00,1,0),(87,3,87,'2025/2026',2,0.18,1.00,1,0),(88,3,88,'2025/2026',3,1.40,3.00,1,0),(89,3,89,'2025/2026',3,2.00,1.00,1,0),(90,3,90,'2025/2026',3,0.30,1.00,1,0),(91,3,91,'2025/2026',3,5.00,113.00,1,0),(92,3,92,'2025/2026',3,0.40,41.00,1,0),(93,3,93,'2025/2026',3,0.60,1.00,1,0),(94,3,94,'2025/2026',3,2.80,60.00,1,0),(95,3,95,'2025/2026',3,0.90,1.00,1,0),(96,3,96,'2025/2026',3,7.50,164.00,1,0),(97,3,97,'2025/2026',3,0.45,1.00,1,0),(98,3,98,'2025/2026',3,1.20,13.00,1,0),(99,3,99,'2025/2026',3,1.20,2.00,1,0),(100,3,100,'2025/2026',2,0.40,1.00,1,0),(101,4,101,'2025/2026',3,0.15,5.00,1,0),(102,4,102,'2025/2026',3,2.60,9.00,1,0),(103,4,103,'2025/2026',1,0.04,1.00,1,0),(104,4,104,'2025/2026',2,1.00,1.00,1,0),(105,4,105,'2025/2026',3,0.80,5.00,1,0),(106,4,106,'2025/2026',2,2.50,81.00,1,0),(107,4,107,'2025/2026',1,0.05,2.00,1,0),(108,4,108,'2025/2026',2,0.50,31.00,1,0),(109,4,109,'2025/2026',2,0.50,1.00,1,0),(110,4,110,'2025/2026',2,0.50,2.00,1,0),(111,4,111,'2025/2026',2,1.50,14.00,1,0),(112,4,112,'2025/2026',3,5.00,35.00,1,0),(113,4,113,'2025/2026',2,0.60,2.00,1,0),(114,4,114,'2025/2026',3,1.80,51.00,1,0),(115,4,115,'2025/2026',3,2.80,12.00,1,0),(116,4,116,'2025/2026',3,5.00,160.00,1,0),(117,4,117,'2025/2026',2,0.30,3.00,1,0),(118,4,118,'2025/2026',1,0.40,2.00,1,0),(119,4,119,'2025/2026',3,0.50,1.00,1,0),(120,4,120,'2025/2026',1,0.60,2.00,1,0),(121,4,121,'2025/2026',2,1.00,10.00,1,0),(122,4,122,'2025/2026',2,0.35,1.00,1,0),(123,4,123,'2025/2026',3,0.50,31.00,1,0),(124,4,124,'2025/2026',3,0.50,3.00,1,0),(125,4,125,'2025/2026',3,0.70,1.00,1,0),(126,4,126,'2025/2026',3,0.40,1.00,1,0),(127,4,127,'2025/2026',3,0.60,3.00,1,0),(128,4,128,'2025/2026',3,0.80,10.00,1,0),(129,4,129,'2025/2026',3,2.50,11.00,1,0),(130,4,130,'2025/2026',2,0.35,17.00,1,0),(131,5,131,'2025/2026',3,0.30,6.00,1,0),(132,5,132,'2025/2026',3,0.50,5.00,1,0),(133,5,133,'2025/2026',3,1.20,2.00,1,0),(134,5,134,'2025/2026',3,3.50,4.00,1,0),(135,5,135,'2025/2026',3,0.35,7.00,1,0),(136,5,136,'2025/2026',3,0.85,1.00,1,0),(137,5,137,'2025/2026',3,0.45,3.00,1,0),(138,5,138,'2025/2026',3,0.95,1.00,1,0),(139,5,139,'2025/2026',3,1.60,1.00,1,0),(140,5,140,'2025/2026',3,0.35,1.00,1,0),(141,5,141,'2025/2026',2,0.35,5.00,1,0),(142,5,142,'2025/2026',3,2.50,7.00,1,0),(143,5,143,'2025/2026',3,2.80,7.00,1,0),(144,5,144,'2025/2026',3,0.80,25.00,1,0),(145,5,145,'2025/2026',3,2.00,25.00,1,0),(146,5,146,'2025/2026',3,5.00,31.00,1,0),(147,5,147,'2025/2026',3,2.50,3.00,1,0),(148,5,148,'2025/2026',3,5.00,104.00,1,0),(149,5,149,'2025/2026',3,0.30,10.00,1,0),(150,5,150,'2025/2026',2,0.10,1.00,0,1),(151,5,151,'2025/2026',3,0.75,2.00,1,0),(152,5,152,'2025/2026',5,0.10,9.00,0,1),(153,5,153,'2025/2026',3,0.85,5.00,1,0),(154,5,154,'2025/2026',3,1.50,13.00,1,0),(155,5,155,'2025/2026',3,0.70,8.00,1,0),(156,5,156,'2025/2026',3,0.28,3.00,1,0),(157,5,157,'2025/2026',3,0.25,2.00,1,0),(158,5,158,'2025/2026',3,0.30,1.00,1,0),(159,5,159,'2025/2026',5,0.60,4.00,1,0),(160,5,160,'2025/2026',3,0.32,2.00,1,0),(161,5,161,'2025/2026',3,0.22,42.00,1,0),(162,5,162,'2025/2026',3,3.50,61.00,1,0),(163,5,163,'2025/2026',5,0.10,141.00,0,1),(164,6,164,'2025/2026',3,1.00,1.00,1,0),(165,6,165,'2025/2026',3,0.75,1.00,1,0),(166,6,166,'2025/2026',3,7.50,32.00,1,0),(167,6,167,'2025/2026',2,0.20,5.00,1,0),(168,6,168,'2025/2026',3,0.80,47.00,1,0),(169,6,169,'2025/2026',3,0.80,4.00,1,0),(170,6,170,'2025/2026',3,1.20,1.00,1,0),(171,6,171,'2025/2026',3,3.50,39.00,1,0),(172,6,172,'2025/2026',3,0.80,25.00,1,0),(173,6,173,'2025/2026',3,2.00,1.00,1,0),(174,6,174,'2025/2026',3,0.43,1.00,1,0),(175,6,175,'2025/2026',2,0.70,7.00,1,0),(176,6,176,'2025/2026',3,3.00,12.00,1,0),(177,6,177,'2025/2026',3,0.40,7.00,1,0),(178,6,178,'2025/2026',3,1.00,13.00,1,0),(179,6,179,'2025/2026',3,0.03,1.00,1,0),(180,6,180,'2025/2026',3,3.00,10.00,1,0),(181,6,181,'2025/2026',3,1.80,11.00,1,0),(182,6,182,'2025/2026',3,1.00,24.00,1,0),(183,6,183,'2025/2026',3,0.30,35.00,1,0),(184,6,184,'2025/2026',3,1.00,1.00,1,0),(185,6,185,'2025/2026',5,0.10,1.00,0,1),(186,6,186,'2025/2026',3,3.00,13.00,1,0),(187,6,187,'2025/2026',3,0.35,1.00,1,0),(188,6,188,'2025/2026',2,0.10,10.00,1,0),(189,6,189,'2025/2026',3,0.65,1.00,1,0),(190,6,190,'2025/2026',3,1.20,20.00,1,0),(191,6,191,'2025/2026',3,0.40,3.00,1,0),(192,6,192,'2025/2026',3,0.50,1.00,1,0),(193,6,193,'2025/2026',3,1.00,27.00,1,0),(194,7,194,'2025/2026',5,0.10,20.00,0,1),(195,7,195,'2025/2026',3,2.70,46.00,1,0),(196,7,196,'2025/2026',3,0.60,3.00,1,0),(197,7,197,'2025/2026',1,0.35,1.00,1,0),(198,7,198,'2025/2026',3,0.25,1.00,1,0),(199,7,199,'2025/2026',3,0.90,2.00,1,0),(200,7,200,'2025/2026',2,0.30,1.00,1,0),(201,7,201,'2025/2026',3,0.65,18.00,1,0),(202,7,202,'2025/2026',3,1.80,56.00,1,0),(203,7,203,'2025/2026',3,3.00,21.00,1,0),(204,7,204,'2025/2026',3,0.28,1.00,1,0),(205,7,205,'2025/2026',3,3.00,24.00,1,0),(206,7,206,'2025/2026',3,3.20,11.00,1,0),(207,7,207,'2025/2026',1,0.07,1.00,1,0),(208,7,208,'2025/2026',3,3.50,10.00,1,0),(209,7,209,'2025/2026',1,0.35,1.00,1,0),(210,7,210,'2025/2026',3,1.50,17.00,1,0),(211,7,211,'2025/2026',2,0.85,2.00,1,0),(212,7,212,'2025/2026',3,2.20,12.00,1,0),(213,7,213,'2025/2026',3,1.50,8.00,1,0),(214,7,214,'2025/2026',2,1.10,13.00,1,0),(215,7,215,'2025/2026',3,0.70,9.00,1,0),(216,7,216,'2025/2026',3,0.85,1.00,1,0),(217,7,217,'2025/2026',5,0.10,101.00,0,1),(218,7,218,'2025/2026',3,0.25,3.00,1,0),(219,7,219,'2025/2026',3,1.20,10.00,1,0),(220,7,220,'2025/2026',3,2.40,43.00,1,0),(221,7,221,'2025/2026',3,2.00,4.00,1,0),(222,7,222,'2025/2026',3,2.00,1.00,1,0),(223,7,223,'2025/2026',3,2.00,18.00,1,0),(224,7,224,'2025/2026',3,1.10,5.00,1,0),(225,7,225,'2025/2026',3,0.50,7.00,1,0),(226,8,226,'2025/2026',3,0.18,16.00,1,0),(227,8,227,'2025/2026',3,8.00,24.00,1,0),(228,8,228,'2025/2026',3,0.08,2.00,1,0),(229,8,229,'2025/2026',3,5.00,20.00,1,0),(230,8,230,'2025/2026',3,1.50,12.00,1,0),(231,8,231,'2025/2026',3,1.50,5.00,1,0),(232,8,232,'2025/2026',3,4.50,101.00,1,0),(233,8,233,'2025/2026',3,0.75,3.00,1,0),(234,8,234,'2025/2026',3,1.20,16.00,1,0),(235,8,235,'2025/2026',3,0.34,3.00,1,0),(236,8,236,'2025/2026',5,0.10,16.00,0,1),(237,8,237,'2025/2026',2,0.18,2.00,1,0),(238,8,238,'2025/2026',3,0.80,1.00,1,0),(239,8,239,'2025/2026',3,3.00,10.00,1,0),(240,8,240,'2025/2026',3,2.50,40.00,1,0),(241,8,241,'2025/2026',3,2.50,77.00,1,0),(242,8,242,'2025/2026',3,0.60,1.00,1,0),(243,8,243,'2025/2026',3,1.20,12.00,1,0),(244,8,244,'2025/2026',3,0.75,5.00,1,0),(245,8,245,'2025/2026',3,0.60,7.00,1,0),(246,8,246,'2025/2026',3,0.60,24.00,1,0),(247,8,247,'2025/2026',3,1.20,18.00,1,0),(248,8,248,'2025/2026',3,1.00,6.00,1,0),(249,8,249,'2025/2026',3,1.20,4.00,1,0),(250,8,250,'2025/2026',3,0.25,3.00,1,0),(251,8,251,'2025/2026',3,3.50,10.00,1,0),(252,8,252,'2025/2026',2,0.60,1.00,1,0),(253,8,253,'2025/2026',3,0.10,1.00,1,0),(254,8,254,'2025/2026',3,0.35,5.00,1,0),(255,8,255,'2025/2026',3,0.05,1.00,1,0),(256,8,256,'2025/2026',3,0.30,1.00,1,0),(257,8,257,'2025/2026',3,2.50,30.00,1,0),(258,9,258,'2025/2026',3,0.80,20.00,1,0),(259,9,259,'2025/2026',2,0.36,8.00,1,0),(260,9,260,'2025/2026',3,2.40,10.00,1,0),(261,9,261,'2025/2026',3,2.80,11.00,1,0),(262,9,262,'2025/2026',1,0.70,3.00,1,0),(263,9,263,'2025/2026',3,0.90,9.00,1,0),(264,9,264,'2025/2026',3,0.50,15.00,1,0),(265,9,265,'2025/2026',2,0.70,7.00,1,0),(266,9,266,'2025/2026',3,0.40,16.00,1,0),(267,9,267,'2025/2026',3,2.20,20.00,1,0),(268,9,268,'2025/2026',3,1.00,2.00,1,0),(269,9,269,'2025/2026',1,1.20,4.00,1,0),(270,9,270,'2025/2026',3,7.00,100.00,1,0),(271,9,271,'2025/2026',3,1.00,20.00,1,0),(272,9,272,'2025/2026',2,0.65,7.00,1,0),(273,9,273,'2025/2026',1,0.28,2.00,1,0),(274,9,274,'2025/2026',3,3.00,15.00,1,0),(275,9,275,'2025/2026',2,1.00,4.00,1,0),(276,9,276,'2025/2026',2,0.35,4.00,1,0),(277,9,277,'2025/2026',1,0.90,3.00,1,0),(278,9,278,'2025/2026',2,0.15,1.00,1,0),(279,9,279,'2025/2026',3,2.50,6.00,1,0),(280,9,280,'2025/2026',3,0.50,18.00,1,0),(281,9,281,'2025/2026',2,0.25,27.00,1,0),(282,9,282,'2025/2026',3,0.50,1.00,1,0),(283,9,283,'2025/2026',3,3.50,77.00,1,0),(284,9,284,'2025/2026',3,0.32,6.00,1,0),(285,9,285,'2025/2026',3,4.00,50.00,1,0),(286,9,286,'2025/2026',2,1.40,9.00,1,0),(287,10,287,'2025/2026',3,0.50,6.00,1,0),(288,10,288,'2025/2026',5,0.10,2.00,0,1),(289,10,289,'2025/2026',5,0.10,5.00,0,1),(290,10,290,'2025/2026',5,0.10,11.00,0,1),(291,10,291,'2025/2026',2,0.01,1.00,1,0),(292,10,292,'2025/2026',2,1.00,11.00,1,0),(293,10,293,'2025/2026',2,2.00,74.00,1,0),(294,10,294,'2025/2026',3,4.50,10.00,1,0),(295,10,295,'2025/2026',1,1.40,2.00,1,0),(296,10,296,'2025/2026',3,1.00,6.00,1,0),(297,10,297,'2025/2026',1,0.50,6.00,1,0),(298,10,298,'2025/2026',1,1.40,8.00,1,0),(299,10,299,'2025/2026',2,0.40,4.00,1,0),(300,10,300,'2025/2026',2,2.40,12.00,1,0),(301,10,301,'2025/2026',2,3.00,11.00,1,0),(302,10,302,'2025/2026',2,0.12,2.00,1,0),(303,10,303,'2025/2026',2,1.80,15.00,1,0),(304,10,304,'2025/2026',3,1.20,15.00,1,0),(305,10,305,'2025/2026',1,1.20,3.00,1,0),(306,10,306,'2025/2026',2,2.40,36.00,1,0),(307,10,307,'2025/2026',2,0.15,7.00,1,0),(308,10,308,'2025/2026',1,0.35,2.00,1,0),(309,10,309,'2025/2026',3,3.50,39.00,1,0),(310,10,310,'2025/2026',2,2.50,55.00,1,0),(311,10,311,'2025/2026',3,1.20,11.00,1,0),(312,10,312,'2025/2026',3,1.80,13.00,1,0),(313,10,313,'2025/2026',1,0.35,5.00,1,0),(314,10,314,'2025/2026',3,2.50,46.00,1,0),(315,10,315,'2025/2026',2,0.30,9.00,1,0);
/*!40000 ALTER TABLE `contratti` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fantasquadre`
--

DROP TABLE IF EXISTS `fantasquadre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasquadre` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Nome` varchar(50) NOT NULL,
  `CreditiResidui` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Nome` (`Nome`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fantasquadre`
--

LOCK TABLES `fantasquadre` WRITE;
/*!40000 ALTER TABLE `fantasquadre` DISABLE KEYS */;
INSERT INTO `fantasquadre` VALUES (1,'AC ACCIA DI TALENTI',19.00),(2,'Brskanite',38.00),(3,'FC Merolone',-29.00),(4,'GIGIOTTO GIAGUARO 92esimo',20.00),(5,'Kaiser Drago Finale',32.00),(6,'Paracezaniolo',48.00),(7,'RB Combatti Tigre',29.00),(8,'SS Caporale',15.00),(9,'Team Broglio',36.00),(10,'Totoriino',70.00);
/*!40000 ALTER TABLE `fantasquadre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `giocatori`
--

DROP TABLE IF EXISTS `giocatori`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `giocatori` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Nome` varchar(50) NOT NULL,
  `Cognome` varchar(50) NOT NULL,
  `Ruolo` enum('P','D','C','A') NOT NULL,
  `ValoreMercato` decimal(12,2) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `Cognome` (`Cognome`)
) ENGINE=InnoDB AUTO_INCREMENT=316 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `giocatori`
--

LOCK TABLES `giocatori` WRITE;
/*!40000 ALTER TABLE `giocatori` DISABLE KEYS */;
INSERT INTO `giocatori` VALUES (1,'','Angelino','D',20.00),(2,'Nicolò','Bertola','D',6.00),(3,'Jérémie','Boga','C',10.00),(4,'Charles','De Ketelaere','C',35.00),(5,'Andy','Diouf','C',15.00),(6,'Anastasios','Douvikas','A',10.00),(7,'Rafiu','Durosinmi','A',6.50),(8,'Neil','El Aynaoui','C',15.00),(9,'Sebastiano','Esposito','A',8.50),(10,'Evan','Ferguson','A',25.00),(11,'Romano','Floriani Mussolini','D',1.50),(12,'Michael','Folorunsho','C',6.00),(13,'Davide','Frattesi','C',35.00),(14,'Tiago','Gabriel','A',3.00),(15,'Daniele','Ghilardi','D',5.00),(16,'Miguel','Gutierrez','C',20.00),(17,'Luis','Henrique','C',25.00),(18,'Ardian','Ismajli','D',6.00),(19,'Odilon','Kossounou','D',25.00),(20,'Vanja','Milinkovic-Savic','P',18.00),(21,'Gianluca','Mancini','D',15.00),(22,'Alex','Meret','P',18.00),(23,'Victor','Nelsson','D',10.00),(24,'Loïs','Openda','A',50.00),(25,'Máximo','Perrone','C',12.00),(26,'Giacomo','Raspadori','A',25.00),(27,'Alexis','Saelemaekers','C',17.00),(28,'Manor','Solomon','C',14.00),(29,'Gabriel','Strefezza','C',7.00),(30,'Peter','Sucic','C',20.00),(31,'Idrissa','Toure','C',4.00),(32,'Konstantinos','Tsimikas','D',18.00),(33,'Robinio','Vaz','A',0.15),(34,'Mattia','Zaccagni','C',20.00),(35,'Manuel','Akanji','D',28.00),(36,'Martin','Baturina','C',22.00),(37,'Gleison','Bremer','D',50.00),(38,'Andrea','Cambiaso','D',35.00),(39,'Marco','Carnesecchi','P',25.00),(40,'Saúl','Coco','D',10.00),(41,'Francisco','Conceicao','C',30.00),(42,'Matteo','Darmian','D',2.50),(43,'Koni','De Winter','D',22.00),(44,'Pio','Esposito','A',35.00),(45,'Kingsley','Ehizibue','D',2.40),(46,'Stephan','El Shaarawy','C',3.50),(47,'Giovanni','Fabbian','C',12.00),(48,'Nicolò','Fagioli','C',18.00),(49,'Rasmus','Hojlund','A',35.00),(50,'Thomas','Kristensen','D',9.00),(51,'Franco','Israel','P',5.00),(52,'Ruslan','Malinovskyi','C',2.50),(53,'Luca','Mazzitelli','C',1.50),(54,'Joao','Mario','C',10.00),(55,'Luka','Modric','C',4.00),(56,'Weston','McKennie','C',22.00),(57,'Alieu','Njie','C',2.50),(58,'Riccardo','Orsolini','C',25.00),(59,'Lazar','Samardzic','C',17.00),(60,'Marco','Sportiello','P',1.00),(61,'Nuno','Tavares','D',20.00),(62,'Matteo','Tramoni','C',7.00),(63,'Emanuele','Valeri','C',3.00),(64,'Oliveira','Vitinha','A',8.00),(65,'Michel','Adopo','C',4.00),(66,'Emil','Audero','P',3.20),(67,'Federico','Bonazzoli','A',1.00),(68,'Ange-Yoan','Bonny','A',20.00),(69,'Pietro','Comuzzo','D',25.00),(70,'Thijs','Dallinga','A',12.00),(71,'Assane','Diao','A',30.00),(72,'','Dodo','D',24.00),(73,'Josh','Doig','D',5.00),(74,'Jurgen','Ekkelenkamp','C',7.00),(75,'Alieu','Fadera','C',4.50),(76,'Youssouf','Fofana','C',30.00),(77,'Billy','Gilmour','C',20.00),(78,'Jack','Harrison','C',14.00),(79,'Jeper','Karlstrom','C',4.00),(80,'R.','Idrissi','C',1.50),(81,'Jay','Idzes','D',7.50),(82,'Valentino','Lazaro','C',4.50),(83,'Jhon','Lucumi','D',25.00),(84,'Sebastiano','Luperto','D',4.00),(85,'Rolando','Mandragora','C',12.00),(86,'Jo.','Martinez','A',12.00),(87,'Nemanja','Matic','C',1.80),(88,'Fabio','Miretti','C',14.00),(89,'Yunus','Musah','C',20.00),(90,'Adam','Obert','D',3.00),(91,'Christian','Pulisic','C',50.00),(92,'Yann','Sommer','P',4.00),(93,'Tomas','Suslov','C',6.00),(94,'','Taylor','A',28.00),(95,'Kristian','Thorstvedt','C',9.00),(96,'Marcus','Thuram','A',75.00),(97,'Sebastian','Walukiewicz','D',4.50),(98,'Nicolò','Zaniolo','C',12.00),(99,'Bryan','Zaragoza','A',12.00),(100,'Alessio','Zerbin','C',4.00),(101,'Jayden','Addai','C',1.50),(102,'Carlos ','Augusto','D',26.00),(103,'Matteo','Bianchetti','D',0.40),(104,'Warren','Bondo','C',10.00),(105,'Marco','Brescianini','C',8.00),(106,'Hakan','Calhanoglu','C',25.00),(107,'Antonio','Caracciolo','D',0.50),(108,'David','de Gea','P',5.00),(109,'Marten','de Roon','C',5.00),(110,'Stefan','de Vrij','D',5.00),(111,'Boulaye','Dia','A',15.00),(112,'Federico','Dimarco','C',50.00),(113,'Berat','Djimsiti','D',6.00),(114,'Albert','Gudmundsson','C',18.00),(115,'Pierre','Kalulu','D',28.00),(116,'Moise','Kean','A',50.00),(117,'Oliver','Kempf','D',3.00),(118,'Henrikh','Mkhitaryan','C',4.00),(119,'Cher','Ndour','C',5.00),(120,'M\'Bala','Nzola','A',6.00),(121,'Mario','Pasalic','C',10.00),(122,'Oliver','Provstgaard','D',3.50),(123,'Petar','Ratkov','A',5.00),(124,'Simon','Sohm','C',5.00),(125,'Calvin','Stengs','A',7.00),(126,'Nikola','Stulic','A',4.00),(127,'Alessandro','Zanoli','D',6.00),(128,'Nikola','Vlasic','C',8.00),(129,'','Wesley','A',25.00),(130,'Duvan','Zapata','A',3.50),(131,'Francesco','Acerbi','D',3.00),(132,'Honest','Ahanor','A',5.00),(133,'Tommaso','Baldanzi','C',12.00),(134,'Yann','Bisseck','D',35.00),(135,'Jean','Butez','P',3.50),(136,'Nicolò','Cambiaghi','A',8.50),(137,'Matteo','Cancellieri','A',4.50),(138,'Diego','Carlos','D',9.50),(139,'Maxence','Caqueret','C',16.00),(140,'Danilo','Cataldi','C',3.50),(141,'Wladimiro','Falcone','P',3.50),(142,'Evan','Ferguson','A',25.00),(143,'Lewis','Ferguson','A',28.00),(144,'Robin','Gosens','D',8.00),(145,'Gustav','Isaksen','C',20.00),(146,'Manu','Kone','C',50.00),(147,'Stanislav','Lobotka','C',25.00),(148,'Scott','McTominay','C',50.00),(149,'Yerry','Mina','D',3.00),(150,'Lorenzo','Montipò','P',2.00),(151,'Arijanet','Muric','P',7.50),(152,'Brooke','Norton-Cuffy','D',3.50),(153,'Leo','Ostigard','D',8.50),(154,'Andrea','Pinamonti','A',15.00),(155,'Alessio','Romagnoli','D',7.00),(156,'Antonio','Sanabria','A',2.80),(157,'Alisson','Santos','D',2.50),(158,'Morten','Thorsby','C',3.00),(159,'Álex','Valle','D',6.00),(160,'Jari','Vandeputte','C',3.20),(161,'Antonio','Vergara','C',2.20),(162,'Dusan','Vlahovic','A',35.00),(163,'Kenan','Yıldız','A',50.00),(164,'Che','Adams','A',10.00),(165,'Michel','Aebischer','C',7.50),(166,'Nicolò','Barella','C',75.00),(167,'Andrea','Belotti','A',2.00),(168,'Domenico','Berardi','A',8.00),(169,'Alessandro','Circati','D',8.00),(170,'Benjamin','Dominguez','C',12.00),(171,'Denzel','Dumfries','D',35.00),(172,'Paulo','Dybala','C',8.00),(173,'Morten','Frendrup','C',20.00),(174,'Antonino','Gallo','D',4.30),(175,'Mario','Hermoso','D',7.00),(176,'Isak','Hien','D',30.00),(177,'Guillermo ','Maripan','D',4.00),(178,'Daniel','Maldini','A',10.00),(179,'Edoardo','Motta','C',0.30),(180,'David','Neres','C',30.00),(181,'Strahinja','Pavlovic','D',18.00),(182,'Matteo','Politano','C',10.00),(183,'Ivan','Provedel','P',3.00),(184,'Devyne','Rensch','D',10.00),(185,'Jesus','Rodriguez','D',30.00),(186,'Nicolò','Rovella','C',30.00),(187,'Adrian','Semper','P',3.50),(188,'Jamie','Vardy','A',1.00),(189,'Cristian','Volpato','C',6.50),(190,'Nicola','Zalewski','D',12.00),(191,'Gabriele','Zappa','D',4.00),(192,'Davide','Zappacosta','D',5.00),(193,'Piotr','Zielinski','C',10.00),(194,'Vasilije','Adzic','C',8.00),(195,'Zambo','Anguissa','C',27.00),(196,'Tino','Anjorin','C',6.00),(197,'Federico','Bernardeschi','C',3.50),(198,'Antoine','Bernede','C',2.50),(199,'Juan','Cabal','D',9.00),(200,'Michele','Collocolo','C',3.00),(201,'Enrico','Delprato','D',6.50),(202,'Michele','Di Gregorio','P',18.00),(203,'Artem','Dovbyk','A',30.00),(204,'Mattia','Felici','C',2.80),(205,'Santiago','Gimenez','A',30.00),(206,'Ardon','Jashari','C',32.00),(207,'Christian','Kabasele','D',0.70),(208,'Teun','Koopmeiners','C',35.00),(209,'Filip','Kostic','C',3.50),(210,'Armand','Laurientè','C',15.00),(211,'Santiago','Lovric','C',8.50),(212,'Romelu','Lukaku','A',22.00),(213,'J.','Miranda','C',15.00),(214,'Álvaro','Morata','A',11.00),(215,'Tarik','Muharemovic','D',7.00),(216,'Hans','Nicolussi Caviglia','C',8.50),(217,'Nico ','Paz','C',55.00),(218,'Mattia','Perin','P',2.50),(219,'Luca','Ranieri','D',12.00),(220,'Gianluca','Scamacca','A',24.00),(221,'K.','Sulemana','C',20.00),(222,'Zion','Suzuki','P',20.00),(223,'Fikayo','Tomori','D',20.00),(224,'Martin','Vitik','D',11.00),(225,'Nadir','Zortea','C',5.00),(226,'Davide','Bartesaghi','D',1.80),(227,'Alessandro','Bastoni','D',80.00),(228,'Lorenzo','Bernasconi','D',0.80),(229,'Alessandro','Buongiorno','D',50.00),(230,'Adrian','Bernabe','C',15.00),(231,'Cesare','Casadei','C',15.00),(232,'Jonathan','David','A',45.00),(233,'Fisayo','Dele-Bashiru','C',7.50),(234,'Giovanni','Di Lorenzo','D',12.00),(235,'Mikeal','Ellertsson','C',3.40),(236,'','Giovane','C',3.00),(237,'Abdou','Harroui','C',1.80),(238,'Emil','Holm','C',8.00),(239,'Manuel','Locatelli','C',30.00),(240,'Mike','Maignan','P',25.00),(241,'Donyell','Malen','A',25.00),(242,'Patrizio','Masini','C',6.00),(243,'Jens','Odgaard','A',12.00),(244,'Maduka','Okoye','P',7.50),(245,'Gaetano','Oristanio','C',6.00),(246,'Matteo','Pellegrino','C',6.00),(247,'Roberto','Piccoli','A',12.00),(248,'Marin','Pongracic','D',10.00),(249,'Amir','Rrahmani','D',12.00),(250,'Răzvan','Sava','P',2.50),(251,'Giorgio','Scalvini','D',35.00),(252,'Ibrahim','Sulemana','C',6.00),(253,'Pietro','Terracciano','D',1.00),(254,'Kialonda','Gaspar','D',3.50),(255,'Lorenzo','Torriani','P',0.50),(256,'Hassane','Kamara','D',3.00),(257,'Edon','Zhegrova','C',25.00),(258,'Arthur','Atta','C',8.00),(259,'Federico','Baschirotto','D',3.60),(260,'Raoul','Bellanova','D',24.00),(261,'Sam','Beukema','D',28.00),(262,'Simone','Canestrelli','D',7.00),(263,'Elia','Caprile','P',9.00),(264,'Lorenzo','Colombo','A',5.00),(265,'Bryan','Cristante','C',7.00),(266,'Keinan','Davis','A',4.00),(267,'Pervis','Estupinan','D',22.00),(268,'Niclas','Fullkrug','A',10.00),(269,'Mandela','Keita M.','C',12.00),(270,'Rafael','Leao','C',70.00),(271,'Ruben','Loftus-Cheek','C',10.00),(272,'Aaron','Martin','C',6.50),(273,'Henrik','Meister','C',2.80),(274,'Evan','N\'Dicka','D',30.00),(275,'Gift','Orban','D',10.00),(276,'Marco','Palestra','C',3.50),(277,'Lorenzo','Pellegrini','C',9.00),(278,'Federico','Ravaglia','P',1.50),(279,'Samuele','Ricci','C',25.00),(280,'Giovanni','Simeone','A',5.00),(281,'Lukasz','Skorupski','P',2.50),(282,'Riccardo','Sottil','C',5.00),(283,'Matias','Soulè','C',35.00),(284,'Filippo','Terracciano F.','D',3.20),(285,'Khéphren','Thuram','A',40.00),(286,'Johan','Vasquez','C',14.00),(287,'Justin','Bijlow','P',5.00),(288,'Iker','Bravo','D',5.00),(289,'Francesco','Camarda','A',10.00),(290,'Santiago','Castro','A',35.00),(291,'Fallou','Cham','D',0.15),(292,'Lucas','Da Cunha','C',10.00),(293,'Kevin','De Bruyne','C',20.00),(294,'Da Silva','Ederson','C',45.00),(295,'Eljif','Elmas','C',14.00),(296,'Jacopo','Fazzini','C',10.00),(297,'Remo','Freuler','C',5.00),(298,'Matteo','Gabbia','D',14.00),(299,'Gianluca','Gaetano','C',4.00),(300,'Federico','Gatti','D',24.00),(301,'Mario','Gila','D',30.00),(302,'Torbjørn','Heggem','D',1.20),(303,'Lloyd','Kelly','D',18.00),(304,'Semih','Kilicsoy','A',12.00),(305,'Isameò','Konè','C',12.00),(306,'Nikola','Krstovic','C',24.00),(307,'Nicola','Leali','P',1.50),(308,'Adam','Marusic','D',3.50),(309,'Christopher','Nkunku','A',35.00),(310,'Adrien','Rabiot','C',25.00),(311,'Jonathan','Rowe','A',12.00),(312,'Oumar','Solet','D',18.00),(313,'Leonardo','Spinazzola','D',3.50),(314,'Mile','Svilar','P',25.00),(315,'Mërgim','Vojvoda','D',3.00);
/*!40000 ALTER TABLE `giocatori` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operazioni_mercato`
--

DROP TABLE IF EXISTS `operazioni_mercato`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operazioni_mercato` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Stagione` varchar(9) NOT NULL,
  `Sessione` enum('Estiva','Invernale') NOT NULL,
  `SquadraID` int NOT NULL,
  `GiocatoreID` int NOT NULL,
  `Tipo` varchar(100) DEFAULT NULL,
  `Costo` decimal(10,2) DEFAULT '0.00',
  `Note` text,
  PRIMARY KEY (`ID`),
  KEY `SquadraID` (`SquadraID`),
  KEY `GiocatoreID` (`GiocatoreID`),
  CONSTRAINT `operazioni_mercato_ibfk_1` FOREIGN KEY (`SquadraID`) REFERENCES `fantasquadre` (`ID`),
  CONSTRAINT `operazioni_mercato_ibfk_2` FOREIGN KEY (`GiocatoreID`) REFERENCES `giocatori` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operazioni_mercato`
--

LOCK TABLES `operazioni_mercato` WRITE;
/*!40000 ALTER TABLE `operazioni_mercato` DISABLE KEYS */;
/*!40000 ALTER TABLE `operazioni_mercato` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `partite`
--

DROP TABLE IF EXISTS `partite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partite` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Stagione` varchar(9) DEFAULT NULL,
  `Giornata` int DEFAULT NULL,
  `SquadraCasaID` int DEFAULT NULL,
  `SquadraOspiteID` int DEFAULT NULL,
  `GolCasa` int DEFAULT NULL,
  `GolOspite` int DEFAULT NULL,
  `Giocata` tinyint(1) DEFAULT '0',
  `GuadagnoCasa` decimal(12,2) DEFAULT '0.00',
  `GuadagnoOspite` decimal(12,2) DEFAULT '0.00',
  `CompetizioneID` int NOT NULL DEFAULT '1',
  `Fase` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`,`CompetizioneID`),
  UNIQUE KEY `uq_partita` (`CompetizioneID`,`Stagione`,`Giornata`,`SquadraCasaID`,`SquadraOspiteID`),
  KEY `SquadraCasaID` (`SquadraCasaID`),
  KEY `SquadraOspiteID` (`SquadraOspiteID`),
  KEY `partite_ibfk_3_idx` (`CompetizioneID`),
  CONSTRAINT `partite_ibfk_1` FOREIGN KEY (`SquadraCasaID`) REFERENCES `fantasquadre` (`ID`),
  CONSTRAINT `partite_ibfk_2` FOREIGN KEY (`SquadraOspiteID`) REFERENCES `fantasquadre` (`ID`),
  CONSTRAINT `partite_ibfk_3` FOREIGN KEY (`CompetizioneID`) REFERENCES `competizioni` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `partite`
--

LOCK TABLES `partite` WRITE;
/*!40000 ALTER TABLE `partite` DISABLE KEYS */;
/*!40000 ALTER TABLE `partite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `premi_competizioni`
--

DROP TABLE IF EXISTS `premi_competizioni`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `premi_competizioni` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `CompetizioneID` int NOT NULL,
  `Fase` varchar(50) NOT NULL,
  `Premio` decimal(12,2) NOT NULL DEFAULT '0.00',
  `Ordine` int NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_fase` (`CompetizioneID`,`Fase`),
  CONSTRAINT `premi_competizioni_ibfk_1` FOREIGN KEY (`CompetizioneID`) REFERENCES `competizioni` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `premi_competizioni`
--

LOCK TABLES `premi_competizioni` WRITE;
/*!40000 ALTER TABLE `premi_competizioni` DISABLE KEYS */;
INSERT INTO `premi_competizioni` VALUES (1,1,'1',35.00,1),(2,1,'2',28.00,2),(3,1,'3',21.00,3),(4,1,'4',16.50,4),(5,1,'5',12.00,5),(6,1,'6',10.50,6),(7,1,'7',9.00,7),(8,1,'8',7.50,8),(9,1,'9',6.00,9),(10,1,'10',4.50,10),(11,2,'Quarti',5.00,1),(12,2,'Semifinale',5.00,2),(13,2,'Finale',5.00,3),(14,2,'Vittoria',15.00,4),(15,3,'Quarti',2.50,1),(16,3,'Semifinale',2.50,2),(17,3,'Finale',5.00,3),(18,3,'Vittoria',10.00,4),(19,4,'Ottavi',2.00,1),(20,4,'Quarti',2.00,2),(21,4,'Semifinale',4.00,3),(22,4,'Finale',4.50,4),(23,4,'Vittoria',12.50,5);
/*!40000 ALTER TABLE `premi_competizioni` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settori_giovanili`
--

DROP TABLE IF EXISTS `settori_giovanili`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settori_giovanili` (
  `SquadraID` int NOT NULL,
  `SlotMax` int NOT NULL DEFAULT '5',
  `SlotAcquistati` int NOT NULL DEFAULT '0',
  `CostoPerSlot` decimal(12,2) NOT NULL DEFAULT '20.00',
  `StipendioFissoGiovani` decimal(12,2) NOT NULL DEFAULT '0.10',
  PRIMARY KEY (`SquadraID`),
  CONSTRAINT `settori_giovanili_ibfk_1` FOREIGN KEY (`SquadraID`) REFERENCES `fantasquadre` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settori_giovanili`
--

LOCK TABLES `settori_giovanili` WRITE;
/*!40000 ALTER TABLE `settori_giovanili` DISABLE KEYS */;
INSERT INTO `settori_giovanili` VALUES (1,2,1,20.00,0.10),(2,1,1,20.00,0.10),(3,2,2,20.00,0.10),(4,1,0,20.00,0.10),(5,3,3,20.00,0.10),(6,1,1,20.00,0.10),(7,3,2,20.00,0.10),(8,1,1,20.00,0.10),(9,2,1,20.00,0.10),(10,3,3,20.00,0.10);
/*!40000 ALTER TABLE `settori_giovanili` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stadi`
--

DROP TABLE IF EXISTS `stadi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stadi` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `SquadraID` int NOT NULL,
  `Livello` int DEFAULT '1',
  `IncassoPartita` decimal(12,2) DEFAULT '50000.00',
  `Costo` decimal(12,2) DEFAULT '5000.00',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `SquadraID` (`SquadraID`),
  CONSTRAINT `stadi_ibfk_1` FOREIGN KEY (`SquadraID`) REFERENCES `fantasquadre` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stadi`
--

LOCK TABLES `stadi` WRITE;
/*!40000 ALTER TABLE `stadi` DISABLE KEYS */;
INSERT INTO `stadi` VALUES (1,1,1,2.00,120.00),(2,2,5,0.25,40.00),(3,3,3,1.00,80.00),(4,4,2,1.50,100.00),(5,5,5,0.25,40.00),(6,6,2,1.50,100.00),(7,7,3,1.00,80.00),(8,8,2,1.50,100.00),(9,9,3,1.00,80.00),(10,10,4,0.50,60.00);
/*!40000 ALTER TABLE `stadi` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-28 12:13:51
