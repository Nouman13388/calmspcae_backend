# PowerShell API Test Script

$baseUrl = "http://localhost:8000/api"

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Testing CalmSpace Backend API" -ForegroundColor Blue
Write-Host "========================================`n" -ForegroundColor Blue

# Test 1: API Health
Write-Host "1. Testing API Health..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -UseBasicParsing
    Write-Host "✓ API is running (Status: $($response.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "✗ API is not responding" -ForegroundColor Red
    exit
}

# Test 2: Login
Write-Host "`n2. Testing Login..." -ForegroundColor Cyan
$loginBody = @{
    email = "admin@test.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/login/" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $loginBody `
        -UseBasicParsing
    
    $data = $response.Content | ConvertFrom-Json
    $accessToken = $data.access
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Access Token: $($accessToken.Substring(0, 30))..." -ForegroundColor Yellow
}
catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    $accessToken = $null
}

# Test 3: Get Profile
if ($accessToken) {
    Write-Host "`n3. Testing Get Profile..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/auth/profile/" `
            -Method GET `
            -Headers @{"Authorization"="Bearer $accessToken"; "Content-Type"="application/json"} `
            -UseBasicParsing
        
        $data = $response.Content | ConvertFrom-Json
        Write-Host "✓ Profile retrieved successfully" -ForegroundColor Green
        Write-Host "  User: $($data.name) ($($data.email))" -ForegroundColor Yellow
        Write-Host "  Phone: $($data.phone_number)" -ForegroundColor Yellow
        Write-Host "  Type: $($data.user_type)" -ForegroundColor Yellow
        Write-Host "  Email Verified: $($data.is_email_verified)" -ForegroundColor Yellow
    }
    catch {
        Write-Host "✗ Get profile failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 4: User Registration
Write-Host "`n4. Testing User Registration..." -ForegroundColor Cyan
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$regBody = @{
    email = "testuser_$timestamp@test.com"
    name = "Test User"
    phone_number = "1234567890"
    user_type = "customer"
    password = "TestPassword123!"
    password_confirm = "TestPassword123!"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/register/" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $regBody `
        -UseBasicParsing
    
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✓ User registered successfully" -ForegroundColor Green
    Write-Host "  Email: $($data.user.email)" -ForegroundColor Yellow
    Write-Host "  Name: $($data.user.name)" -ForegroundColor Yellow
    Write-Host "  Email Verified: $($data.user.is_email_verified)" -ForegroundColor Yellow
}
catch {
    Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Forgot Password
Write-Host "`n5. Testing Forgot Password..." -ForegroundColor Cyan
$forgotBody = @{
    email = "admin@test.com"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/forgot-password/" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $forgotBody `
        -UseBasicParsing
    
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✓ Password reset email sent" -ForegroundColor Green
    Write-Host "  Message: $($data.message)" -ForegroundColor Yellow
}
catch {
    Write-Host "✗ Forgot password failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Authentication Protection
Write-Host "`n6. Testing Authentication Protection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/auth/profile/" `
        -Method GET `
        -Headers @{"Content-Type"="application/json"} `
        -UseBasicParsing -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✗ Authentication not enforced!" -ForegroundColor Red
    }
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.Value
    if ($statusCode -eq 401 -or $statusCode -eq 403) {
        Write-Host "✓ Authentication protection working ($statusCode returned)" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Response: $statusCode" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "Test Complete!" -ForegroundColor Blue
Write-Host "========================================`n" -ForegroundColor Blue

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Import CalmSpace_API.postman_collection.json into Postman"
Write-Host "2. Read AUTHENTICATION_GUIDE.md for API documentation"
Write-Host "3. Check TESTING_GUIDE.md for comprehensive test scenarios"
Write-Host "4. Configure email in .env for full functionality"
