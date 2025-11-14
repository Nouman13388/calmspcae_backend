@echo off
REM Test API endpoints using curl and PowerShell

cd /d "d:\Github Desktop\calmspcae_backend"

echo.
echo ========================================
echo Testing CalmSpace Backend API
echo ========================================
echo.

echo 1. Testing API Health...
powershell -Command "Invoke-WebRequest -Uri 'http://localhost:8000/api/' -UseBasicParsing | Select-Object StatusCode"
echo.

echo 2. Testing User Registration...
powershell -Command "$body = @{email='testuser@example.com'; name='Test'; phone_number='1234567890'; user_type='customer'; password='Test123!'; password_confirm='Test123!'} | ConvertTo-Json; Invoke-WebRequest -Uri 'http://localhost:8000/api/auth/register/' -Method POST -Headers @{'Content-Type'='application/json'} -Body $body -UseBasicParsing | Select-Object StatusCode"
echo.

echo 3. Testing Login...
powershell -Command "$body = @{email='admin@test.com'; password='admin123'} | ConvertTo-Json; Invoke-WebRequest -Uri 'http://localhost:8000/api/auth/login/' -Method POST -Headers @{'Content-Type'='application/json'} -Body $body -UseBasicParsing | Select-Object StatusCode"
echo.

echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Import CalmSpace_API.postman_collection.json into Postman
echo 2. Read AUTHENTICATION_GUIDE.md for API documentation
echo 3. Check TESTING_GUIDE.md for comprehensive test scenarios
echo.
pause
