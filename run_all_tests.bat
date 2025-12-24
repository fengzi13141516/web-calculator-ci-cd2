@echo off
echo ============================================
echo Web计算器本地测试脚本
echo ============================================
echo.

echo 步骤1: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未在PATH中
    pause
    exit /b 1
)

echo Python已安装
echo.

echo 步骤2: 安装依赖
cd src
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo 警告: 依赖安装可能失败，尝试继续...
)
cd ..

echo.
echo 步骤3: 请确保应用程序正在运行
echo 如果应用程序未运行，请执行以下操作:
echo   1. 打开另一个命令提示符窗口
echo   2. 运行: cd src
echo   3. 运行: python app.py
echo.
echo 按任意键继续测试（确保应用程序已启动）...
pause >nul

echo.
echo 步骤4: 运行功能测试
cd src\tests\functional
python run_tests.py
if errorlevel 1 (
    echo 功能测试失败！
    echo.
    echo 可能的原因:
    echo   1. 应用程序未启动
    echo   2. 应用程序运行在非5000端口
    echo   3. 网络问题
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo 测试完成！
echo ============================================
pause