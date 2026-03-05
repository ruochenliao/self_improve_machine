# Code Generation Prompts — 30 Templates for Rapid Development

> From idea to working code in one prompt. Stop writing boilerplate forever.

---

## 1. REST API Endpoint Generator

```
Generate a production-ready REST API endpoint with the following specifications:

- **Framework**: [FastAPI/Express/Django/Rails/Spring Boot]
- **Resource**: [e.g., "User", "Product", "Order"]
- **Operations**: [CRUD / specific operations]
- **Database**: [PostgreSQL/MongoDB/MySQL]
- **Authentication**: [JWT/API Key/OAuth2/None]

Include:
1. Route handler with proper HTTP methods and status codes
2. Request/response models with validation
3. Database model/schema
4. Error handling (400, 401, 403, 404, 409, 500)
5. Pagination for list endpoints
6. Input sanitization
7. OpenAPI/Swagger documentation annotations
8. Unit test stubs

Generate complete, runnable code.
```

---

## 2. Database Schema Generator

```
Design a database schema for: [describe your application]

Requirements:
- Database: [PostgreSQL/MySQL/MongoDB/SQLite]
- ORM: [SQLAlchemy/Prisma/TypeORM/Mongoose/None]

Generate:
1. Entity-relationship diagram (text format)
2. Table/collection definitions with proper data types
3. Indexes (covering common query patterns)
4. Foreign keys and relationships
5. Migration files
6. Seed data script
7. Common query examples

Performance considerations:
- Expected data volume: [e.g., 1M users, 10M orders]
- Read/write ratio: [e.g., 80/20]
- Most common queries: [describe]
```

---

## 3. Authentication System Generator

```
Generate a complete authentication system:

- **Framework**: [specify]
- **Auth method**: [JWT / Session / OAuth2 / Magic Link]
- **Features needed**:
  - [ ] Registration with email verification
  - [ ] Login with rate limiting
  - [ ] Password reset flow
  - [ ] Refresh token rotation
  - [ ] Multi-factor authentication (TOTP)
  - [ ] Social login (Google/GitHub)
  - [ ] Role-based access control (RBAC)
  - [ ] API key authentication

Include:
1. User model with password hashing (bcrypt/argon2)
2. Auth middleware/decorator
3. Token generation and validation
4. Route handlers for all auth endpoints
5. Email templates for verification/reset
6. Security best practices (CSRF, XSS prevention)
7. Tests for auth flows
```

---

## 4. React Component Generator

```
Generate a React component with these specifications:

- **Component name**: [e.g., DataTable, UserProfile, DashboardChart]
- **Functionality**: [describe what it does]
- **State management**: [useState/useReducer/Redux/Zustand]
- **Styling**: [Tailwind/CSS Modules/styled-components/MUI]
- **Data source**: [API endpoint / props / context]

Include:
1. TypeScript component with proper prop types
2. Custom hook for data fetching/logic
3. Loading, error, and empty states
4. Responsive design
5. Accessibility (ARIA, keyboard navigation)
6. Storybook story
7. Unit tests (React Testing Library)
8. Performance optimizations (React.memo, useMemo, useCallback where needed)
```

---

## 5. CLI Tool Generator

```
Generate a command-line tool:

- **Language**: [Python/Node.js/Go/Rust]
- **Purpose**: [describe what the CLI does]
- **Commands**: [list subcommands]
- **Input**: [files/stdin/arguments/flags]
- **Output**: [format: JSON/table/text/file]

Include:
1. Argument parsing (argparse/click/commander/cobra)
2. Help text and usage examples
3. Configuration file support
4. Colored output and progress bars
5. Error handling with helpful messages
6. Logging (verbose mode)
7. Shell completion script
8. Installation instructions
```

---

## 6. Microservice Generator

```
Generate a microservice:

- **Service name**: [e.g., notification-service, payment-service]
- **Framework**: [FastAPI/Express/Go Fiber/Spring Boot]
- **Communication**: [REST/gRPC/Message Queue]
- **Database**: [specify]

Include:
1. Service structure (clean architecture / hexagonal)
2. Health check and readiness endpoints
3. Structured logging with correlation IDs
4. Metrics endpoint (Prometheus format)
5. Circuit breaker for downstream calls
6. Dockerfile + docker-compose
7. Kubernetes deployment manifest
8. OpenAPI/Protobuf definition
9. Integration test setup
```

---

## 7. Data Pipeline Generator

```
Generate a data pipeline:

- **Source**: [API/Database/File/Stream]
- **Processing**: [describe transformations]
- **Destination**: [Database/Data Lake/API/File]
- **Schedule**: [real-time/hourly/daily]
- **Volume**: [estimate data size]

Include:
1. Extract — Data source connectors with retry logic
2. Transform — Data validation, cleaning, enrichment
3. Load — Batch/streaming write with idempotency
4. Error handling — Dead letter queue, alerting
5. Monitoring — Row counts, latency, error rates
6. Backfill — Historical data reprocessing support
7. Configuration — Environment-based settings
```

---

## 8. WebSocket Server Generator

```
Generate a WebSocket server:

- **Framework**: [FastAPI/Socket.io/ws/Gorilla]
- **Use case**: [chat/real-time dashboard/collaborative editing/notifications]

Include:
1. Connection management (connect/disconnect/reconnect)
2. Room/channel support
3. Message types and serialization
4. Authentication on connection
5. Heartbeat/ping-pong
6. Rate limiting per connection
7. Horizontal scaling strategy (Redis pub/sub)
8. Client-side code example
9. Load testing script
```

---

## 9. Email System Generator

```
Generate an email sending system:

- **Provider**: [SendGrid/AWS SES/Mailgun/SMTP]
- **Templates needed**: [Welcome/Reset/Notification/Invoice]
- **Framework**: [specify]

Include:
1. Email service abstraction (provider-agnostic interface)
2. HTML email templates (responsive, dark mode compatible)
3. Template rendering with variables
4. Queue-based sending (background job)
5. Retry logic with exponential backoff
6. Bounce and complaint handling
7. Unsubscribe management
8. Email preview/testing endpoint
```

---

## 10. File Upload System Generator

```
Generate a file upload system:

- **Storage**: [S3/GCS/Azure Blob/Local]
- **File types**: [images/documents/videos/any]
- **Max size**: [specify]
- **Framework**: [specify]

Include:
1. Multipart upload handler
2. File type validation (not just extension, check magic bytes)
3. Virus scanning integration point
4. Image processing (resize, thumbnail, WebP conversion)
5. Presigned URL generation for direct upload
6. Progress tracking
7. Resumable uploads for large files
8. CDN integration
9. Cleanup job for orphaned files
```

---

## 11. Search System Generator

```
Generate a search system:

- **Engine**: [Elasticsearch/Meilisearch/Typesense/PostgreSQL FTS]
- **Data**: [describe what's being searched]
- **Features**: [autocomplete/facets/fuzzy/filters/highlighting]

Include:
1. Index schema/mapping
2. Indexing pipeline (real-time + batch reindex)
3. Search API endpoint with filters, pagination, sorting
4. Autocomplete/suggest endpoint
5. Relevance tuning (boost fields, synonyms)
6. Faceted search
7. Search analytics (popular queries, zero-result queries)
```

---

## 12. Background Job System Generator

```
Generate a background job processing system:

- **Queue**: [Redis/RabbitMQ/SQS/Celery/BullMQ]
- **Jobs**: [describe job types]
- **Framework**: [specify]

Include:
1. Job definition with typed parameters
2. Queue configuration (priority, concurrency)
3. Retry strategy (exponential backoff, max retries, dead letter)
4. Job scheduling (cron, delayed, recurring)
5. Progress tracking and status updates
6. Monitoring dashboard data
7. Graceful shutdown handling
8. Distributed locking for singleton jobs
```

---

## 13. Caching Layer Generator

```
Generate a caching layer:

- **Cache**: [Redis/Memcached/In-memory]
- **Strategy**: [Cache-aside/Write-through/Write-behind]
- **Framework**: [specify]

Include:
1. Cache service with get/set/delete/invalidate
2. Decorator/middleware for automatic caching
3. Cache key generation strategy
4. TTL management per cache type
5. Cache warming on startup
6. Cache stampede prevention (mutex/probabilistic)
7. Multi-level caching (L1 in-memory + L2 Redis)
8. Cache hit/miss metrics
9. Graceful degradation when cache is down
```

---

## 14. Payment Integration Generator

```
Generate a payment integration:

- **Provider**: [Stripe/PayPal/Square]
- **Payment types**: [one-time/subscription/usage-based]
- **Framework**: [specify]

Include:
1. Payment intent/session creation
2. Webhook handler for payment events
3. Subscription management (create/upgrade/cancel)
4. Invoice generation
5. Refund processing
6. Failed payment retry logic
7. Idempotent transaction handling
8. PCI compliance best practices
9. Testing with provider's test mode
```

---

## 15. Rate Limiter Generator

```
Generate a rate limiting system:

- **Algorithm**: [Token bucket/Sliding window/Fixed window/Leaky bucket]
- **Storage**: [Redis/In-memory]
- **Framework**: [specify]
- **Limits**: [e.g., 100 req/min per user, 1000 req/min per IP]

Include:
1. Rate limiter middleware
2. Multiple limit tiers (free/pro/enterprise)
3. Rate limit headers (X-RateLimit-*)
4. Graceful 429 response with retry-after
5. Distributed rate limiting (multi-instance)
6. Burst allowance
7. Whitelist/bypass for internal services
8. Rate limit metrics and alerting
```

---

## 16. Notification System Generator

```
Generate a multi-channel notification system:

- **Channels**: [Email/SMS/Push/In-app/Slack/Webhook]
- **Framework**: [specify]

Include:
1. Notification service with channel abstraction
2. User preference management (opt-in/opt-out per channel)
3. Template system with variables
4. Priority levels (immediate/batch/digest)
5. Delivery tracking and read receipts
6. Retry logic per channel
7. Rate limiting (no spam)
8. Notification center API (list/mark-read/delete)
```

---

## 17. Logging & Monitoring Setup Generator

```
Generate a production logging and monitoring setup:

- **Stack**: [ELK/Grafana+Loki/Datadog/CloudWatch]
- **Application**: [describe your app]

Include:
1. Structured logging middleware (JSON format)
2. Correlation ID propagation
3. Request/response logging (with PII redaction)
4. Error tracking integration (Sentry style)
5. Health check endpoints
6. Prometheus metrics exporter
7. Grafana dashboard JSON
8. Alert rules (error rate, latency, saturation)
9. Log rotation and retention policy
```

---

## 18. GraphQL API Generator

```
Generate a GraphQL API:

- **Framework**: [Apollo Server/Strawberry/graphql-go/Ariadne]
- **Schema**: [describe entities and relationships]
- **Database**: [specify]

Include:
1. Schema definition (types, queries, mutations, subscriptions)
2. Resolvers with DataLoader for N+1 prevention
3. Input validation with custom scalars
4. Authentication and field-level authorization
5. Pagination (Relay cursor-based)
6. File upload mutation
7. Error handling with custom error types
8. Query complexity/depth limiting
9. Code generation setup (codegen)
```

---

## 19. Terraform/IaC Module Generator

```
Generate infrastructure as code:

- **Cloud**: [AWS/GCP/Azure]
- **Resources**: [describe what you need]
- **Tool**: [Terraform/Pulumi/CDK]

Include:
1. Module structure with variables and outputs
2. VPC/networking setup
3. Compute resources (ECS/EKS/Lambda/Cloud Run)
4. Database (RDS/DynamoDB/Cloud SQL)
5. Storage (S3/GCS)
6. IAM roles with least privilege
7. Monitoring and alerting
8. Remote state configuration
9. CI/CD pipeline for infrastructure
```

---

## 20. Test Suite Generator

```
Generate a comprehensive test suite for this code:

- **Testing framework**: [pytest/Jest/JUnit/Go testing]
- **Test types**: [unit/integration/e2e]

Include:
1. Unit tests for each function/method
2. Edge cases (empty input, max values, special characters, Unicode)
3. Error path tests (exceptions, network failures)
4. Integration tests with test database
5. Mock/stub setup for external dependencies
6. Test fixtures and factories
7. Performance/load test skeleton
8. CI configuration for test execution

Code to test:
```

---

## 21. CRUD Admin Dashboard Generator

```
Generate an admin dashboard:

- **Frontend**: [React/Vue/Next.js]
- **Styling**: [Tailwind/MUI/Ant Design]
- **Entities**: [list: User, Product, Order, etc.]

Include:
1. Data table with sort/filter/search/pagination
2. Create/Edit forms with validation
3. Detail view
4. Bulk actions (delete, export)
5. Dashboard overview (stats, charts)
6. Role-based UI (admin vs viewer)
7. Responsive design
8. Dark mode
```

---

## 22. OAuth2/SSO Integration Generator

```
Generate an OAuth2/SSO integration:

- **Providers**: [Google/GitHub/Apple/SAML]
- **Framework**: [specify]
- **Strategy**: [Authorization Code / PKCE]

Include:
1. OAuth2 flow implementation (redirect, callback, token exchange)
2. User creation/linking on first login
3. Account merging (same email, different providers)
4. Token storage and refresh
5. Logout/revocation
6. CSRF protection (state parameter)
7. PKCE for public clients
8. Error handling for denied/expired flows
```

---

## 23. Event-Driven Architecture Generator

```
Generate an event-driven system:

- **Message broker**: [Kafka/RabbitMQ/Redis Streams/SNS+SQS]
- **Events**: [list your domain events]
- **Framework**: [specify]

Include:
1. Event schema definitions (versioned)
2. Event publisher with outbox pattern
3. Event consumer with idempotent processing
4. Dead letter queue handling
5. Event sourcing (if applicable)
6. Saga/choreography for multi-step processes
7. Event replay capability
8. Monitoring (consumer lag, processing time)
```

---

## 24. Middleware/Plugin System Generator

```
Generate an extensible middleware/plugin system:

- **Language**: [specify]
- **Use case**: [HTTP middleware / data processing pipeline / event hooks]

Include:
1. Plugin interface/contract definition
2. Plugin registration and lifecycle management
3. Execution pipeline (ordered, parallel, conditional)
4. Plugin configuration and dependency injection
5. Error handling and circuit breaker per plugin
6. Hot-reload support
7. Plugin discovery (directory scanning, registry)
8. Example plugins (logging, auth, validation)
```

---

## 25. API Client SDK Generator

```
Generate a client SDK for this API:

- **API spec**: [provide endpoints or OpenAPI spec]
- **Language**: [Python/TypeScript/Go/Java]

Include:
1. Client class with configuration (base URL, auth, timeout)
2. Typed request/response models
3. Method for each endpoint with proper signatures
4. Authentication handling (API key, OAuth2, JWT)
5. Retry logic with exponential backoff
6. Rate limit handling (respect 429, queue requests)
7. Pagination helpers (iterator/generator)
8. Error types (network, auth, validation, server)
9. Async support
10. Package configuration (setup.py/package.json)
```

---

## 26. Migration Script Generator

```
Generate a data migration script:

- **From**: [describe source: old schema, CSV, API, legacy DB]
- **To**: [describe target: new schema, new service]
- **Volume**: [number of records]

Include:
1. Schema mapping (old fields → new fields)
2. Data transformation rules
3. Validation and data quality checks
4. Batch processing with progress tracking
5. Rollback strategy
6. Idempotent execution (safe to re-run)
7. Error handling and skip/retry logic
8. Verification queries (row counts, checksums)
9. Dry-run mode
```

---

## 27. Cron Job / Scheduled Task Generator

```
Generate a scheduled task system:

- **Tasks**: [describe periodic tasks]
- **Scheduler**: [APScheduler/node-cron/Kubernetes CronJob]
- **Framework**: [specify]

Include:
1. Task definitions with schedule (cron expression)
2. Distributed lock (prevent duplicate execution)
3. Execution logging and history
4. Error handling and alerting
5. Manual trigger endpoint
6. Task timeout and cancellation
7. Monitoring (last run, next run, success rate)
```

---

## 28. Feature Flag System Generator

```
Generate a feature flag system:

- **Storage**: [Database/Redis/Config file]
- **Framework**: [specify]

Include:
1. Flag definition (boolean, percentage, user segment)
2. Flag evaluation with fallback
3. A/B testing support (experiment assignment)
4. Admin API for flag management
5. Client-side SDK
6. Audit log (who changed what, when)
7. Flag lifecycle (created → active → deprecated → removed)
8. Performance (local cache, minimal latency)
```

---

## 29. Webhook System Generator

```
Generate a webhook delivery system:

- **Framework**: [specify]
- **Events**: [list webhook events]

Include:
1. Webhook registration API (URL, events, secret)
2. Event dispatch with signature (HMAC-SHA256)
3. Delivery queue with retry (exponential backoff)
4. Delivery log with response status
5. Webhook testing endpoint (send test event)
6. Auto-disable failing webhooks
7. Payload versioning
8. Rate limiting per webhook
```

---

## 30. Complete SaaS Boilerplate Generator

```
Generate a SaaS application boilerplate:

- **Stack**: [Next.js + Prisma / FastAPI + React / Rails + React]
- **Features**: [specify which to include]

Include:
1. Authentication (email + social login)
2. Multi-tenancy (organization/workspace model)
3. Subscription billing (Stripe integration)
4. User management (invite, roles, permissions)
5. API with rate limiting and API keys
6. Admin dashboard
7. Onboarding flow
8. Settings page (profile, billing, team)
9. Transactional emails
10. Error tracking and monitoring
11. CI/CD pipeline
12. Docker deployment
```
