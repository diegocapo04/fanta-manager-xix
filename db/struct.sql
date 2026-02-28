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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-28 12:14:14
