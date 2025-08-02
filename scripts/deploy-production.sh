
#!/bin/bash
set -e

# Production deployment script for LexOS on H100 infrastructure
# This script handles the complete deployment process

echo "🔱 LexOS Production Deployment Script 🔱"
echo "Deploying to H100 GPU infrastructure..."

# Configuration
NAMESPACE="lexos"
DEPLOYMENT_NAME="lexos-api"
IMAGE_TAG=${IMAGE_TAG:-"latest"}
REGISTRY=${REGISTRY:-"ghcr.io/lexhelios"}
IMAGE_NAME="lexworking"
TIMEOUT=600

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE does not exist, creating..."
        kubectl apply -f k8s/namespace.yaml
    fi
    
    # Check GPU nodes
    local gpu_nodes=$(kubectl get nodes -l accelerator=nvidia-h100 --no-headers | wc -l)
    if [ "$gpu_nodes" -eq 0 ]; then
        log_error "No H100 GPU nodes found in the cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed ($gpu_nodes H100 GPU nodes available)"
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup current manifests
    kubectl get deployment $DEPLOYMENT_NAME -n $NAMESPACE -o yaml > "$backup_dir/deployment.yaml" 2>/dev/null || true
    kubectl get configmap lexos-config -n $NAMESPACE -o yaml > "$backup_dir/configmap.yaml" 2>/dev/null || true
    kubectl get secret lexos-secrets -n $NAMESPACE -o yaml > "$backup_dir/secrets.yaml" 2>/dev/null || true
    
    log_success "Backup created in $backup_dir"
}

# Update secrets
update_secrets() {
    log_info "Updating secrets..."
    
    # Check if secrets file exists and has been customized
    if [ ! -f "k8s/secrets.yaml" ]; then
        log_error "Secrets file not found: k8s/secrets.yaml"
        exit 1
    fi
    
    # Check for placeholder values
    if grep -q "REPLACE_WITH_" k8s/secrets.yaml; then
        log_error "Secrets file contains placeholder values. Please update k8s/secrets.yaml with actual secrets."
        exit 1
    fi
    
    kubectl apply -f k8s/secrets.yaml
    log_success "Secrets updated"
}

# Deploy infrastructure components
deploy_infrastructure() {
    log_info "Deploying infrastructure components..."
    
    # Apply in order
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/storage.yaml
    kubectl apply -f k8s/configmap.yaml
    
    # Wait for storage to be ready
    log_info "Waiting for storage to be ready..."
    kubectl wait --for=condition=Bound pvc/lexos-data-pvc -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=Bound pvc/lexos-models-pvc -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=Bound pvc/lexos-logs-pvc -n $NAMESPACE --timeout=300s
    
    # Deploy Redis cluster
    log_info "Deploying Redis cluster..."
    kubectl apply -f k8s/redis-cluster.yaml
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis cluster to be ready..."
    kubectl wait --for=condition=Ready pod -l app=redis-cluster -n $NAMESPACE --timeout=300s
    
    # Initialize Redis cluster
    log_info "Initializing Redis cluster..."
    kubectl apply -f k8s/redis-cluster.yaml
    
    log_success "Infrastructure components deployed"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring components..."
    
    kubectl apply -f monitoring/prometheus-rules.yaml
    kubectl apply -f monitoring/otel-config.yaml
    
    log_success "Monitoring components deployed"
}

# Update deployment image
update_deployment_image() {
    log_info "Updating deployment image to $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    
    # Update the deployment YAML with new image
    sed -i.bak "s|image: .*|image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG|g" k8s/lexos-deployment.yaml
    
    log_success "Deployment image updated"
}

# Deploy main application
deploy_application() {
    log_info "Deploying LexOS application..."
    
    # Apply deployment
    kubectl apply -f k8s/lexos-deployment.yaml
    
    # Apply HPA
    kubectl apply -f k8s/hpa.yaml
    
    # Apply ingress
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Application deployed"
}

# Wait for deployment
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    # Wait for deployment rollout
    if kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=${TIMEOUT}s; then
        log_success "Deployment rollout completed"
    else
        log_error "Deployment rollout failed or timed out"
        
        # Show pod status for debugging
        log_info "Pod status:"
        kubectl get pods -n $NAMESPACE -l app=lexos-api
        
        log_info "Recent events:"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
        
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # Wait a bit for services to stabilize
    sleep 30
    
    # Get service endpoint
    local service_ip=$(kubectl get service lexos-api-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    local service_port=$(kubectl get service lexos-api-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')
    
    # Run health check from within cluster
    if kubectl run health-check-$(date +%s) --rm -i --restart=Never --image=curlimages/curl -n $NAMESPACE -- \
        curl -f --max-time 30 "http://$service_ip:$service_port/health"; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        
        # Show logs for debugging
        log_info "Recent application logs:"
        kubectl logs -n $NAMESPACE -l app=lexos-api --tail=50
        
        exit 1
    fi
}

# GPU validation
validate_gpu_setup() {
    log_info "Validating H100 GPU setup..."
    
    # Check if pods are scheduled on GPU nodes
    local gpu_pods=$(kubectl get pods -n $NAMESPACE -l app=lexos-api -o jsonpath='{.items[*].spec.nodeName}' | xargs -n1 kubectl get node -o jsonpath='{.metadata.labels.accelerator}' | grep -c "nvidia-h100" || true)
    
    if [ "$gpu_pods" -gt 0 ]; then
        log_success "Pods scheduled on H100 GPU nodes"
    else
        log_warning "No pods found on H100 GPU nodes"
    fi
    
    # Check GPU resource allocation
    kubectl describe pods -n $NAMESPACE -l app=lexos-api | grep -A 5 -B 5 "nvidia.com/gpu" || log_warning "No GPU resources found in pod specs"
    
    log_success "GPU validation completed"
}

# Performance test
run_performance_test() {
    log_info "Running basic performance test..."
    
    # Simple load test using kubectl
    local service_ip=$(kubectl get service lexos-api-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    local service_port=$(kubectl get service lexos-api-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')
    
    # Run a simple concurrent test
    kubectl run perf-test-$(date +%s) --rm -i --restart=Never --image=curlimages/curl -n $NAMESPACE -- \
        sh -c "
        for i in \$(seq 1 10); do
            curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' http://$service_ip:$service_port/health &
        done
        wait
        " || log_warning "Performance test failed"
    
    log_success "Performance test completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary resources..."
    
    # Remove any temporary test pods
    kubectl delete pods -n $NAMESPACE -l app=temp-test --ignore-not-found=true
    
    # Restore original deployment file if backup exists
    if [ -f "k8s/lexos-deployment.yaml.bak" ]; then
        mv k8s/lexos-deployment.yaml.bak k8s/lexos-deployment.yaml
    fi
}

# Rollback function
rollback_deployment() {
    log_error "Rolling back deployment..."
    
    kubectl rollout undo deployment/$DEPLOYMENT_NAME -n $NAMESPACE
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    local start_time=$(date +%s)
    
    echo "Starting deployment at $(date)"
    echo "Image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    echo "Namespace: $NAMESPACE"
    echo "Timeout: ${TIMEOUT}s"
    echo ""
    
    # Set trap for cleanup
    trap cleanup EXIT
    trap 'rollback_deployment; exit 1' ERR
    
    # Run deployment steps
    check_prerequisites
    backup_deployment
    update_secrets
    deploy_infrastructure
    deploy_monitoring
    update_deployment_image
    deploy_application
    wait_for_deployment
    health_check
    validate_gpu_setup
    
    # Optional performance test
    if [ "$RUN_PERF_TEST" = "true" ]; then
        run_performance_test
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "🎉 Deployment completed successfully in ${duration}s!"
    
    # Show deployment info
    echo ""
    echo "Deployment Information:"
    echo "======================"
    kubectl get deployment $DEPLOYMENT_NAME -n $NAMESPACE
    echo ""
    kubectl get pods -n $NAMESPACE -l app=lexos-api
    echo ""
    kubectl get services -n $NAMESPACE
    echo ""
    
    # Show access information
    local ingress_ip=$(kubectl get ingress lexos-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
    echo "Access Information:"
    echo "=================="
    echo "API Endpoint: http://$ingress_ip (when ready)"
    echo "Health Check: http://$ingress_ip/health"
    echo "Metrics: http://$ingress_ip/metrics"
    echo ""
    
    log_success "LexOS is now running on H100 GPU infrastructure! 🚀"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --image-tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --perf-test)
            RUN_PERF_TEST="true"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --image-tag TAG    Docker image tag to deploy (default: latest)"
            echo "  --registry URL     Docker registry URL (default: ghcr.io/lexhelios)"
            echo "  --timeout SECONDS  Deployment timeout (default: 600)"
            echo "  --perf-test        Run performance test after deployment"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main deployment
main
