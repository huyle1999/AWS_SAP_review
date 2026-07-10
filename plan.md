# Restaurant Platform Roadmap
> Goal: Build a Production-Grade Distributed System for SRE / AWS SAA Pro / AZ-305

---

# Phase 0 - Existing Project

Current Stack

- Django REST Framework
- PostgreSQL
- JWT Authentication
- Restaurant CRUD
- Menu CRUD

---

# Phase 1 - Complete Business Domain

## User & Access

- User Registration
- Login
- JWT Authentication
- Role-Based Access Control

Roles

- Admin
- Manager
- Delivery Crew
- Customer

Admin

- Assign Manager
- Remove Manager

Manager

- Assign Delivery Crew
- Manage Menu
- Manage Categories
- Update Item of the Day

---

## Restaurant

- Restaurant CRUD
- Restaurant Images
- Restaurant Status (Open / Closed)
- Restaurant Working Hours

---

## Category

- CRUD Category

---

## Menu

- CRUD Menu
- Menu Images
- Item of the Day
- Search Menu
- Filter Category
- Sort by Price
- Pagination

---

## Customer

- Browse Restaurants
- Browse Categories
- Browse Menu
- Restaurant Detail
- Menu Detail

---

## Cart

- Add Item
- Update Quantity
- Remove Item
- Clear Cart

---

## Orders

- Place Order
- Order Detail
- Order History
- Order Status

Order Status

- Pending
- Preparing
- Delivering
- Completed
- Cancelled

---

## Inventory ⭐

Inventory per Menu

- Stock
- Reserve Stock
- Release Stock
- Reduce Stock

---

## Payment ⭐

Mock Payment Gateway

Payment Status

- Pending
- Paid
- Failed
- Refunded

---

## Coupon ⭐

- Create Coupon
- Apply Coupon
- Expiration
- Discount Validation

---

## Notification ⭐

Notification Types

- Email
- SMS (Mock)
- In-App Notification

Triggers

- Order Created
- Order Delivered
- Payment Success

---

## Audit Log ⭐

Record

- Login
- Order
- Payment
- Inventory
- Admin Actions
- Menu Update

---

## Analytics ⭐

Dashboard

- Total Orders
- Revenue
- Top Foods
- Popular Restaurants
- Peak Hours

---

# Phase 2 - Production Ready

- Docker
- Docker Compose
- Nginx
- Gunicorn

Implement

- Health Check
- Readiness Probe
- Liveness Probe
- Graceful Shutdown
- Environment Variables
- Secret Management

---

# Phase 3 - Redis

Introduce

- Redis

Implement

- Restaurant Cache
- Menu Cache
- Category Cache
- User Cache
- Rate Limiting
- Distributed Lock

Concepts

- Cache Aside
- TTL
- Cache Invalidation

---

# Phase 4 - Kafka

Introduce

- Kafka

Events

- OrderCreated
- PaymentCompleted
- InventoryReserved
- InventoryReleased
- NotificationRequested
- AuditCreated

Consumers

- Inventory Consumer
- Notification Consumer
- Audit Consumer
- Analytics Consumer

Concepts

- Event Driven
- Producer
- Consumer Group
- Retry
- Dead Letter Queue
- Idempotency
- Eventual Consistency

---

# Phase 5 - Object Storage

Introduce

- MinIO

Later

- AWS S3
- Azure Blob

Store

- Restaurant Images
- Menu Images
- User Avatar

Concepts

- Object Storage
- Presigned URL

---

# Phase 6 - Observability

Metrics

- Prometheus

Logging

- ELK

Dashboard

- Grafana

Implement

- HTTP Metrics
- Database Metrics
- Redis Metrics
- Kafka Metrics
- Business Metrics

Structured Logging

- Trace ID
- Request ID
- User ID
- Latency
- Status Code

---

# Phase 7 - Performance

Implement

- k6
- Connection Pool
- PostgreSQL Optimization
- Redis Benchmark
- Gunicorn Tuning

Measure

- Throughput
- Latency
- P95
- P99
- Cache Hit Ratio

---

# Phase 8 - Reliability

Implement

- Retry
- Timeout
- Circuit Breaker
- Exponential Backoff
- Dead Letter Queue
- Graceful Shutdown

---

# Phase 9 - Kubernetes

Deploy

- Django
- PostgreSQL
- Redis
- Kafka
- MinIO

Implement

- Helm
- ConfigMap
- Secret
- HPA
- Ingress
- Persistent Volume
- Pod Disruption Budget

---

# Phase 10 - GitOps

- GitHub Actions
- ArgoCD

Environment

- Development
- Staging
- Production

---

# Phase 11 - AWS

Replace Infrastructure

- EKS
- RDS PostgreSQL
- ElastiCache Redis
- Amazon MSK
- Amazon S3
- ALB
- ECR

Business Code

No Change

---

# Phase 12 - Azure

Replace Infrastructure

- AKS
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Blob Storage
- Application Gateway

Business Code

No Change

---

# Final Architecture

                         Client

                            │

                     Load Balancer

                            │

                         Nginx

                            │

                     Django REST API

        ┌──────────────┼──────────────┐

   PostgreSQL        Redis         Kafka

                                        │

        ┌─────────────┬─────────────┬──────────────┐

    Inventory      Notification      Audit      Analytics

                            │

                          MinIO

                            │

      Prometheus      ELK       Grafana

                            │

                       Kubernetes

                            │

             On-Prem → AWS → Azure
