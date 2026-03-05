# DevOps & Infrastructure Prompts — 25 Templates

---

## 1. Dockerfile Optimizer
```
Optimize this Dockerfile for production:
1. Multi-stage build to minimize image size
2. Layer caching optimization (order commands by change frequency)
3. Security: non-root user, no secrets in image, vulnerability scanning
4. Health check configuration
5. .dockerignore file
6. Build arguments for flexibility
7. Target image size: < 100MB for compiled languages, < 200MB for Python/Node

Dockerfile:
```

## 2. Kubernetes Deployment Generator
```
Generate Kubernetes manifests for this application:
Include: Deployment, Service, Ingress, HPA, PDB, ConfigMap, Secret, ServiceAccount, NetworkPolicy, ResourceQuotas
Requirements: [replicas, resource limits, health checks, etc.]
Application:
```

## 3. CI/CD Pipeline Generator
```
Generate a CI/CD pipeline:
- Platform: [GitHub Actions/GitLab CI/CircleCI/Jenkins]
- Language: [specify]
Include: lint, test (parallel), build, security scan, deploy (staging→production), rollback, notifications, caching, manual approval gate.
Project:
```

## 4. Terraform Module Generator
```
Generate a Terraform module for [specify infrastructure]:
Include: variables with validation, outputs, resource definitions, data sources, state management, provider configuration, README with usage example.
Requirements:
```

## 5. Monitoring Stack Setup
```
Set up a monitoring stack for this application:
Include: Prometheus metrics, Grafana dashboards (JSON), alerting rules, log aggregation, distributed tracing, SLO/SLI definitions, uptime monitoring.
Application:
```

## 6-25: Additional Templates
Includes: Nginx/reverse proxy config, SSL/TLS setup, Backup strategy, Disaster recovery plan, Network architecture, Security hardening checklist, Auto-scaling configuration, Secrets management, Database high availability, CDN configuration, Container orchestration, Infrastructure cost optimization, Incident response automation, Blue-green deployment, Canary release configuration, Load balancer setup, Service mesh configuration, GitOps workflow, Infrastructure testing, Capacity planning.
