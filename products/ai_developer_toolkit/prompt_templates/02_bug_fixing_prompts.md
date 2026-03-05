# Bug Fixing Prompts — 25 Templates for Rapid Debugging

> Stop wasting hours debugging. Let AI pinpoint the issue in seconds.

---

## 1. Systematic Bug Diagnosis

```
You are a senior debugger. I have a bug in my code. Help me systematically diagnose it.

**Symptoms**: [Describe what's happening]
**Expected behavior**: [What should happen]
**Environment**: [OS, language version, framework version]

Apply this debugging framework:
1. Reproduce — Identify the minimal reproduction steps
2. Isolate — Narrow down the component causing the issue
3. Identify — Find the root cause (not just symptoms)
4. Fix — Provide a corrected code snippet
5. Verify — Suggest test cases to confirm the fix
6. Prevent — Recommend changes to prevent similar bugs

Code:
```

---

## 2. Error Stack Trace Analysis

```
Analyze this error stack trace and:

1. Identify the root cause (not just the symptom)
2. Explain WHY this error occurred in plain English
3. Provide the exact fix with code
4. Suggest defensive coding to prevent recurrence
5. If it's a third-party library issue, suggest workarounds

Stack trace:
```

---

## 3. Race Condition Detector

```
I suspect a race condition in this code. Please:

1. Identify all shared mutable state
2. Map out the concurrent access patterns
3. Find the specific race condition(s)
4. Explain the failure scenario step-by-step (thread interleaving)
5. Provide a thread-safe fix using the minimal synchronization needed
6. Suggest a test that would catch this race condition

Code:
```

---

## 4. Memory Leak Investigation

```
Help me find memory leaks in this code:

1. Identify objects that are created but never freed
2. Find circular references preventing garbage collection
3. Detect event listeners/subscriptions that aren't cleaned up
4. Check for growing caches without eviction
5. Find closures capturing more than they need
6. Provide a fix and memory profiling strategy

Code:
```

---

## 5. "It Works Locally But Fails in Production"

```
This code works in my local development environment but fails in production. Help me diagnose:

1. Environment differences — Config, env vars, file paths
2. Data differences — Volume, encoding, edge cases
3. Timing differences — Network latency, timeouts, race conditions
4. Permission differences — File system, network, API access
5. Dependency differences — Version mismatches, missing packages
6. Resource differences — Memory limits, CPU, disk space

Local environment: [describe]
Production environment: [describe]
Error in production: [describe]

Code:
```

---

## 6. Null/Undefined Reference Fix

```
I'm getting null/undefined reference errors. For each potential null reference in this code:

1. Identify the exact location where null/undefined can occur
2. Trace back to WHERE the null value originates
3. Determine if the null is valid (expected) or a bug (unexpected)
4. If valid: Add proper null handling (Optional, nullable types, guards)
5. If bug: Fix the source of the null value
6. Add type safety to prevent future null issues

Code:
```

---

## 7. Infinite Loop Detector

```
This code appears to hang/run forever. Help me find the infinite loop:

1. Trace each loop's termination condition
2. Check if the loop variable is actually progressing toward termination
3. Check for mutation of the collection being iterated
4. Check for recursive calls without proper base case
5. Provide the fix and add safeguards (max iterations, timeouts)

Code:
```

---

## 8. API Integration Bug Fix

```
My API integration is failing. Debug this:

1. Request formation — Headers, body, query params, content-type
2. Authentication — Token format, expiry, scopes
3. Response handling — Status codes, error parsing, timeout handling
4. Rate limiting — Retry logic, backoff strategy
5. Data serialization — JSON encoding/decoding, date formats, encoding

Expected API behavior: [describe]
Actual behavior: [describe]
API documentation reference: [link if available]

Code:
```

---

## 9. Database Query Bug Fix

```
My database query is returning wrong/no results. Debug:

1. Query logic — JOIN conditions, WHERE clauses, GROUP BY
2. Data types — Implicit casting, string vs integer comparison
3. NULL handling — NULL in comparisons, COALESCE usage
4. Index usage — Is the query using expected indexes?
5. Transaction isolation — Dirty reads, phantom reads
6. Provide the corrected query with EXPLAIN analysis suggestion

Expected results: [describe]
Actual results: [describe]

Query/Code:
```

---

## 10. Authentication/Authorization Bug

```
Users are experiencing authentication/authorization issues. Debug:

1. Token lifecycle — Generation, validation, refresh, expiry
2. Session management — Storage, invalidation, concurrency
3. Permission checks — Role hierarchy, resource ownership
4. CORS/Cookie issues — SameSite, secure flag, domain
5. OAuth flow — Redirect URIs, scopes, state parameter
6. Timing — Token refresh race conditions

Error description: [describe]

Code:
```

---

## 11. CSS/Layout Bug Fix

```
The UI layout is broken. Help me fix:

1. Box model issues — Margin collapse, padding vs border-box
2. Flexbox/Grid — Alignment, wrapping, ordering
3. Positioning — Stacking context, z-index, overflow
4. Responsive — Breakpoint issues, viewport units
5. Browser compatibility — Vendor prefixes, feature support
6. Provide the corrected CSS with comments

Expected layout: [describe or screenshot URL]
Actual layout: [describe]

CSS/HTML:
```

---

## 12. Async/Await Bug Fix

```
My async code isn't behaving correctly. Debug:

1. Missing awaits — Promises resolving out of order
2. Error handling — Unhandled rejections, try/catch placement
3. Parallel vs sequential — Promise.all vs sequential awaits
4. Deadlocks — Awaiting in wrong order
5. Memory leaks — Unresolved promises accumulating
6. Cancellation — AbortController usage

Expected behavior: [describe]
Actual behavior: [describe]

Code:
```

---

## 13. Regex Bug Fix

```
My regular expression isn't matching correctly. Help me:

1. Explain what my current regex actually matches (step by step)
2. Identify why it fails for my test cases
3. Provide the corrected regex with explanation
4. Show test cases (match and non-match)
5. Suggest if regex is the right tool or if parsing would be better

Current regex: [your regex]
Should match: [examples]
Should NOT match: [examples]
Currently failing on: [examples]
```

---

## 14. Encoding/Character Bug Fix

```
I'm having encoding/character issues (mojibake, garbled text, wrong characters). Debug:

1. Identify the encoding chain (source → processing → output)
2. Find where encoding conversion fails
3. Check for BOM (Byte Order Mark) issues
4. Check database column charset/collation
5. Fix HTTP Content-Type headers
6. Provide the corrected code with explicit encoding handling

Input text: [sample]
Expected output: [sample]
Actual output: [sample]

Code:
```

---

## 15. Date/Time Bug Fix

```
Date/time calculations are wrong in my code. Debug:

1. Timezone handling — UTC vs local, DST transitions
2. Date parsing — Format strings, locale-specific parsing
3. Date arithmetic — Month/year boundaries, leap years
4. Comparison — Timestamp precision, timezone-aware comparison
5. Serialization — ISO 8601, Unix timestamps, JSON date format
6. Provide corrected code using proper date/time libraries

Expected: [describe]
Actual: [describe]

Code:
```

---

## 16. File I/O Bug Fix

```
File operations are failing or producing wrong results. Debug:

1. Path issues — Relative vs absolute, OS-specific separators
2. Permissions — Read/write/execute, directory permissions
3. Encoding — UTF-8, BOM, line endings (CRLF vs LF)
4. Concurrent access — File locking, atomic operations
5. Resource leaks — File handles not closed
6. Large files — Memory issues, streaming needed

Error: [describe]

Code:
```

---

## 17. Network/Socket Bug Fix

```
Network communication is failing. Debug:

1. Connection — DNS resolution, port availability, firewall
2. Protocol — HTTP/HTTPS, WebSocket handshake, TLS version
3. Timeout — Connection vs read timeout, keep-alive
4. Proxy — Proxy configuration, tunnel mode
5. Data — Chunked transfer, content-length mismatch
6. Provide the fix and add proper error handling

Error: [describe]

Code:
```

---

## 18. State Management Bug (React/Vue/Angular)

```
My frontend app's state is inconsistent. Debug:

1. State mutation — Direct mutation vs immutable updates
2. State flow — Props drilling, context, store dispatch
3. Re-render triggers — What's causing unnecessary re-renders?
4. Stale closure — Callbacks capturing old state
5. Race conditions — Multiple concurrent state updates
6. Hydration mismatch — SSR vs client state

Steps to reproduce: [describe]

Code:
```

---

## 19. Build/Compilation Bug Fix

```
My project won't build. Debug this build error:

1. Dependency resolution — Version conflicts, peer deps
2. TypeScript/Type errors — Generic constraints, module resolution
3. Webpack/Vite config — Loaders, plugins, aliases
4. Environment — Node version, PATH, env variables
5. Circular dependencies — Import cycle detection
6. Provide step-by-step fix

Build error output:
```

---

## 20. Performance Bug (Slow Code)

```
This code is running too slowly. Profile and fix:

1. Algorithmic complexity — What's the current Big-O? Can it be reduced?
2. Hot path identification — Which lines execute most frequently?
3. I/O bottlenecks — Blocking calls, missing batching
4. Caching opportunities — What can be memoized/cached?
5. Data structure choice — Is the right data structure being used?
6. Provide optimized code with before/after complexity analysis

Performance expectation: [e.g., should handle 10K items in <1s]
Current performance: [e.g., takes 30s for 10K items]

Code:
```

---

## 21. Docker/Container Bug Fix

```
My Docker container isn't working correctly. Debug:

1. Build failures — Missing dependencies, wrong base image
2. Runtime issues — Entrypoint, CMD, environment variables
3. Networking — Port mapping, DNS, inter-container communication
4. Volume — Mount paths, permissions, file visibility
5. Resource — OOM kills, CPU throttling
6. Logs — Container log analysis

Docker error/behavior: [describe]

Dockerfile/docker-compose:
```

---

## 22. Git Conflict Resolution

```
I have a merge conflict. Help me resolve it:

1. Understand both sides — What was the intent of each change?
2. Identify the correct resolution — Which changes to keep?
3. Check for semantic conflicts — Code compiles but logic is wrong?
4. Verify integration — Do the merged changes work together?
5. Suggest test cases to verify the merge

Conflict markers:
```

---

## 23. Webhook/Event Handler Bug

```
My webhook/event handler is misbehaving. Debug:

1. Payload parsing — Content-type, JSON structure, field names
2. Signature verification — HMAC, timing attacks
3. Idempotency — Handling duplicate events
4. Ordering — Out-of-order event handling
5. Timeout — Processing within webhook timeout window
6. Retry handling — Returning proper status codes

Expected events: [describe]
Actual behavior: [describe]

Code:
```

---

## 24. Caching Bug Fix

```
My caching layer is causing issues (stale data, cache stampede, inconsistency). Debug:

1. Invalidation — When and how are cache entries invalidated?
2. TTL — Is the TTL appropriate for the data's change frequency?
3. Cache stampede — Multiple processes rebuilding cache simultaneously
4. Serialization — Data corruption during cache serialization
5. Key design — Are cache keys unique and deterministic?
6. Consistency — Cache vs source of truth synchronization

Expected: [describe]
Actual: [describe]

Code:
```

---

## 25. "The Bug That Only Happens Sometimes" (Intermittent Bug)

```
I have an intermittent bug that's hard to reproduce. Help me:

1. Identify non-deterministic factors:
   - Timing/concurrency
   - External service availability
   - Data-dependent paths
   - Resource limits (memory, connections)
   - Environment state (caches, temp files)

2. Create a reproduction strategy:
   - Stress testing approach
   - Logging instrumentation to add
   - Monitoring alerts to set up

3. Based on the code, what are the MOST LIKELY intermittent failure scenarios?

4. Provide defensive coding fixes for each scenario.

Bug description: [what happens, how often, any patterns]
Environment: [production, staging, load level]

Code:
```

---

## Debugging Workflow Tips

### The 5-Step Debugging Framework

1. **Reproduce** — Can you make it fail consistently?
2. **Isolate** — What's the smallest code that still fails?
3. **Identify** — What's the root cause (not symptom)?
4. **Fix** — Change the minimum necessary code
5. **Verify** — Does the fix work? Did it break anything else?

### When to Use Which Template

| Situation | Template # |
|-----------|-----------|
| Unknown error, need systematic approach | #1 |
| Have a stack trace | #2 |
| Inconsistent/random failures | #3, #25 |
| App getting slower over time | #4 |
| Works locally, fails in prod | #5 |
| Null reference / undefined | #6 |
| App freezes/hangs | #7 |
| Third-party API issues | #8 |
| Wrong query results | #9 |
| Login/permission problems | #10 |
