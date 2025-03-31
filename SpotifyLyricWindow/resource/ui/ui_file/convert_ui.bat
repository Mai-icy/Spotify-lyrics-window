@echo off
chcp 65001 >nul
:: 检查是否有参数（即是否拖拽了文件）
if "%~1"=="" (
    echo 请将 .ui 文件拖拽到此批处理文件上！
    pause
    exit
)

:: 获取 PyQt6 的 pyuic6 路径（如果已安装到 Python）
set PYUIC=D:\Python\Python311\Scripts\pyuic6.exe

:: 处理每个拖拽的 .ui 文件
for %%F in (%*) do (
    echo 正在转换 %%~nxF ...
    %PYUIC% -o "%%~dpnF.py" "%%F"
    echo 生成的 Python 文件: %%~dpnF.py
)

echo 完成！
pause
