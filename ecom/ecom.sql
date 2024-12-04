/*
SQLyog Ultimate v10.00 Beta1
MySQL - 5.5.5-10.4.32-MariaDB : Database - ecom
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ecom` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `ecom`;

/*Table structure for table `accounts` */

DROP TABLE IF EXISTS `accounts`;

CREATE TABLE `accounts` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `verification` varchar(255) DEFAULT 'nonverified',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `accounts` */

insert  into `accounts`(`id`,`email`,`username`,`password`,`verification`) values (25,'fishbaitssgg@gmail.com','admin','scrypt:32768:8:1$rKL4jtxHys2WTTv4$12cde802b2783a9d2aa91d3e1c1a8701d137ff74afe257d6f71e271d57ecf202f32ef09635bbf983944dbb78b6a043497fc9b2465993c6b7bbe4d1907d2cd125','admin'),(26,'renzvillegas0912@gmail.com','user','scrypt:32768:8:1$tAd1XMUdhJ3Emmba$fad016f479749b42e44efa930f74fbcc0dc09b6541c99916cd2ff902bcfbd861c806ca9d143255a5d20387f65e57a5380c8c99af1969207bf2ba62d734ef5d57','verified'),(29,'superslimylemur@gmail.com','bigasbigas','scrypt:32768:8:1$2He4oNyMAsriQs10$3284a596424a3750b3be03f232e0655ed32e0880929fc268071afbab5b816e95a70056e2b9963a7624a83b19a006db17a33d777d801cc4f7e42539bd8f8d1636','verified');

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `buyer_id` int(11) DEFAULT NULL,
  `order_date` timestamp(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  `item_id` int(11) DEFAULT NULL,
  `quantity` int(11) NOT NULL DEFAULT 0,
  `total_price` decimal(10,2) DEFAULT NULL,
  `status` enum('pending','completed','cancelled') DEFAULT 'pending',
  PRIMARY KEY (`order_id`),
  KEY `order_id` (`order_id`),
  KEY `item_id` (`item_id`),
  KEY `buyer_id` (`buyer_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `products` (`productid`) ON UPDATE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders` */

insert  into `orders`(`order_id`,`buyer_id`,`order_date`,`item_id`,`quantity`,`total_price`,`status`) values (18,25,'2024-12-03 21:18:10.264477',3,2,'344.00','pending'),(19,25,'2024-12-03 22:16:58.179012',8,2,'60.00','pending'),(20,25,'2024-12-03 22:16:58.179012',4,2,'40.00','pending'),(21,25,'2024-12-03 22:16:58.179012',3,6,'1032.00','pending'),(22,26,'2024-12-04 11:37:35.830525',3,5,'860.00','pending');

/*Table structure for table `products` */

DROP TABLE IF EXISTS `products`;

CREATE TABLE `products` (
  `productid` int(255) NOT NULL AUTO_INCREMENT,
  `productname` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `productcategory` varchar(255) DEFAULT NULL,
  `productdescription` text DEFAULT NULL,
  `ownerid` int(255) DEFAULT NULL,
  `productimage` varchar(255) DEFAULT NULL,
  `productstock` int(255) NOT NULL DEFAULT 0,
  `discount_percentage` decimal(5,2) DEFAULT 0.00,
  PRIMARY KEY (`productid`),
  KEY `ownerid` (`ownerid`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`ownerid`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

insert  into `products`(`productid`,`productname`,`price`,`productcategory`,`productdescription`,`ownerid`,`productimage`,`productstock`,`discount_percentage`) values (3,'tea shirt','172.00','t-shirts','tea shirt',26,'uploads/tea_shirt.png',5,'5.00'),(4,'shirt','20.00','t-shirts','assssb',26,'uploads/tshirts.jpg',20,'0.00'),(7,'pants','15.00','pants','12412',26,'uploads/pants.png',10,'0.00'),(8,'amongus t-shirt','30.00','t-shirts','amongus',29,'uploads/tea_shirt.png',20,'0.00'),(9,'gunga jacket','450.00','jackets','232873',26,'uploads/jacket.png',20,'0.00');

/*Table structure for table `reviews` */

DROP TABLE IF EXISTS `reviews`;

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` >= 1 and `rating` <= 5),
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`productid`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `reviews` */

insert  into `reviews`(`id`,`product_id`,`user_id`,`rating`,`comment`,`created_at`) values (1,7,26,5,'good pants','2024-12-02 10:11:51'),(2,8,29,5,'amongus usussusu','2024-12-02 14:41:46'),(3,8,25,2,'panget','2024-12-03 21:26:53'),(4,3,26,4,'siraulo','2024-12-04 12:24:05');

/*Table structure for table `sellerapplication` */

DROP TABLE IF EXISTS `sellerapplication`;

CREATE TABLE `sellerapplication` (
  `request_id` int(255) NOT NULL AUTO_INCREMENT,
  `user_id` int(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `shop_description` text DEFAULT NULL,
  `status` varchar(255) DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp(),
  `province` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `barangay` varchar(255) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `phonenumber` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `sellerapplication_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `sellerapplication` */

insert  into `sellerapplication`(`request_id`,`user_id`,`email`,`shop_name`,`shop_description`,`status`,`created_at`,`province`,`city`,`barangay`,`postal_code`,`phonenumber`) values (15,26,'renzvillegas0912@gmail.com','Gunga Shop','jacket seller','approved','2024-12-03 17:56:20','laguna','santa cruz','bagumbayan','4009','090923'),(19,29,'superslimylemur@gmail.com','among','us','approved','2024-12-03 17:56:20','laguna','cavinti','mahipon','4013','096923');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
