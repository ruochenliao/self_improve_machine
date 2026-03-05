# Database Prompts — 25 Templates

---

## 1. Schema Design from Requirements
```
Design a database schema from these business requirements:
- Database: [PostgreSQL/MySQL/MongoDB]
- Include: Tables/collections, columns with types, primary keys, foreign keys, indexes, constraints, ER diagram (mermaid), seed data, common query patterns, migration script.
Requirements:
```

## 2. Query Optimization
```
Optimize this SQL query for performance:
1. Analyze the execution plan (EXPLAIN ANALYZE)
2. Suggest missing indexes
3. Rewrite subqueries as JOINs where beneficial
4. Use CTEs for readability
5. Apply window functions where appropriate
6. Estimate improvement in execution time
Table schemas: [provide]
Query:
```

## 3. Migration Script Generator
```
Generate a safe database migration:
- From: [current schema]
- To: [target schema]
Include: Up migration, down migration, data transformation, zero-downtime strategy, verification queries, rollback plan.
Changes:
```

## 4. Database Performance Audit
```
Audit this database setup for performance:
Check: Slow queries, missing indexes, table bloat, connection pool sizing, replication lag, lock contention, query plan regressions, cache hit ratio.
Schema + sample queries:
```

## 5. NoSQL Data Modeling
```
Design a NoSQL data model for [MongoDB/DynamoDB/Cassandra]:
Consider: Access patterns first, denormalization strategy, partition key design, embedding vs referencing, consistency requirements, query performance.
Use case:
```

## 6-25: Additional Templates
Includes: Data partitioning strategy, backup & recovery plan, replication setup, connection pool optimization, query builder patterns, database security hardening, time-series data modeling, full-text search setup, data archival strategy, ETL pipeline design, database monitoring setup, multi-tenant data isolation, read replica configuration, schema versioning strategy, database comparison/selection guide, stored procedure refactoring, data validation constraints, geographic data handling, JSON/JSONB usage patterns, database load testing.
