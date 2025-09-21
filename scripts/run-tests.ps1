# PowerShell test runner script
param(
    [string]$TestType = "all",
    [switch]$Coverage,
    [switch]$Verbose
)

# Colors
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue

function Write-ColorOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Run-Test {
    param(
        [string]$TestName,
        [string]$Command
    )
    
    Write-ColorOutput "🔍 Running $TestName..." $Blue
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ $TestName passed" $Green
            return $true
        } else {
            Write-ColorOutput "❌ $TestName failed" $Red
            return $false
        }
    } catch {
        Write-ColorOutput "❌ $TestName failed with exception: $($_.Exception.Message)" $Red
        return $false
    }
}

# Initialize counters
$TotalTests = 0
$PassedTests = 0
$FailedTests = 0

# Create reports directory
if (!(Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}

Write-ColorOutput "🧪 Starting comprehensive test suite..." $Yellow

# Backend Tests
if ($TestType -eq "all" -or $TestType -eq "backend") {
    Write-ColorOutput "`n🔧 Backend Tests" $Yellow
    Write-ColorOutput "==================" $Blue
    
    Push-Location backend
    
    # Install test dependencies
    Write-ColorOutput "📦 Installing test dependencies..." $Blue
    pip install -r requirements-test.txt
    
    # Unit Tests
    $TestCommand = "pytest tests/ -m 'unit'"
    if ($Verbose) { $TestCommand += " -v" }
    if ($Coverage) { $TestCommand += " --cov=." }
    
    if (Run-Test "Backend Unit Tests" $TestCommand) { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Integration Tests
    $TestCommand = "pytest tests/ -m 'integration'"
    if ($Verbose) { $TestCommand += " -v" }
    
    if (Run-Test "Backend Integration Tests" $TestCommand) { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # API Tests
    $TestCommand = "pytest tests/ -m 'api'"
    if ($Verbose) { $TestCommand += " -v" }
    
    if (Run-Test "API Tests" $TestCommand) { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Code Coverage Report
    if ($Coverage) {
        Write-ColorOutput "📊 Generating code coverage report..." $Blue
        pytest tests/ --cov=. --cov-report=html:../reports/backend-coverage --cov-report=xml:../reports/backend-coverage.xml
    }
    
    # Code Quality Checks
    Write-ColorOutput "🔍 Running code quality checks..." $Blue
    
    # Black formatting check
    if (Run-Test "Code Formatting (Black)" "black --check .") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Import sorting check
    if (Run-Test "Import Sorting (isort)" "isort --check-only .") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Linting
    if (Run-Test "Code Linting (flake8)" "flake8 .") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    Pop-Location
}

# Frontend Tests
if ($TestType -eq "all" -or $TestType -eq "frontend") {
    Write-ColorOutput "`n⚛️  Frontend Tests" $Yellow
    Write-ColorOutput "==================" $Blue
    
    Push-Location frontend
    
    # Install dependencies
    Write-ColorOutput "📦 Installing frontend dependencies..." $Blue
    npm ci
    
    # Unit Tests
    if (Run-Test "Frontend Unit Tests" "npm run test:unit") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Component Tests
    if (Run-Test "Component Tests" "npm run test:components") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    # Build Test
    if (Run-Test "Frontend Build Test" "npm run build") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    Pop-Location
}

# Docker Tests
if ($TestType -eq "all" -or $TestType -eq "docker") {
    Write-ColorOutput "`n🐳 Docker Tests" $Yellow
    Write-ColorOutput "===============" $Blue
    
    # Check if Docker is available
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        if (Run-Test "Backend Docker Build" "docker build -t rockfall-backend ./backend") { $PassedTests++ } else { $FailedTests++ }
        $TotalTests++
        
        if (Run-Test "Frontend Docker Build" "docker build -t rockfall-frontend ./frontend") { $PassedTests++ } else { $FailedTests++ }
        $TotalTests++
    } else {
        Write-ColorOutput "⚠️  Docker not available, skipping Docker tests" $Yellow
    }
}

# Security Tests
if ($TestType -eq "all" -or $TestType -eq "security") {
    Write-ColorOutput "`n🔒 Security Tests" $Yellow
    Write-ColorOutput "=================" $Blue
    
    Push-Location frontend
    
    # Node Security Check
    if (Run-Test "Node Security Check" "npm audit --audit-level moderate") { $PassedTests++ } else { $FailedTests++ }
    $TotalTests++
    
    Pop-Location
}

# Final Results
Write-ColorOutput "`n📋 Test Results Summary" $Yellow
Write-ColorOutput "=======================" $Blue

Write-ColorOutput "Total test suites: $TotalTests" $Blue
Write-ColorOutput "Passed: $PassedTests" $Green
Write-ColorOutput "Failed: $FailedTests" $Red

if ($FailedTests -eq 0) {
    Write-ColorOutput "🎉 All tests passed!" $Green
    exit 0
} else {
    Write-ColorOutput "💥 $FailedTests test suite(s) failed" $Red
    exit 1
}