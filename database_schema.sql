-- =========================================================================
-- 宇树G1 EDU机器人管理系统 - 完整数据库结构设计
-- 版本: 2.0
-- 创建时间: 2025-01-03
-- 基于前端分析和后端模型的完整数据库设计
-- =========================================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `g1_edu_system` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `g1_edu_system`;

-- =========================================================================
-- 核心用户管理表
-- =========================================================================

-- 用户/账号表
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `real_name` VARCHAR(100) NOT NULL COMMENT '真实姓名',
    `email` VARCHAR(100) UNIQUE COMMENT '邮箱地址',
    `phone` VARCHAR(20) COMMENT '手机号码',
    `role` ENUM('admin', 'operator', 'viewer') NOT NULL DEFAULT 'viewer' COMMENT '用户角色',
    `status` TINYINT(1) DEFAULT 1 COMMENT '用户状态: 1-启用, 0-禁用',
    `last_login` DATETIME COMMENT '最后登录时间',
    `login_count` INT DEFAULT 0 COMMENT '登录次数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_username` (`username`),
    INDEX `idx_role` (`role`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户账号表';

-- =========================================================================
-- 设备管理表
-- =========================================================================

-- 设备表
CREATE TABLE `equipment` (
    `id` VARCHAR(50) PRIMARY KEY COMMENT '设备唯一标识，如G1-EDU-001',
    `name` VARCHAR(100) COMMENT '设备名称',
    `location` VARCHAR(255) NOT NULL COMMENT '设备所在位置',
    `status` VARCHAR(50) DEFAULT 'offline' COMMENT '设备当前状态: online, offline, teaching, touring, standby',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `mac_address` VARCHAR(17) COMMENT 'MAC地址',
    `firmware_version` VARCHAR(50) COMMENT '固件版本',
    `last_active` DATETIME COMMENT '最后活跃时间',
    `usage_rate` DECIMAL(5,2) DEFAULT 0.00 COMMENT '使用率百分比',
    `battery_level` INT DEFAULT 100 COMMENT '电池电量百分比',
    `is_offline` TINYINT(1) DEFAULT 1 COMMENT '离线状态: 1-离线, 0-在线',
    `has_error` TINYINT(1) DEFAULT 0 COMMENT '错误状态: 1-有错误, 0-正常',
    `maintenance_mode` TINYINT(1) DEFAULT 0 COMMENT '维护模式: 1-维护中, 0-正常',
    `description` TEXT COMMENT '设备描述',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_location` (`location`),
    INDEX `idx_status` (`status`),
    INDEX `idx_offline` (`is_offline`),
    INDEX `idx_error` (`has_error`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备管理表';

-- 设备状态历史表
CREATE TABLE `equipment_status_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL,
    `previous_status` VARCHAR(50) COMMENT '之前状态',
    `current_status` VARCHAR(50) NOT NULL COMMENT '当前状态',
    `change_reason` VARCHAR(255) COMMENT '状态变更原因',
    `changed_by` INT COMMENT '操作用户ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`changed_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_equipment_status` (`equipment_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备状态历史表';

-- 设备日志表
CREATE TABLE `equipment_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL,
    `log_type` ENUM('error', 'warning', 'info', 'debug') NOT NULL COMMENT '日志类型',
    `message` TEXT COMMENT '日志消息',
    `stack_trace` TEXT COMMENT '错误堆栈信息',
    `module` VARCHAR(100) COMMENT '相关模块',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    INDEX `idx_equipment_logs` (`equipment_id`, `log_type`, `created_at`),
    INDEX `idx_log_type_time` (`log_type`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备诊断日志表';

-- =========================================================================
-- 课件管理表
-- =========================================================================

-- 课件分类表
CREATE TABLE `courseware_categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '分类名称',
    `description` TEXT COMMENT '分类描述',
    `parent_id` INT COMMENT '父分类ID',
    `sort_order` INT DEFAULT 0 COMMENT '排序序号',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`parent_id`) REFERENCES `courseware_categories`(`id`) ON DELETE SET NULL,
    INDEX `idx_parent_sort` (`parent_id`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课件分类表';

-- 课件表
CREATE TABLE `courseware` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL COMMENT '课件标题',
    `category_id` INT COMMENT '分类ID',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    `file_name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_type` VARCHAR(50) NOT NULL COMMENT '文件类型: ppt, pdf, mp4, jpg, png等',
    `file_size` BIGINT NOT NULL COMMENT '文件大小(字节)',
    `mime_type` VARCHAR(100) COMMENT 'MIME类型',
    `description` TEXT COMMENT '课件描述',
    `tags` VARCHAR(500) COMMENT '标签，逗号分隔',
    `subject` VARCHAR(100) COMMENT '学科',
    `grade_level` VARCHAR(50) COMMENT '年级水平',
    `duration` INT COMMENT '播放时长(秒)',
    `thumbnail_path` VARCHAR(500) COMMENT '缩略图路径',
    `download_count` INT DEFAULT 0 COMMENT '下载次数',
    `view_count` INT DEFAULT 0 COMMENT '查看次数',
    `is_public` TINYINT(1) DEFAULT 1 COMMENT '是否公开',
    `status` ENUM('draft', 'published', 'archived') DEFAULT 'published' COMMENT '状态',
    `uploaded_by` INT COMMENT '上传用户ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `courseware_categories`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`uploaded_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_title` (`title`),
    INDEX `idx_category` (`category_id`),
    INDEX `idx_file_type` (`file_type`),
    INDEX `idx_subject` (`subject`),
    INDEX `idx_uploader` (`uploaded_by`),
    INDEX `idx_status_public` (`status`, `is_public`),
    FULLTEXT `idx_search` (`title`, `description`, `tags`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课件资源表';

-- 课件使用记录表
CREATE TABLE `courseware_usage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `courseware_id` INT NOT NULL,
    `equipment_id` VARCHAR(50) NOT NULL,
    `user_id` INT COMMENT '操作用户ID',
    `action` ENUM('play', 'download', 'view', 'share') NOT NULL COMMENT '操作类型',
    `duration` INT COMMENT '使用时长(秒)',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`courseware_id`) REFERENCES `courseware`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_courseware_usage` (`courseware_id`, `created_at`),
    INDEX `idx_equipment_usage` (`equipment_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课件使用记录表';

-- =========================================================================
-- 教育培训配置表
-- =========================================================================

-- 教育设置表
CREATE TABLE `education_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL COMMENT '设备ID',
    `screen_sync_mode` ENUM('auto', 'manual', 'off') DEFAULT 'auto' COMMENT '大屏同步模式',
    `ai_platform` VARCHAR(50) DEFAULT 'xunfei' COMMENT 'AI平台: xunfei, baidu, chatgpt等',
    `ai_model` VARCHAR(100) COMMENT 'AI模型名称',
    `api_key` VARCHAR(255) COMMENT 'API密钥(加密存储)',
    `subject` VARCHAR(50) COMMENT '教学科目',
    `voice_type` VARCHAR(50) DEFAULT 'male' COMMENT '语音类型: male, female, child',
    `voice_speed` DECIMAL(3,1) DEFAULT 1.0 COMMENT '语音速度倍率',
    `voice_volume` INT DEFAULT 80 COMMENT '语音音量(0-100)',
    `robot_action` VARCHAR(50) DEFAULT 'standard' COMMENT '机器人动作模式',
    `hand_recognition` TINYINT(1) DEFAULT 1 COMMENT '举手识别功能',
    `interactive_qa` TINYINT(1) DEFAULT 1 COMMENT '互动问答模式',
    `auto_answer` TINYINT(1) DEFAULT 0 COMMENT '自动回答模式',
    `navigation_mode` VARCHAR(50) DEFAULT 'classroom' COMMENT '导航模式',
    `max_students` INT DEFAULT 30 COMMENT '最大学生数量',
    `session_timeout` INT DEFAULT 3600 COMMENT '会话超时时间(秒)',
    `custom_prompts` JSON COMMENT '自定义提示词',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `updated_by` INT COMMENT '更新用户ID',
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    UNIQUE KEY `uk_equipment` (`equipment_id`),
    INDEX `idx_ai_platform` (`ai_platform`),
    INDEX `idx_subject` (`subject`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教育培训配置表';

-- =========================================================================
-- 导览系统表
-- =========================================================================

-- 导览设置表
CREATE TABLE `navigation_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL COMMENT '设备ID',
    `scene_type` VARCHAR(50) DEFAULT 'scenic' COMMENT '场景类型: scenic, museum, exhibition, company',
    `scene_name` VARCHAR(200) COMMENT '场景名称',
    `ai_platform` VARCHAR(50) DEFAULT 'xunfei' COMMENT 'AI平台',
    `voice_type` VARCHAR(50) DEFAULT 'male' COMMENT '语音类型',
    `scene_prompt` TEXT COMMENT '场景提示词',
    `welcome_message` TEXT COMMENT '欢迎词',
    `object_recognition` TINYINT(1) DEFAULT 1 COMMENT '物品识别功能',
    `recognition_action` VARCHAR(50) DEFAULT 'move' COMMENT '识别后动作',
    `auto_follow` TINYINT(1) DEFAULT 0 COMMENT '自动跟随模式',
    `follow_distance` DECIMAL(4,2) DEFAULT 2.0 COMMENT '跟随距离(米)',
    `patrol_mode` VARCHAR(50) DEFAULT 'standard' COMMENT '巡逻模式',
    `patrol_schedule` JSON COMMENT '巡逻时间表',
    `navigation_mode` VARCHAR(50) DEFAULT 'dynamic' COMMENT '导航模式: static, dynamic, hybrid',
    `emergency_alert` TINYINT(1) DEFAULT 1 COMMENT '紧急报警功能',
    `alert_mode` VARCHAR(50) DEFAULT 'auto' COMMENT '报警模式',
    `robot_speed` INT DEFAULT 50 COMMENT '机器人移动速度(0-100)',
    `max_tourists` INT DEFAULT 10 COMMENT '最大游客数量',
    `tour_duration` INT DEFAULT 1800 COMMENT '导览时长(秒)',
    `rest_points` JSON COMMENT '休息点配置',
    `emergency_contacts` JSON COMMENT '紧急联系人',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `updated_by` INT COMMENT '更新用户ID',
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    UNIQUE KEY `uk_equipment` (`equipment_id`),
    INDEX `idx_scene_type` (`scene_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导览系统配置表';

-- 导览点位表
CREATE TABLE `navigation_points` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL COMMENT '设备ID',
    `name` VARCHAR(100) NOT NULL COMMENT '点位名称',
    `description` TEXT COMMENT '点位描述',
    `point_type` ENUM('waypoint', 'poi', 'rest', 'checkpoint', 'emergency') DEFAULT 'waypoint' COMMENT '点位类型',
    `x_position` DECIMAL(10,6) NOT NULL COMMENT 'X坐标',
    `y_position` DECIMAL(10,6) NOT NULL COMMENT 'Y坐标',
    `z_position` DECIMAL(10,6) DEFAULT 0 COMMENT 'Z坐标',
    `orientation` DECIMAL(5,2) DEFAULT 0 COMMENT '朝向角度(0-360度)',
    `radius` DECIMAL(5,2) DEFAULT 1.0 COMMENT '有效半径(米)',
    `priority` ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium' COMMENT '优先级',
    `duration` INT DEFAULT 60 COMMENT '停留时间(秒)',
    `content` TEXT COMMENT '讲解内容',
    `audio_file` VARCHAR(500) COMMENT '语音文件路径',
    `image_files` JSON COMMENT '图片文件路径数组',
    `video_file` VARCHAR(500) COMMENT '视频文件路径',
    `trigger_type` ENUM('auto', 'manual', 'proximity', 'voice', 'gesture') DEFAULT 'auto' COMMENT '触发方式',
    `trigger_condition` JSON COMMENT '触发条件配置',
    `interaction_enabled` TINYINT(1) DEFAULT 0 COMMENT '允许游客互动',
    `interaction_options` JSON COMMENT '互动选项配置',
    `visit_count` INT DEFAULT 0 COMMENT '访问次数',
    `average_duration` INT DEFAULT 0 COMMENT '平均停留时间',
    `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `sort_order` INT DEFAULT 0 COMMENT '排序序号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    INDEX `idx_equipment_enabled` (`equipment_id`, `enabled`),
    INDEX `idx_position` (`x_position`, `y_position`),
    INDEX `idx_type_priority` (`point_type`, `priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导览点位表';

-- 导览路径表
CREATE TABLE `navigation_routes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `equipment_id` VARCHAR(50) NOT NULL COMMENT '设备ID',
    `name` VARCHAR(100) NOT NULL COMMENT '路径名称',
    `description` TEXT COMMENT '路径描述',
    `route_type` ENUM('standard', 'express', 'detailed', 'custom') DEFAULT 'standard' COMMENT '路径类型',
    `point_sequence` JSON NOT NULL COMMENT '点位序列配置',
    `estimated_duration` INT DEFAULT 1800 COMMENT '预计时长(秒)',
    `difficulty_level` ENUM('easy', 'medium', 'hard') DEFAULT 'easy' COMMENT '难度等级',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT '是否默认路径',
    `usage_count` INT DEFAULT 0 COMMENT '使用次数',
    `average_rating` DECIMAL(3,2) DEFAULT 0 COMMENT '平均评分',
    `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `created_by` INT COMMENT '创建用户ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_equipment_enabled` (`equipment_id`, `enabled`),
    INDEX `idx_type_default` (`route_type`, `is_default`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导览路径表';

-- =========================================================================
-- 系统配置表
-- =========================================================================

-- 系统设置表
CREATE TABLE `system_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category` VARCHAR(50) NOT NULL COMMENT '设置分类: server, notification, security, data',
    `setting_key` VARCHAR(100) NOT NULL COMMENT '设置键名',
    `setting_value` TEXT COMMENT '设置值',
    `value_type` ENUM('string', 'integer', 'float', 'boolean', 'json') DEFAULT 'string' COMMENT '值类型',
    `description` VARCHAR(255) COMMENT '设置描述',
    `is_encrypted` TINYINT(1) DEFAULT 0 COMMENT '是否加密存储',
    `is_system` TINYINT(1) DEFAULT 0 COMMENT '是否系统设置(不可删除)',
    `updated_by` INT COMMENT '更新用户ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    UNIQUE KEY `uk_category_key` (`category`, `setting_key`),
    INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统设置表';

-- 通知配置表
CREATE TABLE `notification_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT COMMENT '用户ID，NULL表示全局设置',
    `notification_type` VARCHAR(50) NOT NULL COMMENT '通知类型',
    `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `methods` JSON COMMENT '通知方式: email, sms, push',
    `conditions` JSON COMMENT '触发条件',
    `template_id` INT COMMENT '消息模板ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_type` (`user_id`, `notification_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知配置表';

-- =========================================================================
-- 统计与日志表
-- =========================================================================

-- 系统看板统计表
CREATE TABLE `dashboard_statistics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `statistic_date` DATE NOT NULL COMMENT '统计日期',
    `total_devices` INT DEFAULT 0 COMMENT '设备总数',
    `online_devices` INT DEFAULT 0 COMMENT '在线设备数',
    `offline_devices` INT DEFAULT 0 COMMENT '离线设备数',
    `error_devices` INT DEFAULT 0 COMMENT '故障设备数',
    `total_courses_delivered` INT DEFAULT 0 COMMENT '课程交付总数',
    `total_tours_conducted` INT DEFAULT 0 COMMENT '导览执行总数',
    `total_interactions` INT DEFAULT 0 COMMENT '互动总数',
    `total_users` INT DEFAULT 0 COMMENT '用户总数',
    `active_users` INT DEFAULT 0 COMMENT '活跃用户数',
    `total_courseware` INT DEFAULT 0 COMMENT '课件总数',
    `storage_used` BIGINT DEFAULT 0 COMMENT '存储使用量(字节)',
    `avg_response_time` DECIMAL(8,3) DEFAULT 0 COMMENT '平均响应时间(秒)',
    `system_uptime` INT DEFAULT 0 COMMENT '系统运行时间(秒)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_date` (`statistic_date`),
    INDEX `idx_date_desc` (`statistic_date` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统看板统计表';

-- 操作日志表
CREATE TABLE `operation_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT COMMENT '操作用户ID',
    `username` VARCHAR(50) COMMENT '用户名快照',
    `action` VARCHAR(255) NOT NULL COMMENT '操作动作',
    `resource_type` VARCHAR(50) COMMENT '资源类型: user, equipment, courseware等',
    `resource_id` VARCHAR(100) COMMENT '资源ID',
    `details` JSON COMMENT '操作详情',
    `result` ENUM('success', 'failed', 'partial') DEFAULT 'success' COMMENT '操作结果',
    `error_message` TEXT COMMENT '错误信息',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `user_agent` VARCHAR(500) COMMENT '用户代理',
    `session_id` VARCHAR(100) COMMENT '会话ID',
    `duration` INT COMMENT '操作耗时(毫秒)',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_user_time` (`user_id`, `created_at`),
    INDEX `idx_action_time` (`action`, `created_at`),
    INDEX `idx_resource` (`resource_type`, `resource_id`),
    INDEX `idx_result_time` (`result`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 系统事件表
CREATE TABLE `system_events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(50) NOT NULL COMMENT '事件类型',
    `event_level` ENUM('info', 'warning', 'error', 'critical') DEFAULT 'info' COMMENT '事件级别',
    `title` VARCHAR(200) NOT NULL COMMENT '事件标题',
    `message` TEXT COMMENT '事件消息',
    `source` VARCHAR(100) COMMENT '事件源',
    `equipment_id` VARCHAR(50) COMMENT '相关设备ID',
    `user_id` INT COMMENT '相关用户ID',
    `metadata` JSON COMMENT '事件元数据',
    `is_read` TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    `is_resolved` TINYINT(1) DEFAULT 0 COMMENT '是否已解决',
    `resolved_by` INT COMMENT '解决用户ID',
    `resolved_at` DATETIME COMMENT '解决时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`resolved_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_type_level` (`event_type`, `event_level`),
    INDEX `idx_equipment_time` (`equipment_id`, `created_at`),
    INDEX `idx_read_resolved` (`is_read`, `is_resolved`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统事件表';

-- =========================================================================
-- 会话与安全表
-- =========================================================================

-- 用户会话表
CREATE TABLE `user_sessions` (
    `id` VARCHAR(128) PRIMARY KEY COMMENT '会话ID',
    `user_id` INT NOT NULL COMMENT '用户ID',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `user_agent` VARCHAR(500) COMMENT '用户代理',
    `login_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    `last_activity` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后活动时间',
    `expires_at` DATETIME NOT NULL COMMENT '过期时间',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否活跃',
    `session_data` JSON COMMENT '会话数据',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_active` (`user_id`, `is_active`),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户会话表';

-- 登录尝试记录表
CREATE TABLE `login_attempts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) COMMENT '用户名',
    `ip_address` VARCHAR(50) NOT NULL COMMENT 'IP地址',
    `user_agent` VARCHAR(500) COMMENT '用户代理',
    `success` TINYINT(1) NOT NULL COMMENT '是否成功',
    `failure_reason` VARCHAR(100) COMMENT '失败原因',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_ip_time` (`ip_address`, `created_at`),
    INDEX `idx_username_time` (`username`, `created_at`),
    INDEX `idx_success_time` (`success`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录尝试记录表';

-- =========================================================================
-- 文件管理表
-- =========================================================================

-- 文件存储表
CREATE TABLE `file_storage` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `file_uuid` VARCHAR(36) NOT NULL UNIQUE COMMENT '文件UUID',
    `original_name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `stored_name` VARCHAR(255) NOT NULL COMMENT '存储文件名',
    `file_path` VARCHAR(500) NOT NULL COMMENT '文件路径',
    `file_size` BIGINT NOT NULL COMMENT '文件大小',
    `mime_type` VARCHAR(100) COMMENT 'MIME类型',
    `file_hash` VARCHAR(64) COMMENT '文件哈希值',
    `storage_type` ENUM('local', 'cloud', 'cdn') DEFAULT 'local' COMMENT '存储类型',
    `is_temporary` TINYINT(1) DEFAULT 0 COMMENT '是否临时文件',
    `reference_count` INT DEFAULT 0 COMMENT '引用计数',
    `uploaded_by` INT COMMENT '上传用户ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `accessed_at` DATETIME COMMENT '最后访问时间',
    FOREIGN KEY (`uploaded_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_uuid` (`file_uuid`),
    INDEX `idx_hash` (`file_hash`),
    INDEX `idx_temp_created` (`is_temporary`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件存储表';

-- =========================================================================
-- 初始化数据
-- =========================================================================

-- 插入默认管理员账号
INSERT INTO `users` (`username`, `password_hash`, `real_name`, `email`, `role`) VALUES
('admin', '$2b$12$rQ7gHJk5iYKx8YUi2Qq6CON5J7.Y1ZjxwqDbWH7VzP.PuL7nYqJwO', '系统管理员', 'admin@g1edu.com', 'admin'),
('operator', '$2b$12$rQ7gHJk5iYKx8YUi2Qq6CON5J7.Y1ZjxwqDbWH7VzP.PuL7nYqJwO', '操作员', 'operator@g1edu.com', 'operator'),
('demo', '$2b$12$rQ7gHJk5iYKx8YUi2Qq6CON5J7.Y1ZjxwqDbWH7VzP.PuL7nYqJwO', '演示用户', 'demo@g1edu.com', 'viewer');

-- 插入示例设备
INSERT INTO `equipment` (`id`, `name`, `location`, `status`, `ip_address`) VALUES
('G1-EDU-001', '教学机器人001', '北京海淀实验小学', 'online', '192.168.1.101'),
('G1-EDU-002', '教学机器人002', '上海东方小学', 'standby', '192.168.1.102'),
('G1-TOUR-001', '导览机器人001', '西湖风景区', 'touring', '192.168.1.201'),
('G1-EDU-005', '教学机器人005', '广州实验中学', 'offline', '192.168.1.105');

-- 插入课件分类
INSERT INTO `courseware_categories` (`name`, `description`) VALUES
('语文', '语文学科相关课件'),
('数学', '数学学科相关课件'),
('英语', '英语学科相关课件'),
('科学', '科学学科相关课件'),
('编程', '编程教育相关课件');

-- 插入系统设置
INSERT INTO `system_settings` (`category`, `setting_key`, `setting_value`, `value_type`, `description`, `is_system`) VALUES
('server', 'host', '0.0.0.0', 'string', '服务器监听地址', 1),
('server', 'port', '5001', 'integer', '服务器端口', 1),
('server', 'debug', 'false', 'boolean', '调试模式', 1),
('security', 'session_timeout', '3600', 'integer', '会话超时时间(秒)', 1),
('security', 'max_login_attempts', '5', 'integer', '最大登录尝试次数', 1),
('security', 'password_min_length', '6', 'integer', '密码最小长度', 1),
('notification', 'email_enabled', 'false', 'boolean', '邮件通知是否启用', 1),
('notification', 'sms_enabled', 'false', 'boolean', '短信通知是否启用', 1),
('data', 'backup_enabled', 'true', 'boolean', '数据备份是否启用', 1),
('data', 'log_retention_days', '30', 'integer', '日志保留天数', 1);

-- 插入今日统计数据
INSERT INTO `dashboard_statistics` (`statistic_date`, `total_devices`, `online_devices`, `offline_devices`, `error_devices`) VALUES
(CURDATE(), 4, 2, 2, 0);

-- =========================================================================
-- 创建视图
-- =========================================================================

-- 设备状态统计视图
CREATE VIEW `v_equipment_status_summary` AS
SELECT 
    COUNT(*) as total_devices,
    SUM(CASE WHEN is_offline = 0 THEN 1 ELSE 0 END) as online_devices,
    SUM(CASE WHEN is_offline = 1 THEN 1 ELSE 0 END) as offline_devices,
    SUM(CASE WHEN has_error = 1 THEN 1 ELSE 0 END) as error_devices,
    AVG(usage_rate) as avg_usage_rate,
    AVG(battery_level) as avg_battery_level
FROM `equipment`;

-- 用户活动统计视图
CREATE VIEW `v_user_activity_summary` AS
SELECT 
    u.id,
    u.username,
    u.real_name,
    u.role,
    u.last_login,
    COUNT(ol.id) as operation_count,
    MAX(ol.created_at) as last_operation
FROM `users` u
LEFT JOIN `operation_logs` ol ON u.id = ol.user_id
WHERE u.status = 1
GROUP BY u.id, u.username, u.real_name, u.role, u.last_login;

-- 课件使用统计视图
CREATE VIEW `v_courseware_usage_summary` AS
SELECT 
    c.id,
    c.title,
    c.file_type,
    c.subject,
    COUNT(cu.id) as total_usage,
    SUM(CASE WHEN cu.action = 'play' THEN 1 ELSE 0 END) as play_count,
    SUM(CASE WHEN cu.action = 'download' THEN 1 ELSE 0 END) as download_count,
    AVG(cu.duration) as avg_duration
FROM `courseware` c
LEFT JOIN `courseware_usage` cu ON c.id = cu.courseware_id
WHERE c.status = 'published'
GROUP BY c.id, c.title, c.file_type, c.subject;

-- =========================================================================
-- 创建存储过程
-- =========================================================================

DELIMITER //

-- 清理过期会话
CREATE PROCEDURE `CleanupExpiredSessions`()
BEGIN
    DELETE FROM `user_sessions` WHERE `expires_at` < NOW();
    SELECT ROW_COUNT() as deleted_sessions;
END //

-- 清理临时文件
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
END //

-- 更新每日统计
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
END //

DELIMITER ;

-- =========================================================================
-- 创建触发器
-- =========================================================================

DELIMITER //

-- 用户登录时更新统计
CREATE TRIGGER `tr_user_login_stats` 
AFTER UPDATE ON `users`
FOR EACH ROW
BEGIN
    IF NEW.last_login != OLD.last_login AND NEW.last_login IS NOT NULL THEN
        UPDATE `users` SET `login_count` = `login_count` + 1 WHERE `id` = NEW.id;
    END IF;
END //

-- 设备状态变更记录
CREATE TRIGGER `tr_equipment_status_change`
AFTER UPDATE ON `equipment`
FOR EACH ROW
BEGIN
    IF NEW.status != OLD.status THEN
        INSERT INTO `equipment_status_history` (
            `equipment_id`, `previous_status`, `current_status`, `change_reason`
        ) VALUES (
            NEW.id, OLD.status, NEW.status, 'System Update'
        );
    END IF;
END //

-- 课件使用计数更新
CREATE TRIGGER `tr_courseware_usage_count`
AFTER INSERT ON `courseware_usage`
FOR EACH ROW
BEGIN
    IF NEW.action = 'view' THEN
        UPDATE `courseware` SET `view_count` = `view_count` + 1 WHERE `id` = NEW.courseware_id;
    ELSEIF NEW.action = 'download' THEN
        UPDATE `courseware` SET `download_count` = `download_count` + 1 WHERE `id` = NEW.courseware_id;
    END IF;
END //

DELIMITER ;

-- =========================================================================
-- 创建索引优化
-- =========================================================================

-- 复合索引优化查询性能
CREATE INDEX `idx_equipment_status_location` ON `equipment` (`status`, `location`);
CREATE INDEX `idx_operation_logs_user_action_time` ON `operation_logs` (`user_id`, `action`, `created_at`);
CREATE INDEX `idx_equipment_logs_equipment_type_time` ON `equipment_logs` (`equipment_id`, `log_type`, `created_at`);
CREATE INDEX `idx_courseware_type_subject_status` ON `courseware` (`file_type`, `subject`, `status`);
CREATE INDEX `idx_navigation_points_equipment_enabled_type` ON `navigation_points` (`equipment_id`, `enabled`, `point_type`);

-- =========================================================================
-- 数据库权限设置建议
-- =========================================================================

/*
-- 创建应用程序用户
CREATE USER 'g1edu_app'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE ON g1_edu_system.* TO 'g1edu_app'@'localhost';

-- 创建只读用户(用于报表和监控)
CREATE USER 'g1edu_readonly'@'localhost' IDENTIFIED BY 'readonly_password_here';
GRANT SELECT ON g1_edu_system.* TO 'g1edu_readonly'@'localhost';

-- 创建备份用户
CREATE USER 'g1edu_backup'@'localhost' IDENTIFIED BY 'backup_password_here';
GRANT SELECT, LOCK TABLES ON g1_edu_system.* TO 'g1edu_backup'@'localhost';

FLUSH PRIVILEGES;
*/

-- =========================================================================
-- 数据库配置建议
-- =========================================================================

/*
-- 在 MySQL 配置文件 my.cnf 中添加以下配置:

[mysqld]
# 字符集设置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB 设置
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1

# 查询缓存
query_cache_type = 1
query_cache_size = 256M

# 连接设置
max_connections = 200
max_user_connections = 100

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 二进制日志(用于备份和复制)
log-bin = mysql-bin
expire_logs_days = 7
*/

-- =========================================================================
-- 维护任务建议
-- =========================================================================

/*
-- 建议创建以下定时任务(Cron Jobs):

-- 每天凌晨2点清理过期会话
0 2 * * * mysql -u g1edu_app -p g1_edu_system -e "CALL CleanupExpiredSessions();"

-- 每天凌晨3点清理临时文件
0 3 * * * mysql -u g1edu_app -p g1_edu_system -e "CALL CleanupTemporaryFiles();"

-- 每天凌晨1点更新统计数据
0 1 * * * mysql -u g1edu_app -p g1_edu_system -e "CALL UpdateDailyStatistics();"

-- 每周日凌晨4点优化表
0 4 * * 0 mysql -u g1edu_app -p g1_edu_system -e "OPTIMIZE TABLE equipment, users, operation_logs, equipment_logs;"

-- 每月1号备份数据库
0 5 1 * * mysqldump -u g1edu_backup -p g1_edu_system > /backup/g1_edu_$(date +\%Y\%m\%d).sql
*/