# Africa House Pakistan Trade Portal - Executable v2.0

## How to Run

1. Double-click `start_server.bat` to start the application
   OR
   Run `AfricaHousePakistan.exe` directly

2. Open your web browser and go to: http://localhost:5000

3. The application will start with all features:
   - User registration and login with email verification
   - AI Assistant with 50 partner companies (Pakistani, Rwandan, African)
   - Company database and search
   - Dashboard and user profiles
   - Mobile-friendly email verification

## New Features in v2.0

✅ FIXED EMAIL VERIFICATION:
   - Proper verification URLs that work on all devices
   - Manual verification option for mobile users
   - Dynamic URL generation for different networks

✅ ENHANCED AI ASSISTANT:
   - 50 companies in database (Pakistani, Rwandan, African businesses)
   - Smart company search and recommendations
   - Detailed company information and services

✅ MOBILE COMPATIBILITY:
   - Email verification works on mobile devices
   - Manual verification page available
   - Responsive design for all screen sizes

## Files Included

- AfricaHousePakistan.exe - Main application (91MB)
- start_server.bat - Easy launcher script
- .env - Configuration file
- database.db - User database
- companies.db - Company database (50 companies)

## Email Verification

### If Email Link Works:
1. Check your email after registration
2. Click the verification link
3. Complete verification automatically

### If Email Link Doesn't Work (Mobile/Different Device):
1. Go to the login page
2. Click "Manual Email Verification"
3. Enter your email and verification token from the email
4. Complete verification manually

## AI Assistant Features

Ask the AI about:
- "Tell me about Karachi Textile Mills"
- "What Pakistani companies do you have?"
- "Show me companies that export food products"
- "List companies from Rwanda"
- "Which companies offer IT services?"

The AI has information about 50 partner companies including:
- Pakistani businesses (Karachi, Lahore, Punjab, etc.)
- Rwandan companies (Kigali, tech, agriculture)
- African enterprises (textiles, mining, coffee, etc.)

## Troubleshooting

### Application Won't Start:
- Check that port 5000 is not in use
- Run as administrator if needed
- Ensure all .db files are present

### Email Verification Issues:
- Check spam/junk folder for verification email
- Use manual verification if link doesn't work
- Ensure internet connection for email sending

### AI Assistant Not Working:
- Verify companies.db file is present (should be 20KB+)
- Check console for any database errors
- Restart the application if needed

### Mobile Device Issues:
- Use manual verification instead of email links
- Access from computer browser for best experience
- Copy verification token from email for manual entry

## Configuration

Edit the .env file to configure:

### Email Settings:
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

### Application Settings:
BASE_URL=http://localhost:5000
SECRET_KEY=your-secret-key
APP_NAME=Africa House Pakistan

## Support

If you encounter issues:
1. Check the console window for error messages
2. Verify all files are present in the same folder
3. Try running as administrator
4. Check firewall settings for port 5000
5. Ensure .env file has correct email configuration

Enjoy using Africa House Pakistan Trade Portal v2.0! 🚀
