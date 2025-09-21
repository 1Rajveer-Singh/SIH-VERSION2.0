#!/bin/bash
# Comprehensive test runner script

set -e

echo "🧪 Starting comprehensive test suite..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

# Function to run command and check result
run_test() {
    local test_name="$1"
    local command="$2"
    
    print_color $BLUE "🔍 Running $test_name..."
    
    if eval "$command"; then
        print_color $GREEN "✅ $test_name passed"
        return 0
    else
        print_color $RED "❌ $test_name failed"
        return 1
    fi
}

# Create test reports directory
mkdir -p reports

# Initialize test results
total_tests=0
passed_tests=0
failed_tests=0

# Backend Tests
print_color $YELLOW "🔧 Backend Tests"
print_color $BLUE "=================="

cd backend

# Install test dependencies
print_color $BLUE "📦 Installing test dependencies..."
pip install -r requirements-test.txt

# Unit Tests
if run_test "Backend Unit Tests" "pytest tests/ -m 'unit' -v"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Integration Tests
if run_test "Backend Integration Tests" "pytest tests/ -m 'integration' -v"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# API Tests
if run_test "API Tests" "pytest tests/ -m 'api' -v"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# ML Model Tests
if run_test "ML Model Tests" "pytest tests/ -m 'ml' -v"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Database Tests
if run_test "Database Tests" "pytest tests/ -m 'db' -v"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Code Coverage Report
print_color $BLUE "📊 Generating code coverage report..."
pytest tests/ --cov=. --cov-report=html:../reports/backend-coverage --cov-report=xml:../reports/backend-coverage.xml

# Code Quality Checks
print_color $BLUE "🔍 Running code quality checks..."

# Black formatting check
if run_test "Code Formatting (Black)" "black --check ."; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Import sorting check
if run_test "Import Sorting (isort)" "isort --check-only ."; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Linting
if run_test "Code Linting (flake8)" "flake8 ."; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Type checking
if run_test "Type Checking (mypy)" "mypy ."; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

cd ..

# Frontend Tests
print_color $YELLOW "⚛️  Frontend Tests"
print_color $BLUE "=================="

cd frontend

# Install dependencies
print_color $BLUE "📦 Installing frontend dependencies..."
npm ci

# Unit Tests
if run_test "Frontend Unit Tests" "npm run test:unit"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Component Tests
if run_test "Component Tests" "npm run test:components"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Integration Tests
if run_test "Frontend Integration Tests" "npm run test:integration"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# E2E Tests (if available)
if command -v cypress &> /dev/null; then
    if run_test "E2E Tests" "npm run test:e2e"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_color $YELLOW "⚠️  Cypress not installed, skipping E2E tests"
fi

# Build Test
if run_test "Frontend Build Test" "npm run build"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

cd ..

# System Tests
print_color $YELLOW "🌐 System Tests"
print_color $BLUE "==============="

# Docker Build Tests
if command -v docker &> /dev/null; then
    if run_test "Backend Docker Build" "docker build -t rockfall-backend ./backend"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    if run_test "Frontend Docker Build" "docker build -t rockfall-frontend ./frontend"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_color $YELLOW "⚠️  Docker not available, skipping Docker build tests"
fi

# Security Tests
print_color $BLUE "🔒 Security Tests"

# Check for known vulnerabilities in Python packages
if command -v safety &> /dev/null; then
    if run_test "Python Security Check" "cd backend && safety check"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_color $YELLOW "⚠️  Safety not installed, skipping Python security check"
fi

# Check for known vulnerabilities in Node packages
if run_test "Node Security Check" "cd frontend && npm audit --audit-level moderate"; then
    ((passed_tests++))
else
    ((failed_tests++))
fi
((total_tests++))

# Performance Tests
print_color $BLUE "⚡ Performance Tests"

# Load testing (if available)
if command -v locust &> /dev/null; then
    print_color $BLUE "🏃 Running load tests..."
    # Add load test command here
    print_color $YELLOW "⚠️  Load tests configured but not run (requires running services)"
else
    print_color $YELLOW "⚠️  Locust not installed, skipping load tests"
fi

# Final Results
print_color $YELLOW "📋 Test Results Summary"
print_color $BLUE "======================="

print_color $BLUE "Total test suites: $total_tests"
print_color $GREEN "Passed: $passed_tests"
print_color $RED "Failed: $failed_tests"

if [ $failed_tests -eq 0 ]; then
    print_color $GREEN "🎉 All tests passed!"
    exit 0
else
    print_color $RED "💥 $failed_tests test suite(s) failed"
    exit 1
fi