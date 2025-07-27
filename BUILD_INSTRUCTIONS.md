# Building Africa House Pakistan Trade Portal Executable

## Quick Start (Recommended)

### Option 1: Automated Build Script
```bash
python build_exe.py
```

### Option 2: Simple Batch File (Windows)
```bash
build_simple.bat
```

## Manual Build Process

### Step 1: Install Build Dependencies
```bash
pip install -r requirements_build.txt
```

### Step 2: Build with PyInstaller
```bash
pyinstaller --onefile ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "*.db;." ^
    --add-data ".env;." ^
    --hidden-import=flask ^
    --hidden-import=flask_mail ^
    --hidden-import=flask_cors ^
    --hidden-import=flask_sqlalchemy ^
    --hidden-import=sqlite3 ^
    --hidden-import=requests ^
    --hidden-import=email_utils ^
    --hidden-import=dotenv ^
    --name "AfricaHousePakistan" ^
    app.py
```

### Step 3: Copy Additional Files
```bash
copy .env dist\
copy *.db dist\
copy *.txt dist\
```

## What Gets Built

The build process creates:
- `dist/AfricaHousePakistan.exe` - Main executable
- `dist/start_server.bat` - Easy launcher script
- `dist/.env` - Configuration file
- `dist/database.db` - User database
- `dist/companies.db` - Company database
- `dist/README.txt` - Usage instructions

## Running the Executable

### Method 1: Easy Launcher
1. Navigate to the `dist` folder
2. Double-click `start_server.bat`
3. Open http://localhost:5000 in your browser

### Method 2: Direct Execution
1. Navigate to the `dist` folder
2. Double-click `AfricaHousePakistan.exe`
3. Open http://localhost:5000 in your browser

## Troubleshooting

### Build Issues

**Error: "Module not found"**
- Install missing dependencies: `pip install -r requirements_build.txt`
- Add missing modules to hidden imports

**Error: "File not found during build"**
- Ensure all database files exist
- Check that .env file is present
- Verify templates and static folders exist

**Error: "Permission denied"**
- Run command prompt as administrator
- Check antivirus isn't blocking PyInstaller

### Runtime Issues

**Error: "Port 5000 already in use"**
- Close other applications using port 5000
- Or modify the port in app.py

**Error: "Template not found"**
- Ensure templates folder is in the same directory as the .exe
- Check that PyInstaller included all template files

**Error: "Database not found"**
- Ensure .db files are in the same directory as the .exe
- Check file permissions

### Email Issues

**Error: "Failed to send verification email"**
- Update SMTP settings in .env file
- Check internet connection
- Verify Gmail app password (if using Gmail)

## Configuration

Edit the `.env` file in the dist folder to configure:

```env
SECRET_KEY=your-secret-key-change-this
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
APP_NAME=Africa House Pakistan
OPENROUTER_API_KEY=your-api-key-here
BASE_URL=http://localhost:5000
```

## Distribution

To distribute your application:

1. **Zip the dist folder** containing:
   - AfricaHousePakistan.exe
   - start_server.bat
   - .env (with your settings)
   - database.db
   - companies.db
   - README.txt

2. **Share the zip file** with users

3. **Users need to**:
   - Extract the zip file
   - Double-click start_server.bat
   - Open http://localhost:5000

## Advanced Options

### Custom Icon
Add `--icon=path/to/icon.ico` to the PyInstaller command

### Windows Service
Use tools like NSSM to run as a Windows service

### Different Port
Modify `app.py` to use a different port:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

### Hide Console Window
Use `--windowed` flag (but you'll lose error messages)

## File Structure After Build

```
dist/
├── AfricaHousePakistan.exe    # Main executable
├── start_server.bat           # Launcher script
├── .env                       # Configuration
├── database.db               # User database
├── companies.db              # Company database
├── README.txt                # User instructions
└── [other copied files]
```

## Notes

- The executable is self-contained but still needs the database files
- Configuration can be changed by editing the .env file
- The application runs locally on the user's machine
- No internet required except for email sending and AI features
- Database is portable - can be backed up/restored easily

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all required files are present
3. Check the .env configuration
4. Ensure port 5000 is available
5. Run as administrator if needed

Happy building! 🚀
