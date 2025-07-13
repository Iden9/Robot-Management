-- 宇树G1 EDU机器人管理系统数据库结构
-- 创建数据库
CREATE DATABASE IF NOT EXISTS g1_edu_system;
USE g1_edu_system;

-- 用户/账号表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'operator', 'viewer') NOT NULL DEFAULT 'viewer',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    status TINYINT(1) DEFAULT 1 COMMENT '1: 启用, 0: 禁用'
);

-- 设备表
CREATE TABLE IF NOT EXISTS equipment (
    id VARCHAR(50) PRIMARY KEY COMMENT '设备唯一标识，如G1-EDU-001',
    location VARCHAR(255) NOT NULL COMMENT '设备所在位置',
    status VARCHAR(50) COMMENT '设备当前状态',
    ip_address VARCHAR(50),
    last_active DATETIME,
    usage_rate VARCHAR(10),
    is_offline TINYINT(1) DEFAULT 0 COMMENT '1: 离线, 0: 在线',
    has_error TINYINT(1) DEFAULT 0 COMMENT '1: 有错误, 0: 正常',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 设备诊断/日志表
CREATE TABLE IF NOT EXISTS equipment_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    log_type ENUM('error', 'warning', 'info', 'debug') NOT NULL,
    message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);

-- 课件表
CREATE TABLE IF NOT EXISTS courseware (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    description TEXT,
    uploaded_by INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 教育培训配置表
CREATE TABLE IF NOT EXISTS education_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    screen_sync_mode ENUM('auto', 'manual', 'off') DEFAULT 'auto',
    ai_platform VARCHAR(50) DEFAULT 'xunfei',
    subject VARCHAR(50),
    voice_type VARCHAR(50) DEFAULT 'male',
    robot_action VARCHAR(50) DEFAULT 'standard',
    hand_recognition TINYINT(1) DEFAULT 1,
    interactive_qa TINYINT(1) DEFAULT 1,
    navigation_mode VARCHAR(50) DEFAULT 'default',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 导览设置表
CREATE TABLE IF NOT EXISTS navigation_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    scene_type VARCHAR(50) DEFAULT 'scenic',
    ai_platform VARCHAR(50) DEFAULT 'xunfei',
    voice_type VARCHAR(50) DEFAULT 'male',
    scene_prompt TEXT,
    object_recognition TINYINT(1) DEFAULT 1,
    recognition_action VARCHAR(50) DEFAULT 'move',
    auto_follow TINYINT(1) DEFAULT 0,
    patrol_mode VARCHAR(50) DEFAULT 'standard',
    navigation_mode VARCHAR(50) DEFAULT 'dynamic',
    emergency_alert TINYINT(1) DEFAULT 1,
    alert_mode VARCHAR(50) DEFAULT 'auto',
    robot_speed INT DEFAULT 50,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 导览点位表
CREATE TABLE IF NOT EXISTS navigation_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    rotation FLOAT DEFAULT 0,
    enabled TINYINT(1) DEFAULT 1,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);

-- 系统看板统计数据表
CREATE TABLE IF NOT EXISTS dashboard_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    statistic_date DATE NOT NULL,
    total_online_devices INT DEFAULT 0,
    total_offline_devices INT DEFAULT 0,
    total_error_devices INT DEFAULT 0,
    total_courses_delivered INT DEFAULT 0,
    total_tours_conducted INT DEFAULT 0,
    total_interactions INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 初始化管理员账号
INSERT INTO users (username, password, real_name, role) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin');