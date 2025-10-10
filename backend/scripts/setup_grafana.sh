#!/bin/bash
# Week 4 Preview: Grafana + Prometheus Setup for A5 Observability Polish
# Provides dashboards for UI metrics, conflict resolution, and SLO tracking

set -e

echo "📊 Week 4 Preview: Setting up Grafana + Prometheus for A5 Polish"
echo "================================================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker found"
echo ""

# Create prometheus config
echo "📝 Creating Prometheus configuration..."
mkdir -p backend/observability

cat > backend/observability/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # OTel Prometheus Exporter (metrics from workflow activities)
  - job_name: 'otel-metrics'
    static_configs:
      - targets: ['host.docker.internal:8889']
        labels:
          service: 'grok-orc-orchestrator'
          environment: 'dev'

  # FastAPI metrics (if exposed via prometheus_client)
  - job_name: 'swarm-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
        labels:
          service: 'swarm-api'

  # Temporal metrics (if exposed)
  - job_name: 'temporal'
    static_configs:
      - targets: ['host.docker.internal:8233']
        labels:
          service: 'temporal-server'

# SLO Rules (Week 4: Alert on breaches)
rule_files:
  - '/etc/prometheus/slo_rules.yml'
EOF

# Create SLO alert rules
cat > backend/observability/slo_rules.yml << 'EOF'
groups:
  - name: grok_orc_slos
    interval: 30s
    rules:
      # SLO: UI Confidence >0.8 (80%)
      - alert: LowUIConfidence
        expr: avg(stack_confidence) < 0.8
        for: 5m
        labels:
          severity: warning
          slo: ui_confidence
        annotations:
          summary: "UI stack confidence below SLO ({{$value}})"
          description: "Average stack inference confidence is {{$value}}, below 0.8 threshold"

      # SLO: Conflict resolution rate >90%
      - alert: HighConflictRate
        expr: (sum(rate(conflicts_detected[5m])) / sum(rate(workflows_completed[5m]))) > 0.1
        for: 10m
        labels:
          severity: critical
          slo: conflict_rate
        annotations:
          summary: "Conflict rate above SLO ({{$value}}%)"
          description: "UI/Backend conflicts detected in {{$value}}% of workflows (threshold: 10%)"

      # SLO: Visual test pass rate >95%
      - alert: VisualTestFailures
        expr: (sum(rate(visual_tests_failed[5m])) / sum(rate(visual_tests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: warning
          slo: visual_pass_rate
        annotations:
          summary: "Visual test failures above SLO"
          description: "{{$value}}% of visual tests failing (threshold: 5%)"

      # SLO: E2E latency <12 minutes (p95)
      - alert: SlowWorkflowLatency
        expr: histogram_quantile(0.95, workflow_duration_seconds_bucket) > 720
        for: 5m
        labels:
          severity: warning
          slo: e2e_latency
        annotations:
          summary: "Workflow latency exceeds SLO (p95: {{$value}}s)"
          description: "95th percentile workflow duration is {{$value}}s, above 720s (12min) threshold"

      # SLO: Cost per project <$5
      - alert: ProjectCostOverrun
        expr: sum(openrouter_tokens_used * 0.000005) by (project_id) > 5.0
        for: 1m
        labels:
          severity: critical
          slo: project_cost
        annotations:
          summary: "Project {{$labels.project_id}} cost exceeds $5"
          description: "Estimated cost: ${{$value}} (threshold: $5)"
EOF

# Create docker-compose for Grafana/Prometheus
echo "🐳 Creating Docker Compose configuration..."
cat > backend/observability/docker-compose-grafana.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: grok-orc-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./slo_rules.yml:/etc/prometheus/slo_rules.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - observability
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grok-orc-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    networks:
      - observability
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:

networks:
  observability:
    driver: bridge
EOF

# Create Grafana datasource config
echo "📡 Creating Grafana datasource configuration..."
mkdir -p backend/observability/grafana-dashboards

cat > backend/observability/grafana-datasources.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
EOF

# Create basic Grafana dashboard JSON
echo "📈 Creating Grok-orc Synergy Dashboard..."
cat > backend/observability/grafana-dashboards/grok-orc-synergy.json << 'EOF'
{
  "dashboard": {
    "title": "Grok-orc Synergy Metrics",
    "panels": [
      {
        "id": 1,
        "title": "Stack Inference Confidence (Avg)",
        "type": "graph",
        "targets": [{"expr": "avg(stack_confidence)", "legendFormat": "Avg Confidence"}],
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
      },
      {
        "id": 2,
        "title": "UI Components Generated per Workflow",
        "type": "graph",
        "targets": [{"expr": "rate(ui_components_generated[5m])", "legendFormat": "Components/min"}],
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
      },
      {
        "id": 3,
        "title": "Conflict Resolution Rate",
        "type": "stat",
        "targets": [{"expr": "(sum(conflicts_resolved) / sum(conflicts_detected)) * 100", "legendFormat": "Resolution %"}],
        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4}
      },
      {
        "id": 4,
        "title": "Visual Test Pass Rate",
        "type": "stat",
        "targets": [{"expr": "(sum(visual_tests_passed) / sum(visual_tests_total)) * 100", "legendFormat": "Pass %"}],
        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4}
      },
      {
        "id": 5,
        "title": "Workflow Duration (p95)",
        "type": "graph",
        "targets": [{"expr": "histogram_quantile(0.95, workflow_duration_seconds_bucket)", "legendFormat": "p95 Latency (s)"}],
        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
      },
      {
        "id": 6,
        "title": "Project Cost Estimate",
        "type": "graph",
        "targets": [{"expr": "sum(openrouter_tokens_used * 0.000005) by (project_id)", "legendFormat": "{{project_id}}"}],
        "gridPos": {"x": 0, "y": 16, "w": 24, "h": 8}
      }
    ],
    "refresh": "30s",
    "time": {"from": "now-1h", "to": "now"}
  }
}
EOF

# Start services
echo ""
echo "🚀 Starting Grafana + Prometheus..."
cd backend/observability
docker-compose -f docker-compose-grafana.yml up -d

echo ""
echo "⏳ Waiting for services to start (30s)..."
sleep 30

# Check if services are running
if docker ps | grep -q grok-orc-prometheus; then
    echo "   ✅ Prometheus running"
else
    echo "   ❌ Prometheus failed to start"
    exit 1
fi

if docker ps | grep -q grok-orc-grafana; then
    echo "   ✅ Grafana running"
else
    echo "   ❌ Grafana failed to start"
    exit 1
fi

echo ""
echo "🎉 Week 4 Observability Stack Ready!"
echo ""
echo "📊 Access Points:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "📈 Grafana Setup:"
echo "   1. Login: admin/admin"
echo "   2. Dashboard → Grok-orc Synergy Metrics (auto-provisioned)"
echo "   3. Explore → Query stack_confidence, conflicts_detected, etc."
echo ""
echo "🔔 SLO Alerts Configured:"
echo "   - UI Confidence <0.8 (warning after 5m)"
echo "   - Conflict Rate >10% (critical after 10m)"
echo "   - Visual Test Failures >5% (warning after 5m)"
echo "   - Workflow Latency >12min p95 (warning after 5m)"
echo "   - Project Cost >$5 (critical after 1m)"
echo ""
echo "🔍 View Alerts: http://localhost:9090/alerts"
echo ""
echo "🛑 Stop Services: cd backend/observability && docker-compose -f docker-compose-grafana.yml down"
