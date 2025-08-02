
#!/bin/bash
set -e

# Health check script for LexOS production deployment
# Checks API health, GPU status, and critical services

HEALTH_ENDPOINT="http://localhost:${LEXOS_PORT:-8000}/health"
TIMEOUT=10
MAX_RETRIES=3

echo "Running LexOS health check..."

# Function to check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local timeout=${2:-$TIMEOUT}
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check GPU health
check_gpu_health() {
    if command -v nvidia-smi &> /dev/null; then
        # Check if GPUs are accessible
        if nvidia-smi -q -d TEMPERATURE,UTILIZATION,MEMORY > /dev/null 2>&1; then
            # Check for any GPUs with critical temperature
            local max_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | sort -nr | head -1)
            if [ "$max_temp" -gt 85 ]; then
                echo "Warning: GPU temperature too high: ${max_temp}°C"
                return 1
            fi
            return 0
        else
            echo "Error: Cannot query GPU status"
            return 1
        fi
    else
        echo "Warning: nvidia-smi not available"
        return 0  # Don't fail if GPU monitoring is not available
    fi
}

# Function to check process health
check_process_health() {
    local process_name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            echo "Warning: $process_name process (PID: $pid) is not running"
            return 1
        fi
    else
        echo "Warning: $process_name PID file not found: $pidfile"
        return 1
    fi
}

# Main health check
main_health_check() {
    local retry_count=0
    local health_passed=false
    
    while [ $retry_count -lt $MAX_RETRIES ] && [ "$health_passed" = false ]; do
        echo "Health check attempt $((retry_count + 1))/$MAX_RETRIES"
        
        # Check main API endpoint
        if check_http_endpoint "$HEALTH_ENDPOINT"; then
            echo "✅ API health endpoint responding"
            
            # Check detailed health endpoint
            local health_response=$(curl -s --max-time $TIMEOUT "$HEALTH_ENDPOINT" 2>/dev/null)
            if echo "$health_response" | grep -q '"status":"healthy"'; then
                echo "✅ API reports healthy status"
                health_passed=true
            else
                echo "❌ API reports unhealthy status: $health_response"
            fi
        else
            echo "❌ API health endpoint not responding"
        fi
        
        if [ "$health_passed" = false ]; then
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $MAX_RETRIES ]; then
                echo "Retrying in 5 seconds..."
                sleep 5
            fi
        fi
    done
    
    return $([ "$health_passed" = true ] && echo 0 || echo 1)
}

# Extended health checks
extended_health_check() {
    local all_checks_passed=true
    
    echo "Running extended health checks..."
    
    # Check GPU health
    if check_gpu_health; then
        echo "✅ GPU health check passed"
    else
        echo "⚠️  GPU health check failed"
        all_checks_passed=false
    fi
    
    # Check Gunicorn process
    if check_process_health "Gunicorn" "/app/tmp/gunicorn.pid"; then
        echo "✅ Gunicorn process healthy"
    else
        echo "⚠️  Gunicorn process check failed"
        all_checks_passed=false
    fi
    
    # Check Celery worker (if enabled)
    if [ "$ENABLE_CELERY" = "true" ]; then
        if check_process_health "Celery" "/app/tmp/celery.pid"; then
            echo "✅ Celery worker healthy"
        else
            echo "⚠️  Celery worker check failed"
            all_checks_passed=false
        fi
    fi
    
    # Check vLLM server (if enabled)
    if [ "$ENABLE_VLLM" = "true" ]; then
        local vllm_endpoint="http://localhost:${VLLM_PORT:-8001}/health"
        if check_http_endpoint "$vllm_endpoint"; then
            echo "✅ vLLM server healthy"
        else
            echo "⚠️  vLLM server check failed"
            all_checks_passed=false
        fi
    fi
    
    # Check disk space
    local disk_usage=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        echo "✅ Disk usage OK ($disk_usage%)"
    else
        echo "⚠️  High disk usage: $disk_usage%"
        all_checks_passed=false
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$memory_usage" -lt 90 ]; then
        echo "✅ Memory usage OK ($memory_usage%)"
    else
        echo "⚠️  High memory usage: $memory_usage%"
        all_checks_passed=false
    fi
    
    return $([ "$all_checks_passed" = true ] && echo 0 || echo 1)
}

# Run health checks
if main_health_check; then
    echo "✅ Main health check passed"
    
    # Run extended checks if requested
    if [ "$1" = "--extended" ] || [ "$EXTENDED_HEALTH_CHECK" = "true" ]; then
        if extended_health_check; then
            echo "✅ All health checks passed"
            exit 0
        else
            echo "⚠️  Some extended health checks failed"
            exit 1
        fi
    else
        echo "✅ Health check completed successfully"
        exit 0
    fi
else
    echo "❌ Main health check failed"
    exit 1
fi
