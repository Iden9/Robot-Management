-- --------------------------------------------------------
-- 主机:                           8.153.175.16
-- 服务器版本:                        8.0.41 - Source distribution
-- 服务器操作系统:                      Linux
-- HeidiSQL 版本:                  12.3.0.6589
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 导出 g1_edu 的数据库结构
DROP DATABASE IF EXISTS `g1_edu`;
CREATE DATABASE IF NOT EXISTS `g1_edu` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `g1_edu`;

-- 导出  表 g1_edu.alembic_version 结构
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.alembic_version 的数据：~1 rows (大约)
DELETE FROM `alembic_version`;
INSERT INTO `alembic_version` (`version_num`) VALUES
	('36e245a25e24');

-- 导出  存储过程 g1_edu.CleanupExpiredSessions 结构
DROP PROCEDURE IF EXISTS `CleanupExpiredSessions`;
DELIMITER //
CREATE PROCEDURE `CleanupExpiredSessions`()
BEGIN
    DELETE FROM `user_sessions` WHERE `expires_at` < NOW();
    SELECT ROW_COUNT() as deleted_sessions;
END//
DELIMITER ;

-- 导出  存储过程 g1_edu.CleanupTemporaryFiles 结构
DROP PROCEDURE IF EXISTS `CleanupTemporaryFiles`;
DELIMITER //
CREATE PROCEDURE `CleanupTemporaryFiles`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE file_path VARCHAR(500);
    DECLARE file_cursor CURSOR FOR 
        SELECT `file_path` FROM `file_storage` 
        WHERE `is_temporary` = 1 AND `created_at` < DATE_SUB(NOW(), INTERVAL 24 HOUR);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN file_cursor;
    
    cleanup_loop: LOOP
        FETCH file_cursor INTO file_path;
        IF done THEN
            LEAVE cleanup_loop;
        END IF;
        
        -- 这里可以添加删除物理文件的逻辑
        DELETE FROM `file_storage` WHERE `file_path` = file_path;
    END LOOP;
    
    CLOSE file_cursor;
    SELECT ROW_COUNT() as deleted_files;
END//
DELIMITER ;

-- 导出  表 g1_edu.courseware 结构
DROP TABLE IF EXISTS `courseware`;
CREATE TABLE IF NOT EXISTS `courseware` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '课件ID',
  `title` varchar(255) NOT NULL COMMENT '课件标题',
  `file_path` varchar(500) NOT NULL COMMENT '文件存储路径',
  `file_type` varchar(50) NOT NULL COMMENT '文件类型',
  `file_size` bigint NOT NULL COMMENT '文件大小(字节)',
  `description` text COMMENT '课件描述',
  `uploaded_by` int DEFAULT NULL COMMENT '上传用户ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `category_id` int DEFAULT NULL COMMENT '分类ID',
  `file_name` varchar(255) NOT NULL COMMENT '原始文件名',
  `mime_type` varchar(100) DEFAULT NULL COMMENT 'MIME类型',
  `tags` varchar(500) DEFAULT NULL COMMENT '标签，逗号分隔',
  `subject` varchar(100) DEFAULT NULL COMMENT '学科',
  `grade_level` varchar(50) DEFAULT NULL COMMENT '年级水平',
  `duration` int DEFAULT NULL COMMENT '播放时长(秒)',
  `thumbnail_path` varchar(500) DEFAULT NULL COMMENT '缩略图路径',
  `download_count` int DEFAULT NULL COMMENT '下载次数',
  `view_count` int DEFAULT NULL COMMENT '查看次数',
  `is_public` tinyint(1) DEFAULT NULL COMMENT '是否公开',
  `status` enum('draft','published','archived') DEFAULT NULL COMMENT '状态',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `uploaded_by` (`uploaded_by`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `courseware_ibfk_1` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `courseware_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `courseware_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.courseware 的数据：~0 rows (大约)
DELETE FROM `courseware`;
INSERT INTO `courseware` (`id`, `title`, `file_path`, `file_type`, `file_size`, `description`, `uploaded_by`, `created_at`, `category_id`, `file_name`, `mime_type`, `tags`, `subject`, `grade_level`, `duration`, `thumbnail_path`, `download_count`, `view_count`, `is_public`, `status`, `updated_at`) VALUES
	(9, '7307c89043e2b6388d5780073390acb9', '/Users/daixun/Desktop/recentProject/6.27_副本/backend/uploads/courseware/3559e5b8252e4fe0a85d6a568c49f907.jpeg', 'jpeg', 219585, 'chinese课件', 2, '2025-07-14 07:47:27', NULL, '7307c89043e2b6388d5780073390acb9.jpeg', 'image/jpeg', 'chinese', NULL, NULL, NULL, NULL, 0, 1, 1, 'published', '2025-07-14 07:47:30');

-- 导出  表 g1_edu.courseware_categories 结构
DROP TABLE IF EXISTS `courseware_categories`;
CREATE TABLE IF NOT EXISTS `courseware_categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  `name` varchar(100) NOT NULL COMMENT '分类名称',
  `description` text COMMENT '分类描述',
  `parent_id` int DEFAULT NULL COMMENT '父分类ID',
  `sort_order` int DEFAULT NULL COMMENT '排序序号',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `courseware_categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `courseware_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.courseware_categories 的数据：~5 rows (大约)
DELETE FROM `courseware_categories`;
INSERT INTO `courseware_categories` (`id`, `name`, `description`, `parent_id`, `sort_order`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, '基础编程', '编程入门和基础概念课程', NULL, 1, 1, '2025-07-04 13:48:20', '2025-07-04 13:48:20'),
	(2, '机器人控制', '机器人动作和控制相关课程', NULL, 2, 1, '2025-07-04 13:48:20', '2025-07-04 13:48:20'),
	(3, '人工智能', 'AI和机器学习基础课程', NULL, 3, 1, '2025-07-04 13:48:20', '2025-07-04 13:48:20'),
	(4, '交互设计', '人机交互和界面设计课程', NULL, 4, 1, '2025-07-04 13:48:20', '2025-07-04 13:48:20'),
	(5, '科学实验', '科学实验和探索课程', NULL, 5, 1, '2025-07-04 13:48:20', '2025-07-04 13:48:20');

-- 导出  表 g1_edu.courseware_usage 结构
DROP TABLE IF EXISTS `courseware_usage`;
CREATE TABLE IF NOT EXISTS `courseware_usage` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '使用记录ID',
  `courseware_id` int NOT NULL COMMENT '课件ID',
  `equipment_id` varchar(50) NOT NULL COMMENT '设备ID',
  `user_id` int DEFAULT NULL COMMENT '操作用户ID',
  `action` enum('play','download','view','share') NOT NULL COMMENT '操作类型',
  `duration` int DEFAULT NULL COMMENT '使用时长(秒)',
  `ip_address` varchar(50) DEFAULT NULL COMMENT 'IP地址',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `courseware_id` (`courseware_id`),
  KEY `equipment_id` (`equipment_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `courseware_usage_ibfk_1` FOREIGN KEY (`courseware_id`) REFERENCES `courseware` (`id`) ON DELETE CASCADE,
  CONSTRAINT `courseware_usage_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `courseware_usage_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.courseware_usage 的数据：~0 rows (大约)
DELETE FROM `courseware_usage`;
INSERT INTO `courseware_usage` (`id`, `courseware_id`, `equipment_id`, `user_id`, `action`, `duration`, `ip_address`, `created_at`) VALUES
	(59, 9, 'WEB-CLIENT', 2, 'view', NULL, '127.0.0.1', '2025-07-14 07:47:30');

-- 导出  表 g1_edu.dashboard_statistics 结构
DROP TABLE IF EXISTS `dashboard_statistics`;
CREATE TABLE IF NOT EXISTS `dashboard_statistics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `statistic_date` date NOT NULL,
  `total_online_devices` int DEFAULT NULL,
  `total_offline_devices` int DEFAULT NULL,
  `total_error_devices` int DEFAULT NULL,
  `total_courses_delivered` int DEFAULT NULL,
  `total_tours_conducted` int DEFAULT NULL,
  `total_interactions` int DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `statistic_hour` int DEFAULT NULL COMMENT '统计小时(0-23)',
  `total_devices` int DEFAULT NULL COMMENT '设备总数',
  `total_maintenance_devices` int DEFAULT NULL COMMENT '维护设备数',
  `total_users` int DEFAULT NULL COMMENT '用户总数',
  `active_users` int DEFAULT NULL COMMENT '活跃用户数',
  `total_courseware` int DEFAULT NULL COMMENT '课件总数',
  `total_navigation_points` int DEFAULT NULL COMMENT '导览点总数',
  `total_operations` int DEFAULT NULL COMMENT '操作总数',
  `failed_operations` int DEFAULT NULL COMMENT '失败操作数',
  `average_response_time` decimal(8,2) DEFAULT NULL COMMENT '平均响应时间(毫秒)',
  `peak_concurrent_users` int DEFAULT NULL COMMENT '并发用户峰值',
  `total_data_transfer` bigint DEFAULT NULL COMMENT '数据传输量(字节)',
  `system_uptime` int DEFAULT NULL COMMENT '系统运行时间(秒)',
  `error_rate` decimal(5,2) DEFAULT NULL COMMENT '错误率(%)',
  `performance_score` decimal(5,2) DEFAULT NULL COMMENT '性能评分',
  `additional_metrics` text COMMENT '额外指标(JSON)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.dashboard_statistics 的数据：~1 rows (大约)
DELETE FROM `dashboard_statistics`;
INSERT INTO `dashboard_statistics` (`id`, `statistic_date`, `total_online_devices`, `total_offline_devices`, `total_error_devices`, `total_courses_delivered`, `total_tours_conducted`, `total_interactions`, `created_at`, `statistic_hour`, `total_devices`, `total_maintenance_devices`, `total_users`, `active_users`, `total_courseware`, `total_navigation_points`, `total_operations`, `failed_operations`, `average_response_time`, `peak_concurrent_users`, `total_data_transfer`, `system_uptime`, `error_rate`, `performance_score`, `additional_metrics`) VALUES
	(1, '2025-07-02', 1, 0, 0, 5, 3, 0, '2025-07-02 11:57:45', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- 导出  表 g1_edu.education_settings 结构
DROP TABLE IF EXISTS `education_settings`;
CREATE TABLE IF NOT EXISTS `education_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_id` varchar(50) NOT NULL,
  `screen_sync_mode` enum('auto','manual','off') DEFAULT NULL,
  `ai_platform` varchar(50) DEFAULT NULL,
  `subject` varchar(50) DEFAULT NULL,
  `voice_type` varchar(50) DEFAULT NULL,
  `robot_action` varchar(50) DEFAULT NULL,
  `hand_recognition` tinyint(1) DEFAULT NULL,
  `interactive_qa` tinyint(1) DEFAULT NULL,
  `navigation_mode` varchar(50) DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_id` (`equipment_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `education_settings_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `education_settings_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.education_settings 的数据：~2 rows (大约)
DELETE FROM `education_settings`;
INSERT INTO `education_settings` (`id`, `equipment_id`, `screen_sync_mode`, `ai_platform`, `subject`, `voice_type`, `robot_action`, `hand_recognition`, `interactive_qa`, `navigation_mode`, `updated_at`, `updated_by`) VALUES
	(1, 'G1-EDU-TEST-001', 'auto', 'xunfei', 'Mathematics', 'male', 'standard', 1, 1, 'default', '2025-07-02 11:57:45', 2),
	(11, '7121312', 'auto', 'xunfei', 'chinese', 'male', 'standard', 1, 1, 'default', '2025-07-13 12:54:38', 2);

-- 导出  表 g1_edu.equipment 结构
DROP TABLE IF EXISTS `equipment`;
CREATE TABLE IF NOT EXISTS `equipment` (
  `id` varchar(50) NOT NULL,
  `location` varchar(255) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `last_active` datetime DEFAULT NULL,
  `usage_rate` varchar(10) DEFAULT NULL,
  `is_offline` tinyint(1) DEFAULT NULL,
  `has_error` tinyint(1) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.equipment 的数据：~3 rows (大约)
DELETE FROM `equipment`;
INSERT INTO `equipment` (`id`, `location`, `status`, `ip_address`, `last_active`, `usage_rate`, `is_offline`, `has_error`, `created_at`, `updated_at`) VALUES
	('7121312', 'test', 'online', '192.168.31.255', '2025-07-16 17:02:14', '0%', 0, 0, '2025-07-11 17:06:46', '2025-07-16 17:02:14'),
	('G1-EDU-TEST-001', 'Test Location', 'online', '192.168.1.100', '2025-07-13 10:17:05', NULL, 0, 0, '2025-07-02 11:57:27', '2025-07-13 10:17:05'),
	('WEB-CLIENT', '网页客户端', 'online', '127.0.0.1', '2025-07-13 10:17:05', '0%', 0, 0, '2025-07-13 06:40:46', '2025-07-13 10:17:05');

-- 导出  表 g1_edu.equipment_logs 结构
DROP TABLE IF EXISTS `equipment_logs`;
CREATE TABLE IF NOT EXISTS `equipment_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_id` varchar(50) NOT NULL,
  `log_type` enum('error','warning','info','debug') NOT NULL,
  `message` text,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_id` (`equipment_id`),
  CONSTRAINT `equipment_logs_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.equipment_logs 的数据：~1 rows (大约)
DELETE FROM `equipment_logs`;
INSERT INTO `equipment_logs` (`id`, `equipment_id`, `log_type`, `message`, `created_at`) VALUES
	(1, 'G1-EDU-TEST-001', 'info', 'Test log message', '2025-07-02 11:57:27');

-- 导出  表 g1_edu.equipment_status_history 结构
DROP TABLE IF EXISTS `equipment_status_history`;
CREATE TABLE IF NOT EXISTS `equipment_status_history` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '历史记录ID',
  `equipment_id` varchar(50) NOT NULL COMMENT '设备ID',
  `previous_status` varchar(50) DEFAULT NULL COMMENT '之前状态',
  `current_status` varchar(50) NOT NULL COMMENT '当前状态',
  `change_reason` varchar(255) DEFAULT NULL COMMENT '状态变更原因',
  `changed_by` int DEFAULT NULL COMMENT '操作用户ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `changed_by` (`changed_by`),
  KEY `equipment_id` (`equipment_id`),
  CONSTRAINT `equipment_status_history_ibfk_1` FOREIGN KEY (`changed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `equipment_status_history_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.equipment_status_history 的数据：~0 rows (大约)
DELETE FROM `equipment_status_history`;

-- 导出  表 g1_edu.knowledge_base 结构
DROP TABLE IF EXISTS `knowledge_base`;
CREATE TABLE IF NOT EXISTS `knowledge_base` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '知识库ID',
  `title` varchar(255) NOT NULL COMMENT '标题',
  `content` text NOT NULL COMMENT '内容',
  `description` text COMMENT '描述',
  `category` varchar(100) DEFAULT NULL COMMENT '分类',
  `tags` varchar(500) DEFAULT NULL COMMENT '标签，逗号分隔',
  `type` enum('text','document','link','faq') DEFAULT NULL COMMENT '知识类型',
  `status` enum('draft','published','archived') DEFAULT NULL COMMENT '状态',
  `priority` int DEFAULT NULL COMMENT '优先级',
  `view_count` int DEFAULT NULL COMMENT '查看次数',
  `usage_count` int DEFAULT NULL COMMENT '使用次数',
  `is_public` tinyint(1) DEFAULT NULL COMMENT '是否公开',
  `source_url` varchar(500) DEFAULT NULL COMMENT '来源链接',
  `source_type` varchar(50) DEFAULT NULL COMMENT '来源类型',
  `created_by` int DEFAULT NULL COMMENT '创建用户ID',
  `updated_by` int DEFAULT NULL COMMENT '更新用户ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `knowledge_base_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `knowledge_base_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.knowledge_base 的数据：~0 rows (大约)
DELETE FROM `knowledge_base`;
INSERT INTO `knowledge_base` (`id`, `title`, `content`, `description`, `category`, `tags`, `type`, `status`, `priority`, `view_count`, `usage_count`, `is_public`, `source_url`, `source_type`, `created_by`, `updated_by`, `created_at`, `updated_at`) VALUES
	(1, 'test', 'test', 'test', '', 'test', 'text', 'published', 0, 0, 0, 1, 'test', '', 2, 2, '2025-07-14 17:30:28', '2025-07-14 17:30:28'),
	(2, '1121', '1212', '1212', '', NULL, 'text', 'published', 0, 0, 0, 1, '', '', 2, 2, '2025-07-17 06:37:08', '2025-07-17 06:37:08');

-- 导出  表 g1_edu.menus 结构
DROP TABLE IF EXISTS `menus`;
CREATE TABLE IF NOT EXISTS `menus` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
  `name` varchar(100) NOT NULL COMMENT '菜单名称',
  `title` varchar(100) NOT NULL COMMENT '菜单标题',
  `path` varchar(200) DEFAULT NULL COMMENT '路由路径',
  `component` varchar(200) DEFAULT NULL COMMENT '组件路径',
  `icon` varchar(100) DEFAULT NULL COMMENT '菜单图标',
  `parent_id` int DEFAULT NULL COMMENT '父菜单ID',
  `sort_order` int DEFAULT NULL COMMENT '排序',
  `menu_type` enum('directory','menu','button') DEFAULT NULL COMMENT '菜单类型',
  `is_hidden` tinyint(1) DEFAULT NULL COMMENT '是否隐藏',
  `is_keepalive` tinyint(1) DEFAULT NULL COMMENT '是否缓存',
  `is_affix` tinyint(1) DEFAULT NULL COMMENT '是否固定标签',
  `redirect` varchar(200) DEFAULT NULL COMMENT '重定向路径',
  `permission_code` varchar(100) DEFAULT NULL COMMENT '权限编码',
  `status` tinyint(1) DEFAULT NULL COMMENT '状态',
  `created_by` int DEFAULT NULL COMMENT '创建人',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `menus_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `menus` (`id`) ON DELETE CASCADE,
  CONSTRAINT `menus_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.menus 的数据：~15 rows (大约)
DELETE FROM `menus`;
INSERT INTO `menus` (`id`, `name`, `title`, `path`, `component`, `icon`, `parent_id`, `sort_order`, `menu_type`, `is_hidden`, `is_keepalive`, `is_affix`, `redirect`, `permission_code`, `status`, `created_by`, `created_at`, `updated_at`) VALUES
	(1, 'system', '系统管理', '/system', 'Layout', 'system', NULL, 1, 'directory', 0, 1, 0, NULL, 'dashboard:view', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(2, 'dashboard', '系统看板', '/dashboard', 'SystemDashboard', 'dashboard', 1, 1, 'menu', 0, 1, 0, NULL, 'dashboard:view', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(3, 'equipment-management', '设备管理', '/equipment', 'Layout', 'equipment', NULL, 2, 'directory', 0, 1, 0, NULL, NULL, 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(4, 'equipment-list', '设备列表', '/equipment/list', 'EquipmentManagement', 'list', 3, 1, 'menu', 0, 1, 0, NULL, 'equipment:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(5, 'robot-control', '机器人控制', '/equipment/control', 'RobotControl', 'control', 3, 2, 'menu', 0, 1, 0, NULL, 'equipment:control', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(6, 'courseware-management', '课件管理', '/courseware', 'Layout', 'courseware', NULL, 3, 'directory', 0, 1, 0, NULL, NULL, 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(7, 'courseware-list', '课件列表', '/courseware/list', 'CoursewareManagement', 'list', 6, 1, 'menu', 0, 1, 0, NULL, 'courseware:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(8, 'navigation', '导航管理', '/navigation', 'SelfGuidedNavigation', 'navigation', NULL, 4, 'menu', 0, 1, 0, NULL, 'navigation:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(9, 'education', '教育模块', '/education', 'EducationModule', 'education', NULL, 5, 'menu', 0, 1, 0, NULL, 'education:view', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(10, 'user-management', '账号管理', '/users', 'AccountManagement', 'user', NULL, 6, 'menu', 0, 1, 0, NULL, 'user:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(11, 'permission-management', '权限管理', '/permission', 'Layout', 'permission', NULL, 7, 'directory', 0, 1, 0, NULL, NULL, 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(12, 'role-management', '角色管理', '/permission/roles', 'RoleManagement', 'role', 11, 1, 'menu', 0, 1, 0, NULL, 'role:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(13, 'menu-management', '菜单管理', '/permission/menus', 'MenuManagement', 'menu', 11, 2, 'menu', 0, 1, 0, NULL, 'menu:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(14, 'permission-list', '权限管理', '/permission/permissions', 'PermissionManagement', 'permission-list', 11, 3, 'menu', 0, 1, 0, NULL, 'permission:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:13:23'),
	(15, 'log-management', '日志管理', '/logs', 'LogManagement', 'log', NULL, 8, 'menu', 0, 1, 0, NULL, 'log:list', 1, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53');

-- 导出  表 g1_edu.navigation_points 结构
DROP TABLE IF EXISTS `navigation_points`;
CREATE TABLE IF NOT EXISTS `navigation_points` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_id` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text,
  `x_position` float NOT NULL,
  `y_position` float NOT NULL,
  `rotation` float DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_id` (`equipment_id`),
  CONSTRAINT `navigation_points_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.navigation_points 的数据：~1 rows (大约)
DELETE FROM `navigation_points`;
INSERT INTO `navigation_points` (`id`, `equipment_id`, `name`, `description`, `x_position`, `y_position`, `rotation`, `enabled`) VALUES
	(1, 'G1-EDU-TEST-001', 'Entrance', 'Main entrance point', 0, 0, 0, 1);

-- 导出  表 g1_edu.navigation_settings 结构
DROP TABLE IF EXISTS `navigation_settings`;
CREATE TABLE IF NOT EXISTS `navigation_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipment_id` varchar(50) NOT NULL,
  `scene_type` varchar(50) DEFAULT NULL,
  `ai_platform` varchar(50) DEFAULT NULL,
  `voice_type` varchar(50) DEFAULT NULL,
  `scene_prompt` text,
  `object_recognition` tinyint(1) DEFAULT NULL,
  `recognition_action` varchar(50) DEFAULT NULL,
  `auto_follow` tinyint(1) DEFAULT NULL,
  `patrol_mode` varchar(50) DEFAULT NULL,
  `navigation_mode` varchar(50) DEFAULT NULL,
  `emergency_alert` tinyint(1) DEFAULT NULL,
  `alert_mode` varchar(50) DEFAULT NULL,
  `robot_speed` int DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `updated_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_id` (`equipment_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `navigation_settings_ibfk_1` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `navigation_settings_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.navigation_settings 的数据：~0 rows (大约)
DELETE FROM `navigation_settings`;
INSERT INTO `navigation_settings` (`id`, `equipment_id`, `scene_type`, `ai_platform`, `voice_type`, `scene_prompt`, `object_recognition`, `recognition_action`, `auto_follow`, `patrol_mode`, `navigation_mode`, `emergency_alert`, `alert_mode`, `robot_speed`, `updated_at`, `updated_by`) VALUES
	(1, 'G1-EDU-TEST-001', 'scenic', 'xunfei', 'male', NULL, 1, 'move', 0, 'standard', 'dynamic', 1, 'auto', 60, '2025-07-02 11:57:45', 2);

-- 导出  表 g1_edu.operation_logs 结构
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE IF NOT EXISTS `operation_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(255) NOT NULL,
  `details` text,
  `ip_address` varchar(50) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=337 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.operation_logs 的数据：~327 rows (大约)
DELETE FROM `operation_logs`;
INSERT INTO `operation_logs` (`id`, `user_id`, `action`, `details`, `ip_address`, `created_at`) VALUES
	(1, 2, '设备操作: 启动设备', '设备ID: G1-EDU-TEST-001', '192.168.1.10', '2025-07-02 11:57:45'),
	(2, 2, '用户登录', NULL, '127.0.0.1', '2025-07-02 15:25:36'),
	(3, 2, '用户登录', NULL, '127.0.0.1', '2025-07-02 15:26:00'),
	(4, 2, '用户登录', NULL, '127.0.0.1', '2025-07-02 15:28:45'),
	(5, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:30:24'),
	(6, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:30:35'),
	(7, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:34:32'),
	(8, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:47:55'),
	(9, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:48:42'),
	(10, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:51:40'),
	(11, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:52:17'),
	(12, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:52:46'),
	(13, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:52:58'),
	(14, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:53:29'),
	(15, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 09:53:42'),
	(16, 2, '用户登出', NULL, '127.0.0.1', '2025-07-04 09:53:42'),
	(17, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 10:03:09'),
	(18, 2, '重置密码: admin', '用户ID: 2', '127.0.0.1', '2025-07-04 10:21:21'),
	(19, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 13:17:04'),
	(20, 3, '用户登录', NULL, '127.0.0.1', '2025-07-04 13:17:29'),
	(21, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 13:17:51'),
	(22, NULL, '用户登录', NULL, '127.0.0.1', '2025-07-04 13:18:42'),
	(23, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 13:50:27'),
	(26, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:03:03'),
	(27, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:03:07'),
	(28, 2, '重置密码: user1', '用户ID: 3', '127.0.0.1', '2025-07-04 14:05:26'),
	(29, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:06:10'),
	(30, 2, '更新教育培训设置: 设备123', '设置项: AI平台=baidu, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:06:16'),
	(31, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:06:48'),
	(32, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:08:16'),
	(33, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-04 14:08:17'),
	(34, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=english, 语音=male', '127.0.0.1', '2025-07-04 14:08:19'),
	(36, 2, '创建导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-04 14:16:29'),
	(37, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-04 14:16:30'),
	(38, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-04 14:17:24'),
	(39, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-04 14:17:41'),
	(40, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-04 14:17:51'),
	(41, 2, '用户登出', NULL, '127.0.0.1', '2025-07-04 14:19:16'),
	(42, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 14:19:36'),
	(43, 2, '重置密码: user1', '用户ID: 3', '127.0.0.1', '2025-07-04 14:19:50'),
	(44, 2, '用户登出', NULL, '127.0.0.1', '2025-07-04 14:20:11'),
	(45, 3, '用户登录', NULL, '127.0.0.1', '2025-07-04 14:20:17'),
	(46, 3, '用户登出', NULL, '127.0.0.1', '2025-07-04 14:35:14'),
	(47, 2, '用户登录', NULL, '127.0.0.1', '2025-07-04 14:35:21'),
	(48, 2, '用户登出', NULL, '127.0.0.1', '2025-07-05 03:34:42'),
	(49, 2, '用户登录', NULL, '127.0.0.1', '2025-07-05 03:34:52'),
	(50, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-05 03:37:41'),
	(51, 2, '删除用户: test', '用户ID: 4', '127.0.0.1', '2025-07-05 03:39:54'),
	(52, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-05 03:42:16'),
	(53, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-05 03:42:19'),
	(54, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-05 03:42:25'),
	(55, 2, '用户登出', NULL, '127.0.0.1', '2025-07-05 03:42:33'),
	(56, 2, '用户登录', NULL, '127.0.0.1', '2025-07-05 04:55:16'),
	(57, 2, '用户登录', NULL, '127.0.0.1', '2025-07-06 08:37:43'),
	(58, 2, '用户登出', NULL, '127.0.0.1', '2025-07-06 08:37:53'),
	(59, 2, '用户登录', NULL, '127.0.0.1', '2025-07-06 08:38:03'),
	(60, 2, '用户登出', NULL, '127.0.0.1', '2025-07-06 08:38:06'),
	(61, 3, '用户登录', NULL, '127.0.0.1', '2025-07-06 08:38:37'),
	(62, 3, '用户登出', NULL, '127.0.0.1', '2025-07-06 08:38:56'),
	(63, 2, '用户登录', NULL, '127.0.0.1', '2025-07-06 08:39:03'),
	(64, 2, '用户登出', NULL, '127.0.0.1', '2025-07-06 08:41:00'),
	(65, 2, '用户登录', NULL, '127.0.0.1', '2025-07-06 08:42:19'),
	(66, 7, '用户注册', '用户名: 123456, 邮箱: 1@qq.com', '127.0.0.1', '2025-07-09 16:33:50'),
	(67, 7, '用户登录', NULL, '127.0.0.1', '2025-07-09 16:33:59'),
	(68, 7, '用户登出', NULL, '127.0.0.1', '2025-07-09 16:34:02'),
	(69, 7, '用户登录', NULL, '127.0.0.1', '2025-07-09 16:34:10'),
	(70, 7, '用户登出', NULL, '127.0.0.1', '2025-07-09 16:34:28'),
	(71, 7, '用户登录', NULL, '127.0.0.1', '2025-07-10 02:10:58'),
	(72, 7, '用户登出', NULL, '127.0.0.1', '2025-07-10 02:11:04'),
	(73, 7, '用户登录', NULL, '127.0.0.1', '2025-07-10 02:11:56'),
	(74, 7, '用户登出', NULL, '127.0.0.1', '2025-07-10 02:32:48'),
	(75, 7, '用户登录', NULL, '127.0.0.1', '2025-07-10 02:32:58'),
	(76, 7, '用户登出', NULL, '127.0.0.1', '2025-07-10 02:33:23'),
	(77, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 06:20:55'),
	(78, 2, '更新用户: operator', '用户ID: 5', '127.0.0.1', '2025-07-11 06:28:53'),
	(79, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 06:29:41'),
	(80, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 12:21:33'),
	(81, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 12:21:42'),
	(82, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 12:25:53'),
	(83, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 12:26:10'),
	(84, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 12:27:01'),
	(85, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 12:52:29'),
	(86, 7, '用户登录', NULL, '127.0.0.1', '2025-07-11 12:52:38'),
	(87, 7, '用户登出', NULL, '127.0.0.1', '2025-07-11 12:52:45'),
	(88, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 12:52:51'),
	(89, 2, '设备控制: stop', '设备ID: 1234', '127.0.0.1', '2025-07-11 12:55:19'),
	(90, 2, '设备控制: stop', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 12:55:22'),
	(91, 2, '设备控制: stop', '设备ID: test', '127.0.0.1', '2025-07-11 12:55:27'),
	(92, 2, '设备控制: stop', '设备ID: test123', '127.0.0.1', '2025-07-11 12:55:31'),
	(93, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-11 12:55:42'),
	(94, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-11 12:55:42'),
	(95, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-11 12:55:42'),
	(96, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 12:55:42'),
	(97, 2, '设备控制: start', '设备ID: test1234', '127.0.0.1', '2025-07-11 12:55:42'),
	(98, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-11 12:55:42'),
	(99, 2, '创建设备', '设备ID: test1234531', '127.0.0.1', '2025-07-11 12:56:07'),
	(100, 2, '设备控制: restart', '设备ID: test1234531', '127.0.0.1', '2025-07-11 12:56:35'),
	(101, 2, '设备控制: stop', '设备ID: 123', '127.0.0.1', '2025-07-11 12:59:49'),
	(102, 2, '删除设备', '设备ID: test1234', '127.0.0.1', '2025-07-11 13:01:38'),
	(103, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 13:02:03'),
	(104, 7, '用户登录', NULL, '127.0.0.1', '2025-07-11 13:02:20'),
	(105, 7, '用户登出', NULL, '127.0.0.1', '2025-07-11 13:03:06'),
	(106, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 13:11:51'),
	(107, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 13:48:07'),
	(108, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 13:51:00'),
	(109, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 16:40:21'),
	(110, 7, '用户登录', NULL, '127.0.0.1', '2025-07-11 16:40:28'),
	(111, 7, '用户登出', NULL, '127.0.0.1', '2025-07-11 16:41:36'),
	(112, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 16:41:41'),
	(113, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-11 17:02:48'),
	(114, 2, '设备控制: start', '设备ID: test1234531', '127.0.0.1', '2025-07-11 17:02:48'),
	(115, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-11 17:02:48'),
	(116, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-11 17:02:48'),
	(117, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 17:02:48'),
	(118, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-11 17:02:48'),
	(119, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 17:02:50'),
	(120, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-11 17:02:50'),
	(121, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-11 17:02:50'),
	(122, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-11 17:02:50'),
	(123, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-11 17:02:50'),
	(124, 2, '设备控制: start', '设备ID: test1234531', '127.0.0.1', '2025-07-11 17:02:50'),
	(125, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-11 17:06:22'),
	(126, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-11 17:06:26'),
	(127, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-11 17:06:26'),
	(128, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 17:06:26'),
	(129, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-11 17:06:26'),
	(130, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-11 17:06:26'),
	(131, 2, '设备控制: start', '设备ID: test1234531', '127.0.0.1', '2025-07-11 17:06:26'),
	(132, 2, '创建设备', '设备ID: 7121312', '127.0.0.1', '2025-07-11 17:06:46'),
	(133, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-11 17:06:54'),
	(134, 2, '更新导览设置: 设备123', '设置项: 场景=scenic, AI平台=xunfei, 语音=male', '127.0.0.1', '2025-07-11 17:06:54'),
	(135, 2, '更新设备信息', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 17:07:04'),
	(136, 2, '设备控制: restart', '设备ID: test', '127.0.0.1', '2025-07-11 17:08:20'),
	(137, 2, '设备控制: stop', '设备ID: 1234', '127.0.0.1', '2025-07-11 17:08:36'),
	(138, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 17:09:04'),
	(139, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 17:09:11'),
	(140, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:11:37'),
	(141, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:13:10'),
	(142, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:13:51'),
	(143, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:14:01'),
	(144, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:14:04'),
	(145, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:16:39'),
	(146, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:18:54'),
	(147, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:19:01'),
	(148, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:19:32'),
	(149, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:20:32'),
	(150, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 17:21:02'),
	(151, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-11 17:22:47'),
	(152, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:22:57'),
	(153, 7, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:23:03'),
	(154, 7, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:23:17'),
	(155, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:23:24'),
	(156, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-11 17:23:46'),
	(157, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-11 17:23:46'),
	(158, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-11 17:23:46'),
	(159, 2, '设备控制: start', '设备ID: 7121312', '127.0.0.1', '2025-07-11 17:23:46'),
	(160, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-11 17:23:46'),
	(161, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-11 17:23:46'),
	(162, 2, '设备控制: start', '设备ID: test1234531', '127.0.0.1', '2025-07-11 17:23:46'),
	(163, 2, '更新用户: viewer', '用户ID: 6', '127.0.0.1', '2025-07-11 17:24:18'),
	(164, 2, '更新用户: admin', '用户ID: 2', '127.0.0.1', '2025-07-11 17:24:46'),
	(165, 2, '更新用户: user1', '用户ID: 3', '127.0.0.1', '2025-07-11 17:24:55'),
	(166, 2, '更新用户: viewer', '用户ID: 6', '127.0.0.1', '2025-07-11 17:24:59'),
	(167, 2, '用户登出', NULL, '127.0.0.1', '2025-07-11 17:43:28'),
	(168, 2, '用户登录', NULL, '127.0.0.1', '2025-07-11 17:47:37'),
	(169, 2, '上传课件: 8e28f16bb9be6959713909f25b9c76bb', '课件ID: 2', '127.0.0.1', '2025-07-11 18:00:45'),
	(170, 2, '用户登出', NULL, '127.0.0.1', '2025-07-12 07:11:27'),
	(171, 2, '用户登录', NULL, '127.0.0.1', '2025-07-12 07:12:40'),
	(172, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:38:34'),
	(173, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 02:39:26'),
	(174, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-13 02:39:36'),
	(175, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:39:40'),
	(176, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 02:39:45'),
	(177, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:40:04'),
	(178, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 02:44:58'),
	(179, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:45:09'),
	(180, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 02:46:36'),
	(181, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:51:29'),
	(182, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 02:51:39'),
	(183, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 02:54:26'),
	(184, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 03:00:42'),
	(185, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 03:13:39'),
	(186, 2, '创建角色', '角色名称: test, 角色编码: a_1', '127.0.0.1', '2025-07-13 03:24:44'),
	(187, 2, '分配角色权限', '角色: test, 权限数量: 0', '127.0.0.1', '2025-07-13 03:43:54'),
	(188, 2, '更新角色', '角色名称: test, 角色编码: a_1', '127.0.0.1', '2025-07-13 03:44:47'),
	(189, 2, '更新角色', '角色名称: test, 角色编码: a_1', '127.0.0.1', '2025-07-13 04:02:04'),
	(190, 2, '更新角色', '角色名称: 测试角色名称, 角色编码: a_1', '127.0.0.1', '2025-07-13 04:02:25'),
	(191, 2, '更新角色', '角色名称: 测试角色名称, 角色编码: a_1', '127.0.0.1', '2025-07-13 04:06:32'),
	(192, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-13 04:06:41'),
	(193, 2, '重置密码: 123456', '用户ID: 7', '127.0.0.1', '2025-07-13 04:07:04'),
	(194, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:07:06'),
	(195, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:07:13'),
	(196, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:07:27'),
	(197, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:07:34'),
	(198, 2, '分配角色权限', '角色: 测试角色名称, 权限数量: 2', '127.0.0.1', '2025-07-13 04:08:07'),
	(199, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:08:11'),
	(200, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:08:16'),
	(201, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:09:43'),
	(202, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:09:50'),
	(203, 2, '创建角色', '角色名称: 测试角色2, 角色编码: a_2', '127.0.0.1', '2025-07-13 04:10:19'),
	(204, 2, '更新角色', '角色名称: 测试角色21, 角色编码: a_2', '127.0.0.1', '2025-07-13 04:10:31'),
	(205, 2, '更新用户: 123456', '用户ID: 7', '127.0.0.1', '2025-07-13 04:11:31'),
	(206, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:20:36'),
	(207, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:20:42'),
	(208, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:20:50'),
	(209, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:20:56'),
	(210, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 1', '127.0.0.1', '2025-07-13 04:21:07'),
	(211, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 3', '127.0.0.1', '2025-07-13 04:21:19'),
	(212, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:21:22'),
	(213, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:21:30'),
	(214, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:21:35'),
	(215, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:21:41'),
	(216, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 44', '127.0.0.1', '2025-07-13 04:22:23'),
	(217, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:22:28'),
	(218, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:22:34'),
	(219, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:23:12'),
	(220, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:23:19'),
	(221, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 2', '127.0.0.1', '2025-07-13 04:23:39'),
	(222, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 2', '127.0.0.1', '2025-07-13 04:24:10'),
	(223, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:26:11'),
	(224, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:26:16'),
	(225, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:26:29'),
	(226, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:26:34'),
	(227, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 3', '127.0.0.1', '2025-07-13 04:26:56'),
	(228, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:26:59'),
	(229, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:27:07'),
	(230, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:27:10'),
	(231, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:27:19'),
	(232, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 5', '127.0.0.1', '2025-07-13 04:28:23'),
	(233, 2, '分配角色权限', '角色: 测试角色21, 权限数量: 6', '127.0.0.1', '2025-07-13 04:28:32'),
	(234, 2, '用户登出', NULL, '127.0.0.1', '2025-07-13 04:28:36'),
	(235, 7, '用户登录', NULL, '127.0.0.1', '2025-07-13 04:28:42'),
	(236, 7, '用户登出', NULL, '127.0.0.1', '2025-07-13 06:21:21'),
	(237, 2, '用户登录', NULL, '127.0.0.1', '2025-07-13 06:21:26'),
	(238, 2, '上传课件: 7307c89043e2b6388d5780073390acb9', '课件ID: 3', '127.0.0.1', '2025-07-13 06:21:41'),
	(239, 2, '上传课件: 传智播客前端面试宝典+名企真题(1)', '课件ID: 4', '127.0.0.1', '2025-07-13 06:39:36'),
	(240, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:41:09'),
	(241, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:41:13'),
	(242, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:41:14'),
	(243, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:41:15'),
	(244, 2, '上传课件: 前端面试宝典', '课件ID: 5', '127.0.0.1', '2025-07-13 06:42:38'),
	(245, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:43:06'),
	(246, 2, '预览课件', '课件ID: 5', '127.0.0.1', '2025-07-13 06:43:08'),
	(247, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:43:16'),
	(248, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:43:18'),
	(249, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:43:18'),
	(250, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:43:28'),
	(251, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:44:18'),
	(252, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:44:51'),
	(253, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:45:04'),
	(254, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:46:19'),
	(255, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:46:27'),
	(256, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:46:37'),
	(257, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:46:38'),
	(258, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:47:00'),
	(259, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:47:46'),
	(260, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:48:38'),
	(261, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:49:01'),
	(262, 2, '预览课件', '课件ID: 5', '127.0.0.1', '2025-07-13 06:50:48'),
	(263, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:50:54'),
	(264, 2, '预览课件', '课件ID: 5', '127.0.0.1', '2025-07-13 06:55:37'),
	(265, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:55:43'),
	(266, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:56:20'),
	(267, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:57:33'),
	(268, 2, '预览课件', '课件ID: 5', '127.0.0.1', '2025-07-13 06:57:44'),
	(269, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:57:48'),
	(270, 2, '预览课件', '课件ID: 5', '127.0.0.1', '2025-07-13 06:58:07'),
	(271, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 06:58:10'),
	(272, 2, '下载课件', '课件ID: 3', '127.0.0.1', '2025-07-13 06:58:49'),
	(273, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 07:00:16'),
	(274, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 07:00:19'),
	(275, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 07:00:53'),
	(276, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 07:01:24'),
	(277, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 07:28:07'),
	(278, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 07:29:14'),
	(279, 2, '预览课件', '课件ID: 4', '127.0.0.1', '2025-07-13 07:42:31'),
	(280, 2, '预览课件', '课件ID: 3', '127.0.0.1', '2025-07-13 07:42:36'),
	(281, 2, '上传课件: 8e28f16bb9be6959713909f25b9c76bb', '课件ID: 6', '127.0.0.1', '2025-07-13 07:43:17'),
	(282, 2, '预览课件', '课件ID: 6', '127.0.0.1', '2025-07-13 07:43:20'),
	(283, 2, '上传课件: 8e28f16bb9be6959713909f25b9c76bb', '课件ID: 7', '127.0.0.1', '2025-07-13 09:37:37'),
	(284, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 09:37:40'),
	(285, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 09:50:52'),
	(286, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 09:51:17'),
	(287, 2, '上传课件: 传智播客前端面试宝典+名企真题(1)', '课件ID: 8', '127.0.0.1', '2025-07-13 09:51:27'),
	(288, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 09:51:31'),
	(289, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 09:57:27'),
	(290, 2, '更新教育培训设置: 设备123', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-13 09:57:45'),
	(291, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:00:07'),
	(292, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 10:00:10'),
	(293, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 10:01:18'),
	(294, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 10:01:32'),
	(295, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:02:20'),
	(296, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:02:45'),
	(297, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:05:23'),
	(298, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:06:11'),
	(299, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 10:07:08'),
	(300, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:07:35'),
	(301, 2, '预览课件', '课件ID: 8', '127.0.0.1', '2025-07-13 10:12:29'),
	(302, 2, '预览课件', '课件ID: 7', '127.0.0.1', '2025-07-13 10:12:37'),
	(303, 2, '设备控制: start', '设备ID: WEB-CLIENT', '127.0.0.1', '2025-07-13 10:17:05'),
	(304, 2, '设备控制: start', '设备ID: 1234', '127.0.0.1', '2025-07-13 10:17:05'),
	(305, 2, '设备控制: start', '设备ID: 7121312', '127.0.0.1', '2025-07-13 10:17:05'),
	(306, 2, '设备控制: start', '设备ID: 123', '127.0.0.1', '2025-07-13 10:17:05'),
	(307, 2, '设备控制: start', '设备ID: G1-EDU-TEST-001', '127.0.0.1', '2025-07-13 10:17:05'),
	(308, 2, '设备控制: start', '设备ID: test', '127.0.0.1', '2025-07-13 10:17:05'),
	(309, 2, '设备控制: start', '设备ID: test123', '127.0.0.1', '2025-07-13 10:17:05'),
	(310, 2, '设备控制: start', '设备ID: test1234531', '127.0.0.1', '2025-07-13 10:17:05'),
	(311, 2, '删除设备', '设备ID: 123', '127.0.0.1', '2025-07-13 10:17:32'),
	(312, 2, '设备控制: stop', '设备ID: 1234', '127.0.0.1', '2025-07-13 10:17:36'),
	(313, 2, '设备控制: stop', '设备ID: 7121312', '127.0.0.1', '2025-07-13 10:17:39'),
	(314, 2, '设备控制: stop', '设备ID: test', '127.0.0.1', '2025-07-13 10:17:42'),
	(315, 2, '设备控制: stop', '设备ID: test123', '127.0.0.1', '2025-07-13 10:17:46'),
	(316, 2, '设备控制: stop', '设备ID: test1234531', '127.0.0.1', '2025-07-13 10:17:51'),
	(317, 2, '删除设备', '设备ID: test1234531', '127.0.0.1', '2025-07-13 10:17:55'),
	(318, 2, '删除设备', '设备ID: test123', '127.0.0.1', '2025-07-13 10:17:58'),
	(319, 2, '删除设备', '设备ID: test', '127.0.0.1', '2025-07-13 10:18:02'),
	(320, 2, '删除设备', '设备ID: 1234', '127.0.0.1', '2025-07-13 10:18:06'),
	(321, 2, '导出设备列表', '导出了 3 条设备记录', '127.0.0.1', '2025-07-13 12:06:59'),
	(322, 2, '导出设备列表', '导出了 3 条设备记录', '127.0.0.1', '2025-07-13 12:08:41'),
	(323, 2, '更新角色', '角色名称: 测试角色21, 角色编码: a_2', '127.0.0.1', '2025-07-13 12:48:36'),
	(324, 2, '创建教育培训设置: 设备7121312', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-13 12:54:38'),
	(325, 2, '更新教育培训设置: 设备7121312', '设置项: AI平台=xunfei, 学科=chinese, 语音=male', '127.0.0.1', '2025-07-13 12:54:50'),
	(326, 2, '用户登录', NULL, '127.0.0.1', '2025-07-14 06:33:59'),
	(327, 2, '上传课件: 7307c89043e2b6388d5780073390acb9', '课件ID: 9', '127.0.0.1', '2025-07-14 07:47:27'),
	(328, 2, '预览课件', '课件ID: 9', '127.0.0.1', '2025-07-14 07:47:30'),
	(329, 2, '用户登录', NULL, '127.0.0.1', '2025-07-14 17:12:03'),
	(330, 2, '用户登录', NULL, '127.0.0.1', '2025-07-14 17:27:47'),
	(331, 2, '用户登录', NULL, '127.0.0.1', '2025-07-16 17:01:38'),
	(332, 2, '用户登录', NULL, '127.0.0.1', '2025-07-16 17:01:54'),
	(333, 2, '设备控制: start', '设备ID: 7121312', '127.0.0.1', '2025-07-16 17:02:14'),
	(334, 2, '用户登出', NULL, '127.0.0.1', '2025-07-16 17:03:06'),
	(335, 2, '用户登录', NULL, '127.0.0.1', '2025-07-16 17:03:14'),
	(336, 2, '用户登录', NULL, '127.0.0.1', '2025-07-16 17:10:36');

-- 导出  表 g1_edu.permissions 结构
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE IF NOT EXISTS `permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `name` varchar(100) NOT NULL COMMENT '权限名称',
  `code` varchar(100) NOT NULL COMMENT '权限编码',
  `description` text COMMENT '权限描述',
  `module` varchar(50) DEFAULT NULL COMMENT '所属模块',
  `permission_type` enum('menu','button','api') DEFAULT NULL COMMENT '权限类型',
  `resource_path` varchar(200) DEFAULT NULL COMMENT '资源路径',
  `method` varchar(10) DEFAULT NULL COMMENT '请求方法',
  `is_system` tinyint(1) DEFAULT NULL COMMENT '是否为系统内置权限',
  `status` tinyint(1) DEFAULT NULL COMMENT '状态',
  `sort_order` int DEFAULT NULL COMMENT '排序',
  `created_by` int DEFAULT NULL COMMENT '创建人',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.permissions 的数据：~44 rows (大约)
DELETE FROM `permissions`;
INSERT INTO `permissions` (`id`, `name`, `code`, `description`, `module`, `permission_type`, `resource_path`, `method`, `is_system`, `status`, `sort_order`, `created_by`, `created_at`, `updated_at`) VALUES
	(1, '用户查看', 'user:list', NULL, '用户管理', 'api', '/api/users', 'GET', 1, 1, 0, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(2, '用户详情', 'user:detail', NULL, '用户管理', 'api', '/api/users/*', 'GET', 1, 1, 1, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(3, '用户创建', 'user:create', NULL, '用户管理', 'api', '/api/users', 'POST', 1, 1, 2, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(4, '用户编辑', 'user:update', NULL, '用户管理', 'api', '/api/users/*', 'PUT', 1, 1, 3, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(5, '用户删除', 'user:delete', NULL, '用户管理', 'api', '/api/users/*', 'DELETE', 1, 1, 4, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(6, '重置密码', 'user:reset_password', NULL, '用户管理', 'button', NULL, NULL, 1, 1, 5, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(7, '设备查看', 'equipment:list', NULL, '设备管理', 'api', '/api/equipment', 'GET', 1, 1, 6, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(8, '设备详情', 'equipment:detail', NULL, '设备管理', 'api', '/api/equipment/*', 'GET', 1, 1, 7, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(9, '设备创建', 'equipment:create', NULL, '设备管理', 'api', '/api/equipment', 'POST', 1, 1, 8, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(10, '设备编辑', 'equipment:update', NULL, '设备管理', 'api', '/api/equipment/*', 'PUT', 1, 1, 9, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(11, '设备删除', 'equipment:delete', NULL, '设备管理', 'api', '/api/equipment/*', 'DELETE', 1, 1, 10, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(12, '设备控制', 'equipment:control', NULL, '设备管理', 'button', NULL, NULL, 1, 1, 11, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(13, '课件查看', 'courseware:list', NULL, '课件管理', 'api', '/api/courseware', 'GET', 1, 1, 12, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(14, '课件详情', 'courseware:detail', NULL, '课件管理', 'api', '/api/courseware/*', 'GET', 1, 1, 13, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(15, '课件上传', 'courseware:upload', NULL, '课件管理', 'api', '/api/courseware/upload', 'POST', 1, 1, 14, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(16, '课件编辑', 'courseware:update', NULL, '课件管理', 'api', '/api/courseware/*', 'PUT', 1, 1, 15, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(17, '课件删除', 'courseware:delete', NULL, '课件管理', 'api', '/api/courseware/*', 'DELETE', 1, 1, 16, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(18, '导航查看', 'navigation:list', NULL, '导航管理', 'api', '/api/navigation', 'GET', 1, 1, 17, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(19, '导航设置', 'navigation:update', NULL, '导航管理', 'api', '/api/navigation/*', 'PUT', 1, 1, 18, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(20, '系统看板', 'dashboard:view', NULL, '系统管理', 'menu', '/dashboard', NULL, 1, 1, 19, NULL, '2025-07-13 03:11:52', '2025-07-13 03:11:52'),
	(21, '系统设置', 'system:settings', NULL, '系统管理', 'api', '/api/system/*', 'GET', 1, 1, 20, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(22, '系统配置', 'system:config', NULL, '系统管理', 'api', '/api/system/*', 'PUT', 1, 1, 21, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(23, '日志查看', 'log:list', NULL, '日志管理', 'api', '/api/logs', 'GET', 1, 1, 22, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(24, '日志详情', 'log:detail', NULL, '日志管理', 'api', '/api/logs/*', 'GET', 1, 1, 23, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(25, '角色查看', 'role:list', NULL, '角色管理', 'api', '/api/roles', 'GET', 1, 1, 24, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(26, '角色详情', 'role:detail', NULL, '角色管理', 'api', '/api/roles/*', 'GET', 1, 1, 25, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(27, '角色创建', 'role:create', NULL, '角色管理', 'api', '/api/roles', 'POST', 1, 1, 26, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(28, '角色编辑', 'role:update', NULL, '角色管理', 'api', '/api/roles/*', 'PUT', 1, 1, 27, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(29, '角色删除', 'role:delete', NULL, '角色管理', 'api', '/api/roles/*', 'DELETE', 1, 1, 28, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(30, '角色权限分配', 'role:permission', NULL, '角色管理', 'button', NULL, NULL, 1, 1, 29, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(31, '角色批量操作', 'role:batch', NULL, '角色管理', 'button', NULL, NULL, 1, 1, 30, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(32, '权限查看', 'permission:list', NULL, '权限管理', 'api', '/api/permissions', 'GET', 1, 1, 31, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(33, '权限详情', 'permission:detail', NULL, '权限管理', 'api', '/api/permissions/*', 'GET', 1, 1, 32, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(34, '权限创建', 'permission:create', NULL, '权限管理', 'api', '/api/permissions', 'POST', 1, 1, 33, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(35, '权限编辑', 'permission:update', NULL, '权限管理', 'api', '/api/permissions/*', 'PUT', 1, 1, 34, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(36, '权限删除', 'permission:delete', NULL, '权限管理', 'api', '/api/permissions/*', 'DELETE', 1, 1, 35, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(37, '权限批量操作', 'permission:batch', NULL, '权限管理', 'button', NULL, NULL, 1, 1, 36, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(38, '菜单查看', 'menu:list', NULL, '菜单管理', 'api', '/api/menus', 'GET', 1, 1, 37, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(39, '菜单详情', 'menu:detail', NULL, '菜单管理', 'api', '/api/menus/*', 'GET', 1, 1, 38, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(40, '菜单创建', 'menu:create', NULL, '菜单管理', 'api', '/api/menus', 'POST', 1, 1, 39, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(41, '菜单编辑', 'menu:update', NULL, '菜单管理', 'api', '/api/menus/*', 'PUT', 1, 1, 40, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(42, '菜单删除', 'menu:delete', NULL, '菜单管理', 'api', '/api/menus/*', 'DELETE', 1, 1, 41, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(43, '菜单批量操作', 'menu:batch', NULL, '菜单管理', 'button', NULL, NULL, 1, 1, 42, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(44, '教育内容查看', 'education:view', NULL, '教育模块', 'menu', '/education', NULL, 1, 1, 43, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53');

-- 导出  表 g1_edu.prompt_templates 结构
DROP TABLE IF EXISTS `prompt_templates`;
CREATE TABLE IF NOT EXISTS `prompt_templates` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '模板ID',
  `title` varchar(255) NOT NULL COMMENT '标题',
  `content` text NOT NULL COMMENT '模板内容',
  `description` text COMMENT '描述',
  `category` varchar(100) DEFAULT NULL COMMENT '分类',
  `tags` varchar(500) DEFAULT NULL COMMENT '标签，逗号分隔',
  `type` enum('system','user','assistant','general') DEFAULT NULL COMMENT '模板类型',
  `status` enum('draft','published','archived') DEFAULT NULL COMMENT '状态',
  `priority` int DEFAULT NULL COMMENT '优先级',
  `view_count` int DEFAULT NULL COMMENT '查看次数',
  `usage_count` int DEFAULT NULL COMMENT '使用次数',
  `is_public` tinyint(1) DEFAULT NULL COMMENT '是否公开',
  `variables` text COMMENT '变量定义JSON',
  `example_input` text COMMENT '示例输入',
  `example_output` text COMMENT '示例输出',
  `model_type` varchar(50) DEFAULT NULL COMMENT '适用模型类型',
  `temperature` float DEFAULT NULL COMMENT '温度参数',
  `max_tokens` int DEFAULT NULL COMMENT '最大token数',
  `created_by` int DEFAULT NULL COMMENT '创建用户ID',
  `updated_by` int DEFAULT NULL COMMENT '更新用户ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `prompt_templates_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `prompt_templates_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.prompt_templates 的数据：~0 rows (大约)
DELETE FROM `prompt_templates`;
INSERT INTO `prompt_templates` (`id`, `title`, `content`, `description`, `category`, `tags`, `type`, `status`, `priority`, `view_count`, `usage_count`, `is_public`, `variables`, `example_input`, `example_output`, `model_type`, `temperature`, `max_tokens`, `created_by`, `updated_by`, `created_at`, `updated_at`) VALUES
	(1, 'test', '12212121', '12121', '', NULL, 'general', 'published', 0, 0, 0, 1, '', '', '', '', 0.7, NULL, 2, 2, '2025-07-14 17:29:26', '2025-07-14 17:29:26');

-- 导出  表 g1_edu.roles 结构
DROP TABLE IF EXISTS `roles`;
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `name` varchar(50) NOT NULL COMMENT '角色名称',
  `code` varchar(50) NOT NULL COMMENT '角色编码',
  `description` text COMMENT '角色描述',
  `is_system` tinyint(1) DEFAULT NULL COMMENT '是否为系统内置角色',
  `status` tinyint(1) DEFAULT NULL COMMENT '状态',
  `sort_order` int DEFAULT NULL COMMENT '排序',
  `created_by` int DEFAULT NULL COMMENT '创建人',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `roles_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.roles 的数据：~0 rows (大约)
DELETE FROM `roles`;
INSERT INTO `roles` (`id`, `name`, `code`, `description`, `is_system`, `status`, `sort_order`, `created_by`, `created_at`, `updated_at`) VALUES
	(1, '系统管理员', 'admin', '拥有系统所有权限', 1, 1, 0, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(2, '操作员', 'operator', '可操作设备和管理课件', 1, 1, 0, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(3, '查看者', 'viewer', '只能查看相关信息', 1, 1, 0, NULL, '2025-07-13 03:11:53', '2025-07-13 03:11:53'),
	(4, '测试角色名称', 'a_1', '测试角色', 0, 1, 0, 2, '2025-07-13 03:24:44', '2025-07-13 04:06:32'),
	(5, '测试角色21', 'a_2', 'ceshi', 0, 0, 0, 2, '2025-07-13 04:10:19', '2025-07-13 12:48:36');

-- 导出  表 g1_edu.role_permissions 结构
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE IF NOT EXISTS `role_permissions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  `permission_id` int NOT NULL COMMENT '权限ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_permission` (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.role_permissions 的数据：~72 rows (大约)
DELETE FROM `role_permissions`;
INSERT INTO `role_permissions` (`id`, `role_id`, `permission_id`, `created_at`) VALUES
	(1, 1, 1, '2025-07-13 03:11:53'),
	(2, 1, 2, '2025-07-13 03:11:53'),
	(3, 1, 3, '2025-07-13 03:11:53'),
	(4, 1, 4, '2025-07-13 03:11:53'),
	(5, 1, 5, '2025-07-13 03:11:53'),
	(6, 1, 6, '2025-07-13 03:11:53'),
	(7, 1, 7, '2025-07-13 03:11:53'),
	(8, 1, 8, '2025-07-13 03:11:53'),
	(9, 1, 9, '2025-07-13 03:11:53'),
	(10, 1, 10, '2025-07-13 03:11:53'),
	(11, 1, 11, '2025-07-13 03:11:53'),
	(12, 1, 12, '2025-07-13 03:11:53'),
	(13, 1, 13, '2025-07-13 03:11:53'),
	(14, 1, 14, '2025-07-13 03:11:53'),
	(15, 1, 15, '2025-07-13 03:11:53'),
	(16, 1, 16, '2025-07-13 03:11:53'),
	(17, 1, 17, '2025-07-13 03:11:53'),
	(18, 1, 18, '2025-07-13 03:11:53'),
	(19, 1, 19, '2025-07-13 03:11:53'),
	(20, 1, 20, '2025-07-13 03:11:53'),
	(21, 1, 21, '2025-07-13 03:11:53'),
	(22, 1, 22, '2025-07-13 03:11:53'),
	(23, 1, 23, '2025-07-13 03:11:53'),
	(24, 1, 24, '2025-07-13 03:11:53'),
	(25, 1, 25, '2025-07-13 03:11:53'),
	(26, 1, 26, '2025-07-13 03:11:53'),
	(27, 1, 27, '2025-07-13 03:11:53'),
	(28, 1, 28, '2025-07-13 03:11:53'),
	(29, 1, 29, '2025-07-13 03:11:53'),
	(30, 1, 30, '2025-07-13 03:11:53'),
	(31, 1, 31, '2025-07-13 03:11:53'),
	(32, 1, 32, '2025-07-13 03:11:53'),
	(33, 1, 33, '2025-07-13 03:11:53'),
	(34, 1, 34, '2025-07-13 03:11:53'),
	(35, 1, 35, '2025-07-13 03:11:53'),
	(36, 1, 36, '2025-07-13 03:11:53'),
	(37, 1, 37, '2025-07-13 03:11:53'),
	(38, 1, 38, '2025-07-13 03:11:53'),
	(39, 1, 39, '2025-07-13 03:11:53'),
	(40, 1, 40, '2025-07-13 03:11:53'),
	(41, 1, 41, '2025-07-13 03:11:53'),
	(42, 1, 42, '2025-07-13 03:11:53'),
	(43, 1, 43, '2025-07-13 03:11:53'),
	(44, 1, 44, '2025-07-13 03:11:53'),
	(45, 2, 7, '2025-07-13 03:11:53'),
	(46, 2, 8, '2025-07-13 03:11:53'),
	(47, 2, 12, '2025-07-13 03:11:53'),
	(48, 2, 13, '2025-07-13 03:11:53'),
	(49, 2, 14, '2025-07-13 03:11:53'),
	(50, 2, 15, '2025-07-13 03:11:53'),
	(51, 2, 16, '2025-07-13 03:11:53'),
	(52, 2, 17, '2025-07-13 03:11:53'),
	(53, 2, 18, '2025-07-13 03:11:53'),
	(54, 2, 19, '2025-07-13 03:11:53'),
	(55, 2, 44, '2025-07-13 03:11:53'),
	(56, 2, 23, '2025-07-13 03:11:53'),
	(57, 2, 24, '2025-07-13 03:11:53'),
	(58, 3, 7, '2025-07-13 03:11:53'),
	(59, 3, 8, '2025-07-13 03:11:53'),
	(60, 3, 13, '2025-07-13 03:11:53'),
	(61, 3, 14, '2025-07-13 03:11:53'),
	(62, 3, 18, '2025-07-13 03:11:53'),
	(63, 3, 44, '2025-07-13 03:11:53'),
	(64, 3, 23, '2025-07-13 03:11:53'),
	(65, 4, 20, '2025-07-13 04:08:07'),
	(66, 4, 44, '2025-07-13 04:08:07'),
	(127, 5, 7, '2025-07-13 04:28:32'),
	(128, 5, 8, '2025-07-13 04:28:32'),
	(129, 5, 18, '2025-07-13 04:28:32'),
	(130, 5, 19, '2025-07-13 04:28:32'),
	(131, 5, 38, '2025-07-13 04:28:32'),
	(132, 5, 12, '2025-07-13 04:28:32');

-- 导出  表 g1_edu.system_settings 结构
DROP TABLE IF EXISTS `system_settings`;
CREATE TABLE IF NOT EXISTS `system_settings` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '设置ID',
  `category` varchar(50) NOT NULL COMMENT '设置分类',
  `setting_key` varchar(100) NOT NULL COMMENT '设置键名',
  `setting_value` text COMMENT '设置值',
  `value_type` enum('string','integer','float','boolean','json') DEFAULT NULL COMMENT '值类型',
  `description` varchar(255) DEFAULT NULL COMMENT '设置描述',
  `is_encrypted` tinyint(1) DEFAULT NULL COMMENT '是否加密存储',
  `is_system` tinyint(1) DEFAULT NULL COMMENT '是否系统设置(不可删除)',
  `updated_by` int DEFAULT NULL COMMENT '更新用户ID',
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.system_settings 的数据：~0 rows (大约)
DELETE FROM `system_settings`;

-- 导出  存储过程 g1_edu.UpdateDailyStatistics 结构
DROP PROCEDURE IF EXISTS `UpdateDailyStatistics`;
DELIMITER //
CREATE PROCEDURE `UpdateDailyStatistics`()
BEGIN
    DECLARE today DATE DEFAULT CURDATE();
    
    INSERT INTO `dashboard_statistics` (
        `statistic_date`,
        `total_devices`,
        `online_devices`,
        `offline_devices`,
        `error_devices`,
        `total_users`,
        `active_users`,
        `total_courseware`
    ) VALUES (
        today,
        (SELECT COUNT(*) FROM `equipment`),
        (SELECT COUNT(*) FROM `equipment` WHERE `is_offline` = 0),
        (SELECT COUNT(*) FROM `equipment` WHERE `is_offline` = 1),
        (SELECT COUNT(*) FROM `equipment` WHERE `has_error` = 1),
        (SELECT COUNT(*) FROM `users` WHERE `status` = 1),
        (SELECT COUNT(DISTINCT user_id) FROM `operation_logs` WHERE DATE(created_at) = today),
        (SELECT COUNT(*) FROM `courseware` WHERE `status` = 'published')
    ) ON DUPLICATE KEY UPDATE
        `total_devices` = VALUES(`total_devices`),
        `online_devices` = VALUES(`online_devices`),
        `offline_devices` = VALUES(`offline_devices`),
        `error_devices` = VALUES(`error_devices`),
        `total_users` = VALUES(`total_users`),
        `active_users` = VALUES(`active_users`),
        `total_courseware` = VALUES(`total_courseware`);
END//
DELIMITER ;

-- 导出  表 g1_edu.users 结构
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `username` varchar(50) NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(255) NOT NULL,
  `real_name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role` enum('admin','operator','viewer') NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1',
  `email` varchar(120) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `login_count` int DEFAULT '0',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `role_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.users 的数据：~5 rows (大约)
DELETE FROM `users`;
INSERT INTO `users` (`username`, `id`, `password`, `real_name`, `phone`, `role`, `created_at`, `last_login`, `status`, `email`, `is_active`, `login_count`, `updated_at`, `role_id`) VALUES
	('admin', 2, 'scrypt:32768:8:1$wc3e3aWpkTDm7Sh6$4f68fd15c5e29281a145cd4878ffba50b4b0a443d3993c1eb166987c7e2eeefd720dbf112211654ced4a4f0472b7262d39cf4be812d2618d5c6a1c99c93f4ffe', 'System Admin', '18888888888', 'admin', '2025-07-02 19:55:45', '2025-07-16 17:10:36', 1, 'admin@system.com', NULL, 56, '2025-07-16 17:10:36', 1),
	('user1', 3, 'scrypt:32768:8:1$wc3e3aWpkTDm7Sh6$4f68fd15c5e29281a145cd4878ffba50b4b0a443d3993c1eb166987c7e2eeefd720dbf112211654ced4a4f0472b7262d39cf4be812d2618d5c6a1c99c93f4ffe', '张三', '18888888888', 'operator', '2025-07-04 13:16:42', '2025-07-06 08:38:37', 1, 'user1@example.com', NULL, 3, '2025-07-13 03:13:23', 2),
	('operator', 5, 'scrypt:32768:8:1$KwBaeBk0aVPaFw8o$bc3d415317410bca44c82082d5ca940edea440eead126b85dd39891c6f7d4b55f2100426ff2cbc6af23bb0eff1e28e1585dc631760b93a10b5767a6be3545f42', '系统操作员', '188888888888', 'operator', '2025-07-05 03:33:00', NULL, 1, 'operator@system.com', NULL, 0, '2025-07-13 03:13:23', 2),
	('viewer', 6, 'scrypt:32768:8:1$xoEwpo1k53E3PfyY$2e4b4aa7e3cb599d72e61cedbb2b3a2afd6b424fd0319fe8448fcaf03399516d50e36cc3bacd061e3fff8fe38869c118357929b50ca904ce6733fc70ede7dae8', '系统查看者', '18888888888', 'viewer', '2025-07-05 03:33:00', NULL, 1, 'viewer@system.com', NULL, 0, '2025-07-13 03:13:23', 3),
	('123456', 7, 'pbkdf2:sha256:1000000$fWHTDkB5k0eFcEaM$5e1703d6b82c99d508221cbb4220169912c688dab66c1e037602929e8da411e8', '123456', '1', 'viewer', '2025-07-09 16:33:50', '2025-07-13 04:28:42', 1, '1@qq.com', NULL, 22, '2025-07-13 04:28:42', 5);

-- 导出  表 g1_edu.user_sessions 结构
DROP TABLE IF EXISTS `user_sessions`;
CREATE TABLE IF NOT EXISTS `user_sessions` (
  `id` varchar(128) NOT NULL COMMENT '会话ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `ip_address` varchar(50) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(500) DEFAULT NULL COMMENT '用户代理',
  `login_time` datetime NOT NULL COMMENT '登录时间',
  `last_activity` datetime NOT NULL COMMENT '最后活动时间',
  `expires_at` datetime NOT NULL COMMENT '过期时间',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否活跃',
  `session_data` text COMMENT '会话数据(JSON)',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 正在导出表  g1_edu.user_sessions 的数据：~0 rows (大约)
DELETE FROM `user_sessions`;
INSERT INTO `user_sessions` (`id`, `user_id`, `ip_address`, `user_agent`, `login_time`, `last_activity`, `expires_at`, `is_active`, `session_data`) VALUES
	('02529625-f37f-4285-bbfb-bd55e7868c8d', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-05 04:55:16', '2025-07-05 04:55:16', '2025-07-06 04:55:16', 1, '{}'),
	('03023db3-1a85-491a-a211-c902e74df999', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 13:17:04', '2025-07-04 13:17:04', '2025-07-05 13:17:04', 1, '{}'),
	('048cf973-da6a-4c1f-b77e-aa758be7c6f3', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:07:34', '2025-07-13 04:07:34', '2025-07-14 04:07:34', 1, '{}'),
	('0503b962-980d-4d62-8c14-732473367f95', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:47:55', '2025-07-04 09:47:55', '2025-07-05 09:47:55', 1, '{}'),
	('0b042946-fca8-4b9b-a7c3-d923a91e8e1d', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:08:16', '2025-07-13 04:08:16', '2025-07-14 04:08:16', 1, '{}'),
	('0f65889a-ecd5-453e-8d96-84ae76134ab6', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:14:01', '2025-07-11 17:14:01', '2025-07-12 17:14:01', 1, '{}'),
	('0fd0ea64-2231-41e6-aedc-74a20437665d', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:47:37', '2025-07-11 17:47:37', '2025-07-12 17:47:37', 1, '{}'),
	('113e024c-fb3e-4bec-9c7f-5260ed26e2e2', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 13:17:51', '2025-07-04 13:17:51', '2025-07-05 13:17:51', 1, '{}'),
	('14a24771-3fd9-4ed4-b11d-ff549603b72b', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:27:19', '2025-07-13 04:27:19', '2025-07-14 04:27:19', 1, '{}'),
	('14d17657-04fa-4896-a8d1-ef5077ddea3e', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 14:35:21', '2025-07-04 14:35:21', '2025-07-05 14:35:21', 1, '{}'),
	('167bc431-38b3-4303-9ef5-86c2c567f312', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 02:51:39', '2025-07-13 02:51:39', '2025-07-14 02:51:39', 1, '{}'),
	('169d1dc7-af73-468c-bc0d-fdf7972856c2', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:52:46', '2025-07-04 09:52:46', '2025-07-05 09:52:46', 1, '{}'),
	('21f47a14-75ad-4d44-871b-c8390a05811e', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 12:52:38', '2025-07-11 12:52:38', '2025-07-12 12:52:38', 1, '{}'),
	('234204ad-27e2-446a-9650-b8b11b814c32', 2, '127.0.0.1', 'python-requests/2.32.4', '2025-07-04 09:28:30', '2025-07-04 09:28:30', '2025-07-05 09:28:30', 1, '{}'),
	('294aab05-afa9-40fd-b1aa-7b9d4b141ebd', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:20:32', '2025-07-11 17:20:32', '2025-07-12 17:20:32', 1, '{}'),
	('2c18bb50-1724-4a74-8644-914cf00f4a79', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:48:42', '2025-07-04 09:48:42', '2025-07-05 09:48:42', 1, '{}'),
	('3271866d-e526-4608-842f-5cc0db4eb263', 3, '127.0.0.1', 'curl/8.1.2', '2025-07-04 13:17:29', '2025-07-04 13:17:29', '2025-07-05 13:17:29', 1, '{}'),
	('342798f4-7726-42ae-ba9c-34fd01ac5b3d', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:21:30', '2025-07-13 04:21:30', '2025-07-14 04:21:30', 1, '{}'),
	('34a25ce7-0def-4c62-a172-e5d60dd15e91', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 12:52:51', '2025-07-11 12:52:51', '2025-07-12 12:52:51', 1, '{}'),
	('35834318-6df3-413a-9753-47f3982ac3e9', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-14 17:27:47', '2025-07-14 17:27:47', '2025-07-15 17:27:47', 1, '{}'),
	('3ae8b49b-3acc-4e04-9d79-e6ceb863b295', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:53:29', '2025-07-04 09:53:29', '2025-07-05 09:53:29', 1, '{}'),
	('445d5c8e-c099-4a2a-a28b-cfb97fcfd7e4', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 16:40:28', '2025-07-11 16:40:28', '2025-07-12 16:40:28', 1, '{}'),
	('499a6157-b241-4eaf-9ae2-0b4ef239311c', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 06:20:55', '2025-07-11 06:20:55', '2025-07-12 06:20:55', 1, '{}'),
	('49b5cd8b-c95b-429c-889e-be801178b426', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:26:16', '2025-07-13 04:26:16', '2025-07-14 04:26:16', 1, '{}'),
	('4d09185c-7b93-43c2-83c8-dfb74bfbb861', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 14:19:36', '2025-07-04 14:19:36', '2025-07-05 14:19:36', 1, '{}'),
	('4ead27af-225c-4471-9b15-881c93a2ce4e', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 10:03:09', '2025-07-04 10:03:09', '2025-07-05 10:03:09', 1, '{}'),
	('4f29be6e-1314-4ba8-adf3-0e2fcb93d8e9', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:19:01', '2025-07-11 17:19:01', '2025-07-12 17:19:01', 1, '{}'),
	('4f52fa91-30fc-4368-b8b0-f1a799cb4065', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:34:32', '2025-07-04 09:34:32', '2025-07-05 09:34:32', 1, '{}'),
	('4f55677e-f31f-4f31-9f91-eae8b866a8de', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:16:39', '2025-07-11 17:16:39', '2025-07-12 17:16:39', 1, '{}'),
	('504b001d-c0fd-414f-9bc6-c7a5e137062e', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 13:50:27', '2025-07-04 13:50:27', '2025-07-05 13:50:27', 1, '{}'),
	('51852225-5d9c-4535-96ce-7b9cc124473d', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:28:42', '2025-07-13 04:28:42', '2025-07-14 04:28:42', 1, '{}'),
	('5609c21e-547c-41c9-b3a5-706b525d185b', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:07:13', '2025-07-13 04:07:13', '2025-07-14 04:07:13', 1, '{}'),
	('5a06c3ec-7c44-478b-beea-36731a87d5fa', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-10 02:32:58', '2025-07-10 02:32:58', '2025-07-11 02:32:58', 1, '{}'),
	('5f4cc91f-0a29-4db0-8c66-76f5ade5ca6b', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-05 03:34:52', '2025-07-05 03:34:52', '2025-07-06 03:34:52', 1, '{}'),
	('5f79155a-cd5c-40f0-afb3-345cac65398a', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0', '2025-07-16 17:01:38', '2025-07-16 17:01:38', '2025-07-17 17:01:38', 1, '{}'),
	('60ebde1b-3031-4d82-a3d8-4512320e5021', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:21:41', '2025-07-13 04:21:41', '2025-07-14 04:21:41', 1, '{}'),
	('645c7176-8946-4321-b6b2-bd6ceeeb4821', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:20:42', '2025-07-13 04:20:42', '2025-07-14 04:20:42', 1, '{}'),
	('6963fcf1-fefc-4d1a-bca7-cb5617d419af', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:24:14', '2025-07-04 09:24:14', '2025-07-05 09:24:14', 1, '{}'),
	('69644049-99d3-41d1-911d-4d623c768284', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:22:34', '2025-07-13 04:22:34', '2025-07-14 04:22:34', 1, '{}'),
	('6d6756a4-6d65-4582-a576-dc5d72b3aa66', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 02:46:36', '2025-07-13 02:46:36', '2025-07-14 02:46:36', 1, '{}'),
	('6f1bf98e-bbce-429d-9876-867a87ddd273', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 13:02:20', '2025-07-11 13:02:20', '2025-07-12 13:02:20', 1, '{}'),
	('6fe19bd1-7e16-4ce3-8200-1168fa44f459', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:30:35', '2025-07-04 09:30:35', '2025-07-05 09:30:35', 1, '{}'),
	('7179f40b-1ad1-496b-a431-18bf76cce5c9', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:30:24', '2025-07-04 09:30:24', '2025-07-05 09:30:24', 1, '{}'),
	('85471311-8c87-47ff-8341-a51d48837c2b', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 02:39:45', '2025-07-13 02:39:45', '2025-07-14 02:39:45', 1, '{}'),
	('8c75170b-9654-4c45-bc19-f4e24525307f', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:52:58', '2025-07-04 09:52:58', '2025-07-05 09:52:58', 1, '{}'),
	('8e8e315e-134b-4455-b67b-ac63f1f7072b', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-06 08:38:03', '2025-07-06 08:38:03', '2025-07-07 08:38:03', 1, '{}'),
	('95b5cf5d-40e0-445e-b40a-a7de22722a8b', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:23:19', '2025-07-13 04:23:19', '2025-07-14 04:23:19', 1, '{}'),
	('9a1b0cd2-128d-4b9e-baa8-a80f80e0795e', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:13:10', '2025-07-11 17:13:10', '2025-07-12 17:13:10', 1, '{}'),
	('9a55b5f9-113a-48de-ae73-4344f93e9f90', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 13:11:51', '2025-07-11 13:11:51', '2025-07-12 13:11:51', 1, '{}'),
	('9b91e762-f844-4fa7-a6bc-c33ffe01c9a7', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:20:56', '2025-07-13 04:20:56', '2025-07-14 04:20:56', 1, '{}'),
	('9c937bb2-b51d-4a19-9821-0e76e1438933', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-06 08:39:03', '2025-07-06 08:39:03', '2025-07-07 08:39:03', 1, '{}'),
	('a9b7903c-a915-4031-8fa5-d00816e0fa46', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-06 08:37:43', '2025-07-06 08:37:43', '2025-07-07 08:37:43', 1, '{}'),
	('adfd02ed-97af-43ae-a9c1-608cb94e8069', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 02:39:26', '2025-07-13 02:39:26', '2025-07-14 02:39:26', 1, '{}'),
	('aeefa0d1-83b2-4fb6-8410-9a82a38130b6', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 06:21:26', '2025-07-13 06:21:26', '2025-07-14 06:21:26', 1, '{}'),
	('b9282662-cd2c-4afe-a33d-8f6a0ee4e8e8', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 03:00:42', '2025-07-13 03:00:42', '2025-07-14 03:00:42', 1, '{}'),
	('b9cfa45e-9ae3-4c33-93f0-1add7d91bed7', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:23:03', '2025-07-11 17:23:03', '2025-07-12 17:23:03', 1, '{}'),
	('baea6b3f-ab93-4853-a359-c8d4d119e3bf', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 03:13:39', '2025-07-13 03:13:39', '2025-07-14 03:13:39', 1, '{}'),
	('bb0fcdef-2cda-49fa-a343-1811665842ac', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-14 06:33:59', '2025-07-14 06:33:59', '2025-07-15 06:33:59', 1, '{}'),
	('c0adf27b-5f7c-4ae4-bcdd-3c753da32589', 2, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0', '2025-07-16 17:03:14', '2025-07-16 17:03:14', '2025-07-17 17:03:14', 1, '{}'),
	('c6af426a-b2e9-4cfb-95b3-bafb9c6ba326', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-09 16:33:59', '2025-07-09 16:33:59', '2025-07-10 16:33:59', 1, '{}'),
	('c8f43fff-b118-410c-a006-bb9f8a044007', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-09 16:34:10', '2025-07-09 16:34:10', '2025-07-10 16:34:10', 1, '{}'),
	('c952cb8d-621b-49ef-bc9e-fd45db3d3ddb', 2, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0', '2025-07-16 17:01:54', '2025-07-16 17:01:54', '2025-07-17 17:01:54', 1, '{}'),
	('cc0d6be5-a50d-429a-8e99-8bda53727420', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 12:26:10', '2025-07-11 12:26:10', '2025-07-12 12:26:10', 1, '{}'),
	('d14eb31f-47c2-4f2c-9097-d1fb1c389a07', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 17:23:24', '2025-07-11 17:23:24', '2025-07-12 17:23:24', 1, '{}'),
	('d4940b6b-24d9-4130-8301-19f341196470', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 13:51:00', '2025-07-11 13:51:00', '2025-07-12 13:51:00', 1, '{}'),
	('d65aea06-8a13-4215-9b7b-8767d6d6a0e9', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:53:42', '2025-07-04 09:53:42', '2025-07-05 09:53:42', 1, '{}'),
	('d91f207f-16b4-4bc2-a169-0da73253b61a', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:27:07', '2025-07-13 04:27:07', '2025-07-14 04:27:07', 1, '{}'),
	('de793e8d-856e-44f2-ba0f-c8fd95a105b2', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-11 16:41:41', '2025-07-11 16:41:41', '2025-07-12 16:41:41', 1, '{}'),
	('e330890c-6991-4a9d-960e-543f5439d610', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-14 17:12:03', '2025-07-14 17:12:03', '2025-07-15 17:12:03', 1, '{}'),
	('e5a0dfb9-3c80-494f-89df-577cc200fb30', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-12 07:12:40', '2025-07-12 07:12:40', '2025-07-13 07:12:40', 1, '{}'),
	('e6d77471-5e5b-48ef-9338-9e2db7432f95', 3, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-04 14:20:17', '2025-07-04 14:20:17', '2025-07-05 14:20:17', 1, '{}'),
	('e8e08422-9d0b-4b76-a570-0a865b79e14c', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 02:44:58', '2025-07-13 02:44:58', '2025-07-14 02:44:58', 1, '{}'),
	('e94b96e1-8f8d-44db-8423-5b23bca6798d', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:26:34', '2025-07-13 04:26:34', '2025-07-14 04:26:34', 1, '{}'),
	('ed75c9a2-5129-45de-b5f5-4f72b1534866', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:52:17', '2025-07-04 09:52:17', '2025-07-05 09:52:17', 1, '{}'),
	('ede8ce37-0afe-4e19-b76a-e2f3d1b5d168', 2, '127.0.0.1', 'curl/8.1.2', '2025-07-04 09:51:40', '2025-07-04 09:51:40', '2025-07-05 09:51:40', 1, '{}'),
	('ee1a5890-4be0-4abe-a8e7-8d1ce73a4aa4', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-10 02:10:58', '2025-07-10 02:10:58', '2025-07-11 02:10:58', 1, '{}'),
	('ef83e553-40df-4002-831a-250901a5649e', 3, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-06 08:38:37', '2025-07-06 08:38:37', '2025-07-07 08:38:37', 1, '{}'),
	('f6c430b0-4382-4e01-8355-97facb67975a', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-13 04:09:50', '2025-07-13 04:09:50', '2025-07-14 04:09:50', 1, '{}'),
	('f7069d0e-c48e-4ae3-9897-017409a2df21', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-06 08:42:19', '2025-07-06 08:42:19', '2025-07-07 08:42:19', 1, '{}'),
	('fabd7c37-9a46-4a78-9117-ee28d2c5561a', 2, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', '2025-07-16 17:10:36', '2025-07-16 17:10:36', '2025-07-17 17:10:36', 1, '{}'),
	('fb7c58d0-7b33-4a2f-b273-d87dfb96cf3d', 7, '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', '2025-07-10 02:11:56', '2025-07-10 02:11:56', '2025-07-11 02:11:56', 1, '{}');

-- 导出  视图 g1_edu.v_courseware_usage_summary 结构
DROP VIEW IF EXISTS `v_courseware_usage_summary`;
-- 创建临时表以解决视图依赖性错误
CREATE TABLE `v_courseware_usage_summary` (
	`id` INT(10) NOT NULL COMMENT '课件ID',
	`title` VARCHAR(255) NOT NULL COMMENT '课件标题' COLLATE 'utf8mb4_0900_ai_ci',
	`file_type` VARCHAR(50) NOT NULL COMMENT '文件类型' COLLATE 'utf8mb4_0900_ai_ci',
	`subject` VARCHAR(100) NULL COMMENT '学科' COLLATE 'utf8mb4_0900_ai_ci',
	`total_usage` BIGINT(19) NOT NULL,
	`play_count` DECIMAL(23,0) NULL,
	`download_count` DECIMAL(23,0) NULL,
	`avg_duration` DECIMAL(14,4) NULL
) ENGINE=MyISAM;

-- 导出  视图 g1_edu.v_equipment_status_summary 结构
DROP VIEW IF EXISTS `v_equipment_status_summary`;
-- 创建临时表以解决视图依赖性错误
CREATE TABLE `v_equipment_status_summary` 
) ENGINE=MyISAM;

-- 导出  视图 g1_edu.v_user_activity_summary 结构
DROP VIEW IF EXISTS `v_user_activity_summary`;
-- 创建临时表以解决视图依赖性错误
CREATE TABLE `v_user_activity_summary` (
	`id` INT(10) NOT NULL,
	`username` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`real_name` VARCHAR(100) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`role` ENUM('admin','operator','viewer') NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`last_login` DATETIME NULL,
	`operation_count` BIGINT(19) NOT NULL,
	`last_operation` DATETIME NULL
) ENGINE=MyISAM;

-- 导出  视图 g1_edu.v_courseware_usage_summary 结构
DROP VIEW IF EXISTS `v_courseware_usage_summary`;
-- 移除临时表并创建最终视图结构
DROP TABLE IF EXISTS `v_courseware_usage_summary`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_courseware_usage_summary` AS select `c`.`id` AS `id`,`c`.`title` AS `title`,`c`.`file_type` AS `file_type`,`c`.`subject` AS `subject`,count(`cu`.`id`) AS `total_usage`,sum((case when (`cu`.`action` = 'play') then 1 else 0 end)) AS `play_count`,sum((case when (`cu`.`action` = 'download') then 1 else 0 end)) AS `download_count`,avg(`cu`.`duration`) AS `avg_duration` from (`courseware` `c` left join `courseware_usage` `cu` on((`c`.`id` = `cu`.`courseware_id`))) where (`c`.`status` = 'published') group by `c`.`id`,`c`.`title`,`c`.`file_type`,`c`.`subject`;

-- 导出  视图 g1_edu.v_equipment_status_summary 结构
DROP VIEW IF EXISTS `v_equipment_status_summary`;
-- 移除临时表并创建最终视图结构
DROP TABLE IF EXISTS `v_equipment_status_summary`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_equipment_status_summary` AS select count(0) AS `total_devices`,sum((case when (`equipment`.`is_offline` = 0) then 1 else 0 end)) AS `online_devices`,sum((case when (`equipment`.`is_offline` = 1) then 1 else 0 end)) AS `offline_devices`,sum((case when (`equipment`.`has_error` = 1) then 1 else 0 end)) AS `error_devices`,avg(`equipment`.`usage_rate`) AS `avg_usage_rate`,avg(`equipment`.`battery_level`) AS `avg_battery_level` from `equipment`;

-- 导出  视图 g1_edu.v_user_activity_summary 结构
DROP VIEW IF EXISTS `v_user_activity_summary`;
-- 移除临时表并创建最终视图结构
DROP TABLE IF EXISTS `v_user_activity_summary`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `v_user_activity_summary` AS select `u`.`id` AS `id`,`u`.`username` AS `username`,`u`.`real_name` AS `real_name`,`u`.`role` AS `role`,`u`.`last_login` AS `last_login`,count(`ol`.`id`) AS `operation_count`,max(`ol`.`created_at`) AS `last_operation` from (`users` `u` left join `operation_logs` `ol` on((`u`.`id` = `ol`.`user_id`))) where (`u`.`status` = 1) group by `u`.`id`,`u`.`username`,`u`.`real_name`,`u`.`role`,`u`.`last_login`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
