#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="fluent-bit-datadog"
HEALTH_ENDPOINT="http://localhost:2020/api/v1/health"
METRICS_ENDPOINT="http://localhost:2020/api/v1/metrics"
FORWARD_ENDPOINT="http://localhost:24224"

echo -e "${YELLOW}=== Fluent Bit Validation Script ===${NC}"

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        return 1
    fi
}

# Check if container is running
echo -e "\n${YELLOW}1. Checking container status...${NC}"
if docker ps | grep -q $CONTAINER_NAME; then
    print_status 0 "Container is running"
else
    print_status 1 "Container is not running"
    echo "Starting container..."
    docker-compose up -d
    sleep 10
fi

# Health check
echo -e "\n${YELLOW}2. Health check...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)
if [ "$response" -eq 200 ]; then
    print_status 0 "Health check passed (HTTP $response)"
else
    print_status 1 "Health check failed (HTTP $response)"
fi

# Metrics check
echo -e "\n${YELLOW}3. Metrics endpoint check...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" $METRICS_ENDPOINT)
if [ "$response" -eq 200 ]; then
    print_status 0 "Metrics endpoint accessible (HTTP $response)"
    echo "Sample metrics:"
    curl -s $METRICS_ENDPOINT | head -10
else
    print_status 1 "Metrics endpoint not accessible (HTTP $response)"
fi

# SSL/TLS verification
echo -e "\n${YELLOW}4. SSL/TLS configuration check...${NC}"
if docker exec $CONTAINER_NAME fluent-bit --help | grep -q "tls"; then
    print_status 0 "TLS support available"
else
    print_status 1 "TLS support not available"
fi

# Test log forwarding
echo -e "\n${YELLOW}5. Testing log forwarding...${NC}"
test_message='{"message":"Test log from validation script","level":"info","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'

# Send test log via Forward protocol
if command -v nc >/dev/null 2>&1; then
    echo "$test_message" | nc localhost 24224 && print_status 0 "Test log sent via Forward protocol"
else
    echo -e "${YELLOW}netcat not available, skipping Forward protocol test${NC}"
fi

# Send test log via HTTP (alternative method)
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$test_message" \
  "http://localhost:24224" 2>/dev/null && print_status 0 "Test log sent via HTTP" || echo -e "${YELLOW}HTTP log sending not available${NC}"

# Check container logs
echo -e "\n${YELLOW}6. Container logs (last 20 lines):${NC}"
docker logs --tail 20 $CONTAINER_NAME

# Datadog connectivity test
echo -e "\n${YELLOW}7. Testing Datadog connectivity...${NC}"
if [ -n "$DATADOG_API_KEY" ]; then
    # Test Datadog API connectivity
    datadog_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "DD-API-KEY: $DATADOG_API_KEY" \
        "https://api.datadoghq.com/api/v1/validate")
    
    if [ "$datadog_response" -eq 200 ]; then
        print_status 0 "Datadog API key is valid"
    else
        print_status 1 "Datadog API key validation failed (HTTP $datadog_response)"
    fi
    
    # Test Datadog logs intake connectivity
    intake_response=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://http-intake.logs.datadoghq.com")
    
    if [ "$intake_response" -eq 200 ] || [ "$intake_response" -eq 401 ]; then
        print_status 0 "Datadog logs intake is reachable"
    else
        print_status 1 "Datadog logs intake connectivity failed (HTTP $intake_response)"
    fi
else
    echo -e "${YELLOW}DATADOG_API_KEY not set, skipping Datadog connectivity tests${NC}"
fi

# Configuration validation
echo -e "\n${YELLOW}8. Configuration validation...${NC}"
if docker exec $CONTAINER_NAME fluent-bit -c /fluent-bit/config/fluent-bit.yaml -T; then
    print_status 0 "Configuration syntax is valid"
else
    print_status 1 "Configuration syntax validation failed"
fi

# Process check
echo -e "\n${YELLOW}9. Process check...${NC}"
if docker exec $CONTAINER_NAME pgrep fluent-bit > /dev/null; then
    print_status 0 "Fluent Bit process is running"
    echo "Process details:"
    docker exec $CONTAINER_NAME ps aux | grep fluent-bit | grep -v grep
else
    print_status 1 "Fluent Bit process is not running"
fi

# Resource usage
echo -e "\n${YELLOW}10. Resource usage:${NC}"
docker stats --no-stream $CONTAINER_NAME

echo -e "\n${YELLOW}=== Validation Complete ===${NC}"

# Additional curl commands for manual testing
echo -e "\n${YELLOW}=== Additional Manual Test Commands ===${NC}"
echo "1. Health check:"
echo "   curl -X GET $HEALTH_ENDPOINT"
echo ""
echo "2. Metrics:"
echo "   curl -X GET $METRICS_ENDPOINT"
echo ""
echo "3. Send test log via Forward protocol:"
echo "   echo '{\"message\":\"manual test\",\"level\":\"info\"}' | nc localhost 24224"
echo ""
echo "4. Check container logs:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "5. Test Datadog connectivity:"
echo "   curl -H \"DD-API-KEY: \$DATADOG_API_KEY\" https://api.datadoghq.com/api/v1/validate"