@echo off
chcp 65001 >nul
echo ========================================
echo 宇树G1 EDU机器人管理系统 - 数据库同步工具
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

:: 检查PyMySQL是否安装
python -c "import pymysql" >nul 2>&1
if errorlevel 1 (
    echo 警告：未找到PyMySQL库，正在安装...
    pip install pymysql
    if errorlevel 1 (
        echo 错误：PyMySQL安装失败
        pause
        exit /b 1
    )
    echo PyMySQL安装成功
    echo.
)

:: 检查配置文件是否存在
if not exist "sync_config.json" (
    echo 未找到配置文件，正在创建示例配置文件...
    python sync_database.py --create-config
    if errorlevel 1 (
        echo 错误：创建配置文件失败
        pause
        exit /b 1
    )
    echo.
    echo 配置文件已创建：sync_config.json
    echo 请编辑配置文件后重新运行此脚本
    echo.
    pause
    exit /b 0
)

echo 开始数据库同步...
echo.
python sync_database.py

if errorlevel 1 (
    echo.
    echo 同步过程中出现错误，请查看日志文件：sync_database.log
) else (
    echo.
    echo 数据库同步完成！
)

echo.
echo 按任意键退出...
pause >nul