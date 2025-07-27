"""
Build script to create executable for Africa House Pakistan Trade Portal
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for the Flask app"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('*.db', '.'),
        ('.env', '.'),
        ('*.txt', '.'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_mail',
        'flask_cors',
        'flask_sqlalchemy',
        'sqlite3',
        'requests',
        'email_utils',
        'dotenv',
        'itsdangerous',
        'jinja2',
        'werkzeug',
        'markupsafe',
        'click',
        'blinker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AfricaHousePakistan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('AfricaHousePakistan.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Run PyInstaller with the spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "AfricaHousePakistan.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            print("📁 Executable location: dist/AfricaHousePakistan.exe")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

def create_launcher_script():
    """Create a launcher script for the executable"""
    launcher_content = '''@echo off
echo Starting Africa House Pakistan Trade Portal...
echo.
echo The application will start on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
AfricaHousePakistan.exe

pause
'''
    
    with open('dist/start_server.bat', 'w') as f:
        f.write(launcher_content)
    print("✅ Created launcher script: dist/start_server.bat")

def copy_additional_files():
    """Copy additional files needed for the executable"""
    files_to_copy = [
        '.env',
        'database.db',
        'companies.db',
        'requirements.txt',
        'README.md' if os.path.exists('README.md') else None,
    ]

    # Ensure companies.db exists and has data
    if os.path.exists('companies.db'):
        print(f"✅ Found companies.db")
    else:
        print(f"⚠️  companies.db not found - running seed script...")
        os.system('python seed_companies.py')
    
    dist_dir = Path('dist')
    
    for file_name in files_to_copy:
        if file_name and os.path.exists(file_name):
            try:
                shutil.copy2(file_name, dist_dir / file_name)
                print(f"✅ Copied {file_name}")
            except Exception as e:
                print(f"⚠️  Could not copy {file_name}: {e}")

def create_readme():
    """Create README for the executable"""
    readme_content = '''# Africa House Pakistan Trade Portal - Executable

## How to Run

1. Double-click `start_server.bat` to start the application
   OR
   Run `AfricaHousePakistan.exe` directly

2. Open your web browser and go to: http://localhost:5000

3. The application will start with all features:
   - User registration and login
   - AI Assistant
   - Company database
   - Dashboard and profiles

## Files Included

- AfricaHousePakistan.exe - Main application
- start_server.bat - Easy launcher script
- .env - Configuration file
- database.db - User database
- companies.db - Company database
- templates/ - HTML templates
- static/ - CSS, JS, and images

## Troubleshooting

1. If the application doesn't start:
   - Check that port 5000 is not in use
   - Run as administrator if needed
   - Check .env file for correct configuration

2. If email verification doesn't work:
   - Update SMTP settings in .env file
   - Check internet connection

3. For support:
   - Check console output for error messages
   - Ensure all database files are present

## Configuration

Edit the .env file to configure:
- Email settings (SMTP)
- API keys
- Application settings

Enjoy using Africa House Pakistan Trade Portal!
'''
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    print("✅ Created README.txt")

def main():
    """Main build process"""
    print("🚀 Building Africa House Pakistan Trade Portal Executable")
    print("=" * 60)
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Step 2: Create spec file
    create_spec_file()
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Step 4: Copy additional files
    copy_additional_files()
    
    # Step 5: Create launcher script
    create_launcher_script()
    
    # Step 6: Create README
    create_readme()
    
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("📁 Your executable is ready in the 'dist' folder")
    print("🚀 Run 'dist/start_server.bat' to start the application")
    print("🌐 Then open http://localhost:5000 in your browser")
    
    return True

if __name__ == "__main__":
    main()
