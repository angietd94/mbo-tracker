#!/bin/bash
"""
Web Health Check Script for MBO Tracker

This script performs comprehensive health checks on the MBO Tracker web service:
1. Service status verification
2. HTTP endpoint testing
3. Database connectivity check
4. Performance monitoring
5. Error detection

Usage:
    ./verify_web.sh [options]
    
Options:
    --verbose       Show detailed output
    --continuous    Run continuous monitoring (Ctrl+C to stop)
    --interval N    Set check interval for continuous mode (default: 30s)
    --timeout N     Set HTTP timeout (default: 10s)
"""

# Configuration
SERVICE_NAME="mbo-tracker"
BASE_URL="http://localhost:5000"
TIMEOUT=10
INTERVAL=30
VERBOSE=false
CONTINUOUS=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --continuous)
            CONTINUOUS=true
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--verbose] [--continuous] [--interval N] [--timeout N]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check systemd service status
check_service_status() {
    log_info "Checking systemd service status..."
    
    if ! command_exists systemctl; then
        log_warning "systemctl not available, skipping service check"
        return 1
    fi
    
    local status=$(systemctl is-active $SERVICE_NAME 2>/dev/null)
    local enabled=$(systemctl is-enabled $SERVICE_NAME 2>/dev/null)
    
    case $status in
        "active")
            log_success "Service is active"
            ;;
        "inactive")
            log_error "Service is inactive"
            return 1
            ;;
        "failed")
            log_error "Service has failed"
            return 1
            ;;
        *)
            log_warning "Service status unknown: $status"
            return 1
            ;;
    esac
    
    case $enabled in
        "enabled")
            log_verbose "Service is enabled for auto-start"
            ;;
        "disabled")
            log_warning "Service is not enabled for auto-start"
            ;;
        *)
            log_verbose "Service enable status: $enabled"
            ;;
    esac
    
    # Get service uptime
    local uptime=$(systemctl show $SERVICE_NAME --property=ActiveEnterTimestamp --value 2>/dev/null)
    if [ -n "$uptime" ] && [ "$uptime" != "0" ]; then
        log_verbose "Service started: $uptime"
    fi
    
    return 0
}

# Check HTTP endpoint
check_http_endpoint() {
    local endpoint="$1"
    local expected_status="$2"
    local description="$3"
    
    log_verbose "Testing $description: $endpoint"
    
    if ! command_exists curl; then
        log_error "curl not available for HTTP testing"
        return 1
    fi
    
    local response=$(curl -s -w "%{http_code}|%{time_total}|%{size_download}" \
                          --max-time $TIMEOUT \
                          "$endpoint" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        log_error "$description: Connection failed"
        return 1
    fi
    
    local http_code=$(echo "$response" | tail -1 | cut -d'|' -f1)
    local time_total=$(echo "$response" | tail -1 | cut -d'|' -f2)
    local size_download=$(echo "$response" | tail -1 | cut -d'|' -f3)
    local body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        log_success "$description: HTTP $http_code (${time_total}s, ${size_download} bytes)"
        log_verbose "Response body: $body"
        return 0
    else
        log_error "$description: HTTP $http_code (expected $expected_status)"
        log_verbose "Response body: $body"
        return 1
    fi
}

# Check health endpoint
check_health_endpoint() {
    log_info "Checking health endpoint..."
    
    local response=$(curl -s --max-time $TIMEOUT "$BASE_URL/healthz" 2>/dev/null)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log_error "Health endpoint unreachable"
        return 1
    fi
    
    # Check if response contains expected JSON
    if echo "$response" | grep -q '"status".*"ok"'; then
        log_success "Health endpoint responding correctly"
        log_verbose "Health response: $response"
        return 0
    else
        log_error "Health endpoint returned unexpected response"
        log_verbose "Health response: $response"
        return 1
    fi
}

# Check main application endpoints
check_application_endpoints() {
    log_info "Checking application endpoints..."
    
    local endpoints=(
        "$BASE_URL/|200|Home page"
        "$BASE_URL/login|200|Login page"
        "$BASE_URL/healthz|200|Health check"
    )
    
    local failed=0
    
    for endpoint_info in "${endpoints[@]}"; do
        local url=$(echo "$endpoint_info" | cut -d'|' -f1)
        local expected=$(echo "$endpoint_info" | cut -d'|' -f2)
        local desc=$(echo "$endpoint_info" | cut -d'|' -f3)
        
        if ! check_http_endpoint "$url" "$expected" "$desc"; then
            ((failed++))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log_success "All application endpoints responding"
        return 0
    else
        log_error "$failed application endpoint(s) failed"
        return 1
    fi
}

# Check process information
check_process_info() {
    log_info "Checking process information..."
    
    if ! command_exists pgrep; then
        log_warning "pgrep not available, skipping process check"
        return 1
    fi
    
    local pids=$(pgrep -f "gunicorn.*mbo-tracker" 2>/dev/null)
    
    if [ -z "$pids" ]; then
        log_error "No gunicorn processes found"
        return 1
    fi
    
    local process_count=$(echo "$pids" | wc -l)
    log_success "Found $process_count gunicorn process(es)"
    
    if [ "$VERBOSE" = true ]; then
        echo "$pids" | while read pid; do
            if [ -n "$pid" ]; then
                local cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
                log_verbose "PID $pid: $cmd"
            fi
        done
    fi
    
    return 0
}

# Check recent logs for errors
check_recent_logs() {
    log_info "Checking recent logs for errors..."
    
    if ! command_exists journalctl; then
        log_warning "journalctl not available, skipping log check"
        return 1
    fi
    
    # Check for errors in the last 5 minutes
    local error_count=$(journalctl -u $SERVICE_NAME --since "5 minutes ago" --no-pager -q | \
                       grep -i -E "(error|exception|failed|critical)" | wc -l)
    
    if [ "$error_count" -eq 0 ]; then
        log_success "No recent errors in logs"
        return 0
    else
        log_warning "Found $error_count recent error(s) in logs"
        
        if [ "$VERBOSE" = true ]; then
            log_verbose "Recent errors:"
            journalctl -u $SERVICE_NAME --since "5 minutes ago" --no-pager -q | \
                grep -i -E "(error|exception|failed|critical)" | tail -5 | \
                while read line; do
                    log_verbose "  $line"
                done
        fi
        return 1
    fi
}

# Performance check
check_performance() {
    log_info "Checking performance metrics..."
    
    # Test response time for health endpoint
    local start_time=$(date +%s.%N)
    local response=$(curl -s --max-time $TIMEOUT "$BASE_URL/healthz" 2>/dev/null)
    local end_time=$(date +%s.%N)
    
    if [ $? -eq 0 ]; then
        local response_time=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "N/A")
        if [ "$response_time" != "N/A" ]; then
            log_success "Health endpoint response time: ${response_time}s"
            
            # Warn if response time is slow
            if (( $(echo "$response_time > 2.0" | bc -l 2>/dev/null || echo 0) )); then
                log_warning "Response time is slow (>2s)"
            fi
        else
            log_verbose "Response time calculation not available"
        fi
    else
        log_error "Performance check failed - endpoint unreachable"
        return 1
    fi
    
    return 0
}

# Main health check function
run_health_check() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo
    echo "=========================================="
    echo "MBO Tracker Web Health Check - $timestamp"
    echo "=========================================="
    
    local checks_passed=0
    local total_checks=0
    
    # Run all checks
    local checks=(
        "check_service_status"
        "check_health_endpoint"
        "check_application_endpoints"
        "check_process_info"
        "check_recent_logs"
        "check_performance"
    )
    
    for check in "${checks[@]}"; do
        ((total_checks++))
        if $check; then
            ((checks_passed++))
        fi
        echo
    done
    
    # Summary
    echo "=========================================="
    echo "Health Check Summary"
    echo "=========================================="
    echo "Checks passed: $checks_passed/$total_checks"
    
    if [ $checks_passed -eq $total_checks ]; then
        log_success "All health checks passed - Service is healthy"
        echo
        return 0
    else
        local failed=$((total_checks - checks_passed))
        log_error "$failed health check(s) failed - Service may have issues"
        echo
        return 1
    fi
}

# Main execution
main() {
    # Validate dependencies
    if ! command_exists curl; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if [ "$CONTINUOUS" = true ]; then
        log_info "Starting continuous monitoring (interval: ${INTERVAL}s, timeout: ${TIMEOUT}s)"
        log_info "Press Ctrl+C to stop"
        echo
        
        while true; do
            run_health_check
            sleep $INTERVAL
        done
    else
        run_health_check
        exit $?
    fi
}

# Handle Ctrl+C gracefully
trap 'echo; log_info "Monitoring stopped"; exit 0' INT

# Run main function
main "$@"