# Testing Prompts — 25 Templates for Bulletproof Code

> Generate comprehensive tests in seconds. Never ship untested code again.

---

## 1. Unit Test Generator

```
Generate comprehensive unit tests for this code:

Requirements:
- Framework: [pytest/Jest/JUnit/Go testing/RSpec]
- Coverage target: 90%+
- Include: Happy path, edge cases, error cases

For each function/method, generate tests for:
1. Normal input → expected output
2. Empty/null/undefined input
3. Boundary values (0, -1, MAX_INT, empty string)
4. Invalid input types
5. Error/exception paths
6. Side effects verification

Use descriptive test names following: test_[function]_[scenario]_[expected_result]
Use Arrange-Act-Assert pattern.

Code to test:
```

---

## 2. Integration Test Generator

```
Generate integration tests for this system:

- Components involved: [e.g., API → Service → Database]
- Test database: [SQLite in-memory / Docker PostgreSQL / TestContainers]
- Framework: [specify]

Include:
1. Test database setup/teardown
2. API endpoint tests with real HTTP calls
3. Database state verification after operations
4. Transaction rollback between tests
5. External service mocking (HTTP, message queue)
6. Authentication flow testing
7. Data consistency tests across components

System description:
```

---

## 3. E2E Test Generator

```
Generate end-to-end tests:

- Tool: [Playwright/Cypress/Selenium/Puppeteer]
- Application: [describe the app and its main flows]

Include:
1. User registration and login flow
2. Core feature happy path
3. Error handling (invalid input, network failure)
4. Cross-browser considerations
5. Mobile viewport tests
6. Page object model setup
7. Test data factories
8. Screenshot on failure
9. CI configuration

Main user flows to test:
```

---

## 4. API Contract Test Generator

```
Generate API contract tests:

- API spec: [provide endpoints or OpenAPI/Swagger spec]
- Tool: [Pact/Dredd/Schemathesis]

Include:
1. Request schema validation (required fields, types, formats)
2. Response schema validation (status codes, body structure)
3. Error response format consistency
4. Authentication requirement tests
5. Rate limiting behavior tests
6. Pagination contract tests
7. Consumer-driven contract tests
8. Breaking change detection

API endpoints:
```

---

## 5. Performance/Load Test Generator

```
Generate performance tests:

- Tool: [k6/Locust/JMeter/Artillery]
- Target: [API endpoints to test]
- Requirements:
  - Concurrent users: [number]
  - Response time target: [e.g., p95 < 200ms]
  - Throughput target: [e.g., 1000 req/s]

Include:
1. Ramp-up scenario (gradual load increase)
2. Sustained load test
3. Spike test (sudden traffic burst)
4. Stress test (find breaking point)
5. Soak test configuration (long-running)
6. Realistic user scenario with think time
7. Custom metrics and thresholds
8. HTML report generation
9. CI integration

Target endpoints:
```

---

## 6. Security Test Generator

```
Generate security tests for this application:

- Framework: [specify]
- Application type: [web/API/mobile backend]

Include:
1. SQL injection test cases
2. XSS (reflected, stored, DOM-based)
3. CSRF token validation
4. Authentication bypass attempts
5. Authorization boundary tests (horizontal/vertical)
6. Rate limiting enforcement
7. Input validation (special characters, Unicode, oversized input)
8. Header security (CORS, CSP, HSTS)
9. Session management (fixation, hijacking)
10. File upload security tests

Application endpoints:
```

---

## 7. Snapshot Test Generator

```
Generate snapshot tests for UI components:

- Framework: [Jest/Vitest + React Testing Library]
- Components: [list components]

Include:
1. Default render snapshot
2. Each prop variation snapshot
3. Loading state snapshot
4. Error state snapshot
5. Empty state snapshot
6. Interactive state changes
7. Responsive breakpoint snapshots
8. Theme/dark mode variants

Component:
```

---

## 8. Edge Case Test Generator

```
Given this code, identify and generate tests for ALL edge cases:

Think about:
1. **Numeric boundaries**: 0, -1, MAX_INT, MIN_INT, NaN, Infinity, floating point precision
2. **String boundaries**: empty, single char, very long (10MB), Unicode, emoji, RTL, null bytes
3. **Collection boundaries**: empty, single element, very large, nested, circular references
4. **Time boundaries**: midnight, DST transitions, leap years, year 2038, timezone changes
5. **Concurrency**: simultaneous operations, interleaved operations, timeout during operation
6. **Resource limits**: disk full, memory exhaustion, connection pool exhausted
7. **Network**: timeout, partial response, redirect loops, DNS failure
8. **State**: uninitialized, partially initialized, corrupted, concurrent modification

Code:
```

---

## 9. Mock/Stub Generator

```
Generate mocks and stubs for testing this code:

- Mocking framework: [unittest.mock/Jest/Mockito/gomock/testify]

For each external dependency:
1. Create a mock/stub implementation
2. Define expected behaviors for happy path
3. Define error simulation scenarios
4. Create factory functions for common mock setups
5. Ensure type safety of mocks
6. Add verification (was the mock called correctly?)

Code with dependencies to mock:
```

---

## 10. Test Data Factory Generator

```
Generate test data factories for these models:

- Library: [Factory Boy/Faker/Fishery/go-faker]
- Models: [describe your data models]

Include:
1. Factory for each model with sensible defaults
2. Traits/variations (e.g., admin user, premium user)
3. Related object generation (nested factories)
4. Sequence handling for unique fields
5. Realistic fake data (names, emails, addresses, dates)
6. Bulk generation helper
7. Database-backed and in-memory variants

Models:
```

---

## 11. Mutation Testing Prompt

```
Analyze this code and its tests for mutation testing quality:

1. List potential mutations (operator changes, boundary shifts, return value changes)
2. For each mutation, determine if current tests would catch it
3. Identify surviving mutants (tests that would still pass)
4. Generate additional tests to kill surviving mutants
5. Calculate estimated mutation score

Current tests:
[paste tests]

Code under test:
[paste code]
```

---

## 12. Property-Based Test Generator

```
Generate property-based tests (QuickCheck-style):

- Framework: [Hypothesis/fast-check/gopter/ScalaCheck]

For this code, identify:
1. Invariants that should always hold
2. Properties of the output given any valid input
3. Roundtrip properties (encode → decode = identity)
4. Idempotency properties (f(f(x)) = f(x))
5. Commutativity/associativity where applicable
6. Custom generators for domain-specific types

Code:
```

---

## 13. Database Test Generator

```
Generate database tests:

- Database: [PostgreSQL/MySQL/MongoDB]
- ORM: [specify]
- Test strategy: [in-memory SQLite/Docker/TestContainers]

Include:
1. Schema migration tests (up and down)
2. CRUD operation tests
3. Constraint validation (unique, foreign key, check)
4. Index effectiveness tests (EXPLAIN)
5. Transaction isolation tests
6. Concurrent access tests
7. Data integrity tests
8. Backup/restore verification
9. Performance regression tests for key queries

Models/Schema:
```

---

## 14. Error Handling Test Generator

```
Generate tests that verify error handling:

For each error scenario in this code:
1. Trigger the error condition
2. Verify the correct exception/error type is raised
3. Verify the error message is helpful
4. Verify error context/metadata is preserved
5. Verify cleanup occurs (resources released, partial state rolled back)
6. Verify the error is logged appropriately
7. Verify the error propagates correctly to callers
8. Verify recovery behavior (retry, fallback)

Code:
```

---

## 15. Accessibility Test Generator

```
Generate accessibility tests:

- Tool: [axe-core/pa11y/Lighthouse/jest-axe]
- Standard: [WCAG 2.1 AA/AAA]

Include:
1. Color contrast checks
2. Keyboard navigation flow
3. Screen reader compatibility
4. Focus management (modals, dynamic content)
5. Alt text for images
6. Form label associations
7. ARIA attribute correctness
8. Heading hierarchy
9. Skip navigation links
10. Dynamic content announcements

Components/Pages:
```

---

## 16. Regression Test Generator

```
A bug was found and fixed. Generate regression tests:

Bug description: [describe the bug]
Root cause: [explain why it happened]
Fix applied: [describe the fix]

Generate tests that:
1. Reproduce the exact original bug scenario
2. Test variations of the bug (similar inputs that might trigger it)
3. Test the boundary between buggy and correct behavior
4. Ensure the fix doesn't break existing functionality
5. Add a descriptive test name referencing the bug/ticket ID

Fixed code:
```

---

## 17. Test Refactoring Prompt

```
Refactor these tests for better quality:

1. Remove duplication (extract shared setup, use parameterized tests)
2. Improve naming (describe behavior, not implementation)
3. Reduce brittleness (don't test implementation details)
4. Add missing assertions
5. Improve test isolation (no shared state between tests)
6. Use proper assertion methods (assertEqual vs assertTrue)
7. Add test documentation/comments for complex scenarios
8. Organize with proper test classes/describe blocks

Current tests:
```

---

## 18. Contract/Schema Validation Test

```
Generate validation tests for this data schema/contract:

1. All required fields present
2. Field types correct
3. String format validation (email, URL, UUID, date)
4. Numeric range validation (min, max, precision)
5. Enum/allowed values
6. Nested object validation
7. Array min/max items
8. Cross-field validation rules
9. Default value application
10. Null/optional handling

Schema:
```

---

## 19. WebSocket Test Generator

```
Generate tests for WebSocket communication:

- Framework: [specify]
- Events: [list WebSocket events]

Include:
1. Connection establishment test
2. Authentication on connect
3. Message sending and receiving
4. Room/channel join and leave
5. Broadcast verification
6. Reconnection handling
7. Connection timeout
8. Invalid message handling
9. Concurrent connections
10. Message ordering

WebSocket implementation:
```

---

## 20. CI Pipeline Test Configuration

```
Generate CI test configuration:

- CI: [GitHub Actions/GitLab CI/CircleCI/Jenkins]
- Tests: [unit/integration/e2e/all]
- Language: [specify]

Include:
1. Parallel test execution
2. Test matrix (multiple versions/OS)
3. Database service containers
4. Cache configuration (dependencies, build)
5. Test result reporting (JUnit XML)
6. Coverage reporting and thresholds
7. Flaky test retry
8. Artifact upload (screenshots, logs)
9. Status badge configuration
```

---

## 21. Chaos/Resilience Test Generator

```
Generate chaos/resilience tests:

- Target: [describe your system]
- Infrastructure: [Kubernetes/Docker/cloud]

Include:
1. Network partition simulation
2. Service unavailability
3. High latency injection
4. CPU/memory pressure
5. Disk full simulation
6. DNS failure
7. Clock skew
8. Verify graceful degradation
9. Verify recovery after failure
10. Verify alerting triggers

System architecture:
```

---

## 22. Parameterized Test Generator

```
Convert these test cases into parameterized/table-driven tests:

For the given function, generate a comprehensive parameter table covering:
1. Normal inputs (multiple valid combinations)
2. Edge cases (boundaries, limits)
3. Invalid inputs (type errors, out of range)
4. Special values (null, empty, zero, negative)
5. Unicode and special character inputs
6. Performance-sensitive inputs (very large)

Function signature:
Expected behavior:
```

---

## 23. API Rate Limiting Test

```
Generate tests for API rate limiting:

- Rate limit: [e.g., 100 req/min per user]
- Framework: [specify]

Include:
1. Under-limit requests succeed
2. At-limit request succeeds
3. Over-limit request returns 429
4. Rate limit headers present (X-RateLimit-*)
5. Retry-After header correctness
6. Rate limit reset timing
7. Different limit tiers (free/pro/enterprise)
8. Distributed rate limiting (multi-instance)
9. Burst handling
```

---

## 24. Data Migration Test Generator

```
Generate tests for a data migration:

- Source: [old schema/format]
- Target: [new schema/format]

Include:
1. Row count verification (source = target)
2. Field mapping correctness
3. Data type conversion accuracy
4. Null/missing value handling
5. Referential integrity preservation
6. Idempotency (running twice produces same result)
7. Rollback verification
8. Performance benchmarks (time per 1000 records)
9. Edge case data (Unicode, very long strings, special chars)

Migration code:
```

---

## 25. Monitoring/Alert Test Generator

```
Generate tests for monitoring and alerting:

- Monitoring: [Prometheus/Datadog/CloudWatch]
- Alerting: [PagerDuty/OpsGenie/Slack]

Include:
1. Metrics are emitted correctly
2. Counter/gauge/histogram proper usage
3. Alert threshold triggers correctly
4. Alert resolves when condition clears
5. Alert routing to correct channel
6. Dashboard queries return expected data
7. Log-based alerts trigger correctly
8. Composite alert conditions
9. Alert deduplication

Application metrics:
```
