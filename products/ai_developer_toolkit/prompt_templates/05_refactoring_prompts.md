# Refactoring Prompts — 25 Templates for Clean, Maintainable Code

---

## 1. Clean Code Refactoring
```
Refactor this code following Clean Code principles:
1. Meaningful names — Variables, functions, classes should reveal intent
2. Small functions — Each function does ONE thing (max 20 lines)
3. No side effects — Functions should be predictable
4. DRY — Remove all duplication
5. Single level of abstraction per function
6. Minimal arguments (ideally ≤ 3)
7. No magic numbers/strings — Use named constants
8. Guard clauses instead of nested if-else

Show the refactored code with comments explaining each change.
Code:
```

## 2. SOLID Principles Refactoring
```
Refactor this code to follow SOLID principles:
1. Single Responsibility — Each class has one reason to change
2. Open/Closed — Open for extension, closed for modification
3. Liskov Substitution — Subtypes must be substitutable
4. Interface Segregation — No client depends on methods it doesn't use
5. Dependency Inversion — Depend on abstractions, not concretions

For each violation found, explain the problem and show the fix.
Code:
```

## 3. Design Pattern Application
```
Analyze this code and suggest which design patterns would improve it:
- Creational: Factory, Builder, Singleton
- Structural: Adapter, Decorator, Facade, Proxy
- Behavioral: Strategy, Observer, Command, State, Chain of Responsibility

For each suggested pattern:
1. Explain WHY it's appropriate here
2. Show the refactored code using the pattern
3. Explain the trade-offs

Code:
```

## 4. Extract Service/Module
```
This code is doing too much. Help me extract it into well-defined services/modules:
1. Identify distinct responsibilities
2. Define clear interfaces between modules
3. Handle shared state and dependencies
4. Ensure each module is independently testable
5. Create an integration point (facade/coordinator)

Code:
```

## 5. Legacy Code Modernization
```
Modernize this legacy code to use current language features and best practices:
- Language: [specify language and current version]
- Target: [specify target version]

Update:
1. Deprecated API usage → modern equivalents
2. Callback hell → async/await
3. var → const/let (or type inference)
4. String concatenation → template literals/f-strings
5. Manual loops → functional methods (map, filter, reduce)
6. Class-based → functional (if appropriate)
7. Add type annotations/hints

Code:
```

## 6. Reduce Cyclomatic Complexity
```
This code has high cyclomatic complexity. Reduce it:
1. Replace nested conditionals with guard clauses
2. Replace switch/if-else chains with strategy pattern or lookup tables
3. Extract complex conditions into named boolean methods
4. Replace conditional logic with polymorphism
5. Simplify boolean expressions

Target: Cyclomatic complexity ≤ 5 per function.
Code:
```

## 7. Error Handling Improvement
```
Improve error handling in this code:
1. Replace generic exceptions with specific types
2. Add context to errors (what was attempted, with what data)
3. Implement proper error propagation (wrap, don't swallow)
4. Add retry logic where appropriate
5. Ensure resource cleanup in error paths
6. Create a consistent error handling strategy

Code:
```

## 8. Performance Optimization Refactoring
```
Refactor this code for better performance without sacrificing readability:
1. Identify hot paths (most frequently executed code)
2. Optimize data structures (HashMap vs List, etc.)
3. Add caching for expensive computations
4. Batch I/O operations
5. Lazy initialization for expensive objects
6. Remove unnecessary allocations
7. Profile before and after (suggest profiling approach)

Code:
```

## 9. Testability Refactoring
```
Refactor this code to make it fully testable:
1. Extract dependencies (database, APIs, file system) behind interfaces
2. Move business logic out of framework-specific code
3. Break static/global dependencies
4. Make side effects explicit
5. Use dependency injection
6. Separate pure functions from impure ones

Code:
```

## 10. API/Interface Redesign
```
Redesign this API/interface for better developer experience:
1. Consistent naming conventions
2. Intuitive parameter ordering
3. Sensible defaults (minimize required params)
4. Method chaining / fluent interface where appropriate
5. Clear error messages
6. Proper use of Optional/nullable
7. Backward compatibility strategy

Current interface:
```

## 11. Database Query Optimization
```
Refactor these database queries for performance:
1. Eliminate N+1 queries (use JOINs or batch loading)
2. Add missing indexes
3. Optimize WHERE clauses for index usage
4. Replace subqueries with JOINs where faster
5. Add proper pagination (cursor-based)
6. Use database-specific features (CTEs, window functions)
7. Connection pooling optimization

Queries:
```

## 12. Configuration Externalization
```
Refactor to externalize all configuration:
1. Extract hardcoded values to config files/env vars
2. Create a typed configuration class
3. Add validation for required config values
4. Support multiple environments (dev/staging/prod)
5. Add sensible defaults
6. Support hot-reload where possible
7. Secret management (no secrets in code/config files)

Code:
```

## 13. Async/Concurrent Code Refactoring
```
Refactor this code for proper async/concurrent execution:
1. Identify blocking operations that should be async
2. Parallelize independent operations
3. Add proper cancellation support
4. Implement backpressure for streams
5. Fix async anti-patterns (fire-and-forget, missing awaits)
6. Add proper timeout handling
7. Ensure thread safety for shared state

Code:
```

## 14. Monolith to Modular Decomposition
```
Help me decompose this monolithic code into modules:
1. Identify bounded contexts / business domains
2. Map dependencies between modules
3. Define module interfaces (public API)
4. Handle cross-cutting concerns (logging, auth, validation)
5. Plan data separation strategy
6. Create a migration roadmap (incremental, not big bang)

Codebase overview:
```

## 15. Type Safety Enhancement
```
Add comprehensive type safety to this code:
1. Add type annotations to all functions and variables
2. Replace `any`/`object` with specific types
3. Create domain types (NewType, branded types)
4. Add runtime validation at boundaries
5. Use discriminated unions for state
6. Make impossible states unrepresentable
7. Add generic types where appropriate

Code:
```

## 16. Logging & Observability Refactoring
```
Improve logging and observability:
1. Add structured logging (key-value pairs, not string interpolation)
2. Use appropriate log levels (DEBUG/INFO/WARN/ERROR)
3. Add correlation IDs for request tracing
4. Remove sensitive data from logs (PII, passwords)
5. Add performance metrics at key points
6. Add health check endpoints
7. Make debugging easier with contextual information

Code:
```

## 17. Functional Programming Refactoring
```
Refactor this imperative code to a functional style:
1. Replace mutable variables with immutable data
2. Replace loops with map/filter/reduce
3. Extract pure functions (no side effects)
4. Use function composition
5. Replace null with Option/Maybe types
6. Use pattern matching where available
7. Apply point-free style where it improves readability

Code:
```

## 18. API Versioning Refactoring
```
Add versioning to this API:
1. Choose versioning strategy (URL path/header/query param)
2. Create version-specific handlers
3. Implement backward compatibility layer
4. Add deprecation warnings
5. Document breaking vs non-breaking changes
6. Create migration guide for consumers
7. Set up version sunset timeline

API code:
```

## 19. Security Hardening Refactoring
```
Harden this code for security:
1. Input validation and sanitization
2. Output encoding (prevent XSS)
3. Parameterized queries (prevent SQL injection)
4. Authentication/authorization checks
5. Rate limiting
6. Secure headers (CORS, CSP, HSTS)
7. Secret management (no hardcoded secrets)
8. Audit logging for sensitive operations

Code:
```

## 20. Dependency Cleanup
```
Clean up dependencies in this project:
1. Identify unused dependencies (remove them)
2. Find duplicate functionality (keep one)
3. Update outdated packages (check for breaking changes)
4. Replace heavy libraries with lighter alternatives
5. Check for security vulnerabilities
6. Lock dependency versions
7. Document why each dependency is needed

Dependency file:
```

## 21. Code Documentation Refactoring
```
Add proper documentation to this code:
1. Module/file-level docstrings explaining purpose
2. Function docstrings with params, returns, raises, examples
3. Complex algorithm explanations
4. Architecture decision records (ADRs) for design choices
5. TODO/FIXME annotations for known issues
6. Type annotations as documentation
7. Usage examples in docstrings

Code:
```

## 22. State Management Refactoring (Frontend)
```
Refactor state management in this frontend application:
1. Categorize state (local/shared/server/URL)
2. Move server state to data fetching library (React Query/SWR)
3. Move URL state to router
4. Minimize global state
5. Use proper state machines for complex flows
6. Optimize re-renders
7. Add persistence where needed

Code:
```

## 23. Error Boundary Refactoring
```
Add comprehensive error boundaries and graceful degradation:
1. Component-level error boundaries (UI)
2. Service-level circuit breakers (API calls)
3. Fallback content for each error type
4. Retry mechanisms with user feedback
5. Offline support / graceful degradation
6. Error reporting to monitoring service
7. User-friendly error messages

Code:
```

## 24. Test Suite Refactoring
```
Improve this test suite:
1. Remove flaky tests (time-dependent, order-dependent)
2. Add missing edge case coverage
3. Use parameterized tests for similar test cases
4. Improve test naming (describe behavior, not implementation)
5. Extract common setup into fixtures/helpers
6. Speed up slow tests (mocking, parallel execution)
7. Add integration tests where only unit tests exist

Tests:
```

## 25. Microservice Communication Refactoring
```
Improve inter-service communication:
1. Add circuit breakers for downstream calls
2. Implement retry with exponential backoff + jitter
3. Add request/response logging with correlation IDs
4. Implement bulkhead pattern (isolate failures)
5. Add timeout configuration per service
6. Health check consumers for dependency monitoring
7. Implement fallback responses for degraded mode

Code:
```
