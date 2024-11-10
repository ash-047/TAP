CREATE DATABASE  IF NOT EXISTS `tap` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tap`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: tap
-- ------------------------------------------------------
-- Server version	8.0.39

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
-- Table structure for table `approval`
--

DROP TABLE IF EXISTS `approval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `approval` (
  `TA_ID` varchar(21) NOT NULL,
  `Teacher_ID` varchar(15) NOT NULL,
  PRIMARY KEY (`TA_ID`),
  CONSTRAINT `approval_ibfk_1` FOREIGN KEY (`TA_ID`) REFERENCES `ta` (`TA_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `approval`
--

LOCK TABLES `approval` WRITE;
/*!40000 ALTER TABLE `approval` DISABLE KEYS */;
/*!40000 ALTER TABLE `approval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assigned`
--

DROP TABLE IF EXISTS `assigned`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assigned` (
  `Class_ID` varchar(21) NOT NULL,
  `TA_ID` varchar(21) NOT NULL,
  PRIMARY KEY (`Class_ID`,`TA_ID`),
  KEY `TA_ID` (`TA_ID`),
  CONSTRAINT `assigned_ibfk_1` FOREIGN KEY (`Class_ID`) REFERENCES `class` (`Class_ID`),
  CONSTRAINT `assigned_ibfk_2` FOREIGN KEY (`TA_ID`) REFERENCES `ta` (`TA_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assigned`
--

LOCK TABLES `assigned` WRITE;
/*!40000 ALTER TABLE `assigned` DISABLE KEYS */;
/*!40000 ALTER TABLE `assigned` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `belongs`
--

DROP TABLE IF EXISTS `belongs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `belongs` (
  `Class_ID` varchar(21) NOT NULL,
  `SRN` varchar(15) NOT NULL,
  PRIMARY KEY (`Class_ID`,`SRN`),
  KEY `SRN` (`SRN`),
  CONSTRAINT `belongs_ibfk_1` FOREIGN KEY (`Class_ID`) REFERENCES `class` (`Class_ID`),
  CONSTRAINT `belongs_ibfk_2` FOREIGN KEY (`SRN`) REFERENCES `student` (`SRN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `belongs`
--

LOCK TABLES `belongs` WRITE;
/*!40000 ALTER TABLE `belongs` DISABLE KEYS */;
/*!40000 ALTER TABLE `belongs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class` (
  `Class_ID` varchar(21) NOT NULL,
  `Semester` enum('1','2','3','4','5','6','7','8') NOT NULL,
  PRIMARY KEY (`Class_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `Course_ID` varchar(15) NOT NULL,
  `Course_Name` varchar(25) NOT NULL,
  `Course_Type` enum('Elective','Core') NOT NULL,
  PRIMARY KEY (`Course_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opts`
--

DROP TABLE IF EXISTS `opts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opts` (
  `SRN` varchar(15) NOT NULL,
  `Course_ID` varchar(15) NOT NULL,
  PRIMARY KEY (`SRN`,`Course_ID`),
  KEY `Course_ID` (`Course_ID`),
  CONSTRAINT `opts_ibfk_1` FOREIGN KEY (`SRN`) REFERENCES `student` (`SRN`),
  CONSTRAINT `opts_ibfk_2` FOREIGN KEY (`Course_ID`) REFERENCES `courses` (`Course_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opts`
--

LOCK TABLES `opts` WRITE;
/*!40000 ALTER TABLE `opts` DISABLE KEYS */;
/*!40000 ALTER TABLE `opts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `request`
--

DROP TABLE IF EXISTS `request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `request` (
  `SRN` varchar(15) NOT NULL,
  `Course_ID` varchar(15) NOT NULL,
  `Teacher_ID` varchar(15) NOT NULL,
  PRIMARY KEY (`SRN`, `Course_ID`),
  KEY `Course_ID` (`Course_ID`)
  CONSTRAINT `request_ibfk_1` FOREIGN KEY (`SRN`) REFERENCES `student` (`SRN`),
  CONSTRAINT `opts_ibfk_2` FOREIGN KEY (`Course_ID`) REFERENCES `courses` (`Course_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `request`
--

LOCK TABLES `request` WRITE;
/*!40000 ALTER TABLE `request` DISABLE KEYS */;
/*!40000 ALTER TABLE `request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `SRN` varchar(15) NOT NULL,
  `First_Name` varchar(25) NOT NULL,
  `Last_Name` varchar(25) NOT NULL,
  `YearOfJoining` year NOT NULL,
  PRIMARY KEY (`SRN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ta`
--

DROP TABLE IF EXISTS `ta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ta` (
  `TA_ID` varchar(21) NOT NULL,
  `SRN` varchar(15) NOT NULL,
  PRIMARY KEY (`TA_ID`,`SRN`),
  KEY `SRN` (`SRN`),
  CONSTRAINT `ta_ibfk_1` FOREIGN KEY (`SRN`) REFERENCES `student` (`SRN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ta`
--

LOCK TABLES `ta` WRITE;
/*!40000 ALTER TABLE `ta` DISABLE KEYS */;
/*!40000 ALTER TABLE `ta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ta_bank_details`
--

DROP TABLE IF EXISTS `ta_bank_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ta_bank_details` (
  `TA_ID` varchar(21) NOT NULL,
  `Bank_Name` varchar(25) NOT NULL,
  `Account_Number` varchar(15) NOT NULL,
  `ISFC_Code` varchar(11) NOT NULL,
  PRIMARY KEY (`TA_ID`),
  CONSTRAINT `ta_bank_details_ibfk_1` FOREIGN KEY (`TA_ID`) REFERENCES `ta` (`TA_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ta_bank_details`
--

LOCK TABLES `ta_bank_details` WRITE;
/*!40000 ALTER TABLE `ta_bank_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `ta_bank_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `Teacher_ID` varchar(15) NOT NULL,
  `Teacher_Name` varchar(25) NOT NULL,
  PRIMARY KEY (`Teacher_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teaches`
--

DROP TABLE IF EXISTS `teaches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teaches` (
  `Teacher_ID` varchar(15) NOT NULL,
  `Course_ID` varchar(15) NOT NULL,
  `Class_ID` varchar(21) NOT NULL,
  PRIMARY KEY (`Teacher_ID`,`Course_ID`,`Class_ID`),
  KEY `Course_ID` (`Course_ID`),
  KEY `Class_ID` (`Class_ID`),
  CONSTRAINT `teaches_ibfk_1` FOREIGN KEY (`Teacher_ID`) REFERENCES `teacher` (`Teacher_ID`),
  CONSTRAINT `teaches_ibfk_2` FOREIGN KEY (`Course_ID`) REFERENCES `courses` (`Course_ID`),
  CONSTRAINT `teaches_ibfk_3` FOREIGN KEY (`Class_ID`) REFERENCES `class` (`Class_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teaches`
--

LOCK TABLES `teaches` WRITE;
/*!40000 ALTER TABLE `teaches` DISABLE KEYS */;
/*!40000 ALTER TABLE `teaches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `worklog`
--

DROP TABLE IF EXISTS `worklog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `worklog` (
  `TA_ID` varchar(21) NOT NULL,
  `Course_ID` varchar(15) NOT NULL,
  `Start_Timestamp` timestamp NOT NULL,
  `Work_Description` varchar(300) NOT NULL,
  `End_Timestamp` timestamp NOT NULL,
  PRIMARY KEY (`TA_ID`,`Course_ID`),
  KEY `Course_ID` (`Course_ID`),
  CONSTRAINT `worklog_ibfk_1` FOREIGN KEY (`TA_ID`) REFERENCES `ta` (`TA_ID`),
  CONSTRAINT `worklog_ibfk_2` FOREIGN KEY (`Course_ID`) REFERENCES `courses` (`Course_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `worklog`
--

LOCK TABLES `worklog` WRITE;
/*!40000 ALTER TABLE `worklog` DISABLE KEYS */;
/*!40000 ALTER TABLE `worklog` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-18 22:00:05
