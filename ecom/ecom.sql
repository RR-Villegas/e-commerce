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
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `accounts` */

insert  into `accounts`(`id`,`email`,`username`,`password`,`verification`) values (20,'superslimylemur@gmail.com','Renz Rouei Villegas','scrypt:32768:8:1$NAYBjkmjD3XUvMEP$193c345a908f37df6f92989f283ddee0f46f765b02a98f2418173b1f6eca6ab41f1e368375a18035cff35be7133969a10db13d57a129a25db8921f3a342b8b7f','nonverified'),(25,'fishbaitssgg@gmail.com','admin','scrypt:32768:8:1$rKL4jtxHys2WTTv4$12cde802b2783a9d2aa91d3e1c1a8701d137ff74afe257d6f71e271d57ecf202f32ef09635bbf983944dbb78b6a043497fc9b2465993c6b7bbe4d1907d2cd125','admin'),(26,'renzvillegas0912@gmail.com','user','scrypt:32768:8:1$tAd1XMUdhJ3Emmba$fad016f479749b42e44efa930f74fbcc0dc09b6541c99916cd2ff902bcfbd861c806ca9d143255a5d20387f65e57a5380c8c99af1969207bf2ba62d734ef5d57','verified'),(27,'cosmicplayer124@gmail.com','Renz Renz','scrypt:32768:8:1$0i9w4NEVBhGAppX5$2f023b0501ab6dd033562a9014c61913f0ece8225b812370d0b2d60e2df0bca40e16947e3bb06b55bca551b395d240c92ca89844ee382b01927e3ec5f483e459','verified');

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `order_id` int(255) NOT NULL AUTO_INCREMENT,
  `buyer_id` int(255) DEFAULT NULL,
  `order_date` timestamp(6) NOT NULL DEFAULT current_timestamp(6) ON UPDATE current_timestamp(6),
  `item_id` int(255) DEFAULT NULL,
  `quantity` int(255) NOT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `order_id` (`order_id`),
  KEY `item_id` (`item_id`),
  KEY `buyer_id` (`buyer_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `products` (`productid`) ON UPDATE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders` */

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
  PRIMARY KEY (`productid`),
  KEY `ownerid` (`ownerid`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`ownerid`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

insert  into `products`(`productid`,`productname`,`price`,`productcategory`,`productdescription`,`ownerid`,`productimage`) values (2,'na shirt','727.00','t-shirts','nanaana',26,NULL),(3,'tea shirt','172.00','t-shirts','tea shirt',26,'static/uploads\\tea_shirt.png');

/*Table structure for table `sellerapplication` */

DROP TABLE IF EXISTS `sellerapplication`;

CREATE TABLE `sellerapplication` (
  `request_id` int(255) NOT NULL AUTO_INCREMENT,
  `user_id` int(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `shop_description` text DEFAULT NULL,
  `status` varchar(255) DEFAULT 'pending',
  PRIMARY KEY (`request_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `sellerapplication_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `sellerapplication` */

insert  into `sellerapplication`(`request_id`,`user_id`,`email`,`shop_name`,`shop_description`,`status`) values (15,26,'renzvillegas0912@gmail.com','Gunga Shop','jacket seller','approved'),(17,27,'cosmicplayer124@gmail.com','Lamaw','Lamaw shop','approved');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
