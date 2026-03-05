# Code Review Prompts — 25 Battle-Tested Templates

> Copy-paste ready. Works with ChatGPT, Claude, DeepSeek, Gemini, and any LLM.

---

## 1. Comprehensive Code Review

```
You are a senior software engineer conducting a thorough code review. Analyze the following code for:

1. **Bugs & Logic Errors** — Race conditions, off-by-one errors, null/undefined handling
2. **Security Vulnerabilities** — SQL injection, XSS, CSRF, insecure deserialization
3. **Performance Issues** — N+1 queries, unnecessary allocations, blocking operations
4. **Code Quality** — Naming conventions, DRY violations, function complexity
5. **Best Practices** — Error handling, logging, testing considerations

For each issue found, provide:
- Severity: 🔴 Critical | 🟡 Warning | 🔵 Info
- Location: File and line reference
- Problem: What's wrong
- Fix: Corrected code snippet

Code to review:
```

---

## 2. Security-Focused Audit

```
Act as a cybersecurity expert reviewing code for vulnerabilities. Check for:

1. OWASP Top 10 vulnerabilities
2. Injection attacks (SQL, NoSQL, LDAP, OS command)
3. Authentication/authorization flaws
4. Sensitive data exposure (hardcoded secrets, PII leaks)
5. Insecure dependencies
6. Input validation gaps
7. Cryptographic weaknesses

For each finding, rate it using CVSS scoring and provide a remediation code snippet.

Code to audit:
```

---

## 3. Performance Review

```
You are a performance engineer. Analyze this code for performance bottlenecks:

1. Time complexity — Identify O(n²) or worse algorithms
2. Space complexity — Unnecessary memory allocations
3. I/O efficiency — Blocking calls, missing caching, excessive DB queries
4. Concurrency — Thread safety, deadlock potential, async opportunities
5. Resource management — Connection pools, file handles, memory leaks

Provide benchmarking suggestions and optimized code alternatives.

Code to analyze:
```

---

## 4. Architecture Review

```
As a software architect, review this code's architectural decisions:

1. Separation of concerns — Is business logic mixed with infrastructure?
2. Dependency management — Are dependencies properly injected/inverted?
3. Scalability — Will this code work at 10x/100x current load?
4. Testability — Can each component be unit tested in isolation?
5. Maintainability — Can a new developer understand and modify this easily?

Suggest architectural improvements with refactored code examples.

Code to review:
```

---

## 5. API Endpoint Review

```
Review this API endpoint implementation for:

1. REST/GraphQL best practices compliance
2. Input validation and sanitization
3. Error response format consistency (RFC 7807)
4. Rate limiting considerations
5. Authentication/authorization checks
6. Response pagination for list endpoints
7. Idempotency for mutation operations
8. API versioning strategy

Provide improved implementation.

Code:
```

---

## 6. Database Query Review

```
As a database performance expert, review these database queries/ORM code:

1. N+1 query detection
2. Missing indexes suggestions
3. Query optimization opportunities
4. Transaction handling correctness
5. Connection pool usage
6. Data consistency concerns
7. Migration safety (for schema changes)

Provide optimized queries with EXPLAIN ANALYZE suggestions.

Code:
```

---

## 7. Error Handling Review

```
Review this code's error handling strategy:

1. Are all error paths handled? (happy path bias detection)
2. Are errors properly categorized? (retryable vs fatal)
3. Is error context preserved? (stack traces, correlation IDs)
4. Are errors logged appropriately? (not too verbose, not too silent)
5. Are user-facing error messages helpful but not leaking internals?
6. Is there proper cleanup in error paths? (resources, partial operations)

Suggest a robust error handling pattern for this code.

Code:
```

---

## 8. Concurrency & Thread Safety Review

```
Analyze this code for concurrency issues:

1. Race conditions — Shared mutable state without synchronization
2. Deadlocks — Lock ordering violations
3. Starvation — Thread/goroutine starvation scenarios
4. Atomicity — Operations that should be atomic but aren't
5. Visibility — Memory ordering/caching issues
6. async/await correctness — Missing awaits, fire-and-forget issues

Provide thread-safe alternatives.

Code:
```

---

## 9. Frontend Component Review (React/Vue)

```
Review this frontend component for:

1. Re-render performance — Unnecessary re-renders, missing memoization
2. State management — Local vs global state decisions
3. Accessibility — ARIA attributes, keyboard navigation, screen reader support
4. Responsive design — Mobile/tablet/desktop breakpoints
5. Error boundaries — Component error handling
6. Memory leaks — Event listeners, subscriptions cleanup
7. Bundle size impact — Large imports, tree-shaking opportunities

Provide optimized component code.

Component:
```

---

## 10. TypeScript Type Safety Review

```
Review this TypeScript code for type safety:

1. `any` type usage — Replace with proper types
2. Type assertions — Validate necessity
3. Union type exhaustiveness — Missing switch cases
4. Null safety — Optional chaining and nullish coalescing
5. Generic constraints — Proper bounds
6. Interface vs Type — Consistency
7. Discriminated unions — Pattern correctness

Provide fully type-safe alternatives.

Code:
```

---

## 11. Docker/Container Review

```
Review this Dockerfile/docker-compose for:

1. Image size optimization — Multi-stage builds, layer caching
2. Security — Running as non-root, secrets handling, vulnerability scanning
3. Build cache efficiency — Layer ordering
4. Health checks — Proper health check endpoints
5. Resource limits — Memory/CPU constraints
6. Networking — Service discovery, port exposure
7. Volumes — Data persistence strategy

Provide optimized Dockerfile.

File:
```

---

## 12. CI/CD Pipeline Review

```
Review this CI/CD pipeline configuration for:

1. Build efficiency — Caching, parallel jobs, conditional execution
2. Security — Secrets management, artifact signing
3. Test strategy — Unit, integration, e2e test stages
4. Deployment safety — Blue/green, canary, rollback strategy
5. Notifications — Failure alerts, deployment notifications
6. Environment parity — Dev/staging/prod consistency

Provide improved pipeline configuration.

Pipeline config:
```

---

## 13. Python-Specific Code Review

```
Review this Python code against PEP 8 and modern Python best practices:

1. Type hints — Missing or incorrect annotations
2. Pythonic idioms — List comprehensions, generators, context managers
3. f-strings vs format — Consistency
4. dataclasses/Pydantic — Data modeling best practices
5. async/await — Proper asyncio patterns
6. Import organization — stdlib, third-party, local
7. Magic methods — Proper __repr__, __eq__, __hash__ implementation

Provide Pythonic refactored code.

Code:
```

---

## 14. Go-Specific Code Review

```
Review this Go code for idiomatic patterns:

1. Error handling — Wrapping, sentinel errors, error types
2. Goroutine leaks — Context cancellation, WaitGroups
3. Interface design — Accept interfaces, return structs
4. Package structure — Circular dependency detection
5. Channel usage — Buffered vs unbuffered, select patterns
6. Struct design — Embedding, method receivers
7. Testing — Table-driven tests, test helpers

Provide idiomatic Go alternatives.

Code:
```

---

## 15. Rust-Specific Code Review

```
Review this Rust code for:

1. Ownership & borrowing — Unnecessary clones, lifetime issues
2. Error handling — Result/Option usage, custom error types, thiserror
3. Unsafe code — Justification and soundness
4. Pattern matching — Exhaustive matching, destructuring
5. Iterator usage — Functional chains vs loops
6. Trait design — Default implementations, trait objects vs generics
7. Concurrency — Arc/Mutex usage, Send/Sync bounds

Provide optimized Rust code.

Code:
```

---

## 16. Code Smell Detection

```
Scan this code for common code smells:

1. Long Method (>20 lines) — Break into smaller functions
2. God Class — Class doing too much
3. Feature Envy — Method using another class's data more than its own
4. Primitive Obsession — Using primitives instead of value objects
5. Shotgun Surgery — A change requires editing many classes
6. Divergent Change — One class changed for many different reasons
7. Dead Code — Unreachable or unused code
8. Duplicate Code — Copy-paste patterns

For each smell, explain the refactoring technique to fix it.

Code:
```

---

## 17. Migration/Upgrade Review

```
I'm migrating/upgrading the following code from [OLD VERSION] to [NEW VERSION]. Review for:

1. Deprecated API usage — What needs to change?
2. Breaking changes — What will stop working?
3. New features — What new patterns should I adopt?
4. Performance changes — Any performance implications?
5. Security patches — What vulnerabilities does the upgrade fix?

Provide a migration plan and updated code.

Code:
```

---

## 18. Dependency/Import Review

```
Review the dependencies/imports in this project:

1. Unused imports/dependencies — What can be removed?
2. Outdated versions — What should be updated? (security, features)
3. Redundant dependencies — Multiple packages for the same purpose?
4. License compatibility — Any GPL/AGPL in an MIT project?
5. Bundle size impact — Can lighter alternatives be used?
6. Vulnerability scan — Known CVEs in current versions?

Provide a cleaned-up dependency list.

File:
```

---

## 19. Logging & Observability Review

```
Review this code's logging and observability:

1. Log levels — Correct use of DEBUG/INFO/WARN/ERROR
2. Structured logging — JSON format, consistent fields
3. Correlation IDs — Request tracing across services
4. Metrics — Key business and performance metrics
5. Health endpoints — Readiness and liveness probes
6. Alert conditions — What should trigger alerts?
7. PII in logs — Sensitive data leakage

Provide improved logging implementation.

Code:
```

---

## 20. Test Code Review

```
Review these tests for quality:

1. Test naming — Descriptive, follows conventions
2. Arrange-Act-Assert — Clear structure
3. Test isolation — No shared mutable state between tests
4. Edge cases — Boundary values, empty inputs, error paths
5. Mocking — Appropriate level of mocking (not too much/little)
6. Flaky test indicators — Time-dependent, order-dependent
7. Coverage gaps — What scenarios are missing?

Suggest additional test cases.

Tests:
```

---

## 21. Microservice Communication Review

```
Review this microservice communication code:

1. Circuit breaker — Handling downstream failures
2. Retry strategy — Exponential backoff, jitter
3. Timeout configuration — Request and connection timeouts
4. Serialization — Protobuf vs JSON, schema evolution
5. Service discovery — Static vs dynamic
6. Distributed tracing — Span propagation
7. Data consistency — Saga pattern, eventual consistency

Provide resilient communication code.

Code:
```

---

## 22. GraphQL Schema Review

```
Review this GraphQL schema/resolver for:

1. N+1 query prevention — DataLoader usage
2. Schema design — Types, interfaces, unions
3. Pagination — Cursor-based vs offset
4. Authorization — Field-level access control
5. Depth limiting — Query complexity limits
6. Error handling — Custom error types
7. Input validation — Scalars, directives

Provide optimized schema.

Schema:
```

---

## 23. Mobile App Code Review (React Native/Flutter)

```
Review this mobile app code for:

1. Performance — FlatList optimization, image caching
2. Navigation — Stack/tab navigator patterns
3. State management — Provider/Riverpod/Redux patterns
4. Native modules — Bridge performance
5. Offline support — Data persistence, sync strategy
6. Push notifications — Handling and deep linking
7. App lifecycle — Background/foreground transitions

Provide optimized mobile code.

Code:
```

---

## 24. Infrastructure as Code Review (Terraform/Pulumi)

```
Review this infrastructure code for:

1. State management — Remote state, state locking
2. Module design — Reusability, input validation
3. Security — IAM least privilege, encryption
4. Networking — VPC design, security groups
5. Cost optimization — Right-sizing, reserved instances
6. Drift detection — Preventing manual changes
7. Disaster recovery — Backup, multi-region

Provide improved infrastructure code.

Code:
```

---

## 25. Pull Request Review Template

```
I need to write a pull request review for the following changes. Help me write a thorough, constructive review that covers:

1. **Summary** — What does this PR do? Does it match the ticket/issue?
2. **Correctness** — Are there any bugs or logic errors?
3. **Design** — Is the approach reasonable? Are there better alternatives?
4. **Testing** — Are there adequate tests? What's missing?
5. **Documentation** — Are changes documented? API docs updated?
6. **Deployment** — Any migration needed? Feature flags? Rollback plan?

Format the review with specific line references, praise for good code, and constructive suggestions for improvements. Be kind but thorough.

PR diff:
```

---

## How to Use These Templates

1. **Copy the template** you need
2. **Paste your code** at the end
3. **Send to your preferred LLM** (ChatGPT, Claude, DeepSeek, etc.)
4. **Iterate** — Follow up with "Can you also check for [X]?"

### Pro Tips

- Combine templates: "Use template #1 and #6 together" for comprehensive reviews
- Add context: "This is a payment processing service handling $10M/year"
- Specify language/framework for more targeted advice
- Use with `git diff` output for PR reviews
