@echo off
echo Building Africa House Pakistan Trade Portal Executable
echo =====================================================

echo.
echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Building executable...
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "*.db;." --add-data ".env;." --hidden-import=flask --hidden-import=flask_mail --hidden-import=flask_cors --hidden-import=flask_sqlalchemy --hidden-import=sqlite3 --hidden-import=requests --hidden-import=email_utils --hidden-import=dotenv --name "AfricaHousePakistan" app.py

echo.
echo Step 3: Copying additional files...
copy .env dist\
copy *.db dist\
copy *.txt dist\

echo.
echo Step 4: Creating launcher script...
echo @echo off > dist\start_server.bat
echo echo Starting Africa House Pakistan Trade Portal... >> dist\start_server.bat
echo echo. >> dist\start_server.bat
echo echo The application will start on http://localhost:5000 >> dist\start_server.bat
echo echo Press Ctrl+C to stop the server >> dist\start_server.bat
echo echo. >> dist\start_server.bat
echo AfricaHousePakistan.exe >> dist\start_server.bat
echo pause >> dist\start_server.bat

echo.
echo =====================================================
echo BUILD COMPLETED!
echo.
echo Your executable is ready in the 'dist' folder:
echo - AfricaHousePakistan.exe (main application)
echo - start_server.bat (easy launcher)
echo.
echo To run: Double-click dist\start_server.bat
echo Then open http://localhost:5000 in your browser
echo =====================================================

pause
