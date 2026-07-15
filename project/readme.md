# Little Lemon Restaurant API

REST API cho hệ thống quản lý nhà hàng, được xây dựng bằng **Django REST Framework** và hướng tới triển khai trên **AWS** theo lộ trình từ **Monolith Modular** đến **Microservices**.

---

# 1. Khởi tạo Project

## Cài đặt Pipenv

```bash
pipenv install django djangorestframework djoser
pipenv shell
```

## Tạo Project

```bash
django-admin startproject LittleLemon
cd LittleLemon
python manage.py startapp LittleLemonAPI
```

## Chạy project

```bash
pipenv shell

python manage.py makemigrations
python manage.py migrate

python manage.py runserver
```

---

# 2. Database Models

Thiết kế database sẽ bao gồm:

- User (Django Auth)
- Restaurant
- Category
- MenuItem
- Cart
- Order
- OrderItem
- Coupon
- Payment
- Inventory

Business logic sẽ được chia theo module thay vì để toàn bộ trong `views.py`.

---

# 3. Lỗi Migration

Nếu container Django bị dừng với log:

```text
June 15, 2026, 18:44

[ERROR] Worker (pid:9) was sent SIGKILL!
Perhaps out of memory?
```

Điều này **không hẳn do Django lỗi**.

Nếu đây là lần chạy đầu tiên và chưa migrate database thì Django chưa có các bảng mặc định như:

- auth_user
- django_session
- django_content_type
- django_admin_log

Hãy chạy:

```bash
python manage.py makemigrations

python manage.py migrate
```

Nếu deploy bằng Docker:

```bash
docker exec -it littlelemon python manage.py migrate
```

sau đó mới start Gunicorn.

---

# 4. Docker Commands

Build Image

```bash
docker build -t huyle99/littlelemon-api:v2 .
```

Run Container

```bash
docker run -d \
    --name littlelemon-test \
    --network bridge \
    -p 8001:8000 \
    huyle99/littlelemon-api:v2
```

Connect vào network khác

```bash
docker network connect littlelemon-net littlelemon-test
```

---

# 5. PostgreSQL

Đăng nhập PostgreSQL

```bash
sudo docker exec -it postgres \
psql -U django restaurant
```

Đổi password user

```sql
UPDATE auth_user
SET password='fAkEpAs5w0rd'
WHERE username='huy';
```

---

# 6. Kiến trúc hiện tại

Trong giai đoạn đầu dự án sử dụng:

```
Django Modular Monolith
```

Ví dụ:

```
LittleLemonAPI

├── restaurant
├── menu
├── cart
├── order
├── payment
├── inventory
├── notification
└── analytics
```

Mỗi module có:

- models
- serializers
- services
- repositories
- views
- urls

Không viết business logic trực tiếp trong View.

---

# 7. Lộ trình Microservices

Sau khi business ổn định mới tách thành 7 services.

## 1. API Gateway / Auth Service

Chức năng

- JWT Authentication
- RBAC
- Rate Limiting
- API Routing

---

## 2. Restaurant & Menu Service

Quản lý

- Restaurant
- Category
- Menu
- Search
- Filter
- Item of the Day

---

## 3. Cart & Order Service

Quản lý

- Cart
- Checkout
- Order
- Coupon Validation
- Order Status

---

## 4. Inventory Service

Quản lý

- Stock
- Reserve Stock
- Release Stock
- Reduce Stock

Tách riêng để đảm bảo:

- High Consistency
- Independent Scaling

---

## 5. Payment Service

Bao gồm

- Mock Payment Gateway
- Transaction
- Refund
- Payment Status

---

## 6. Notification Service

Consume Kafka Event để gửi

- Email
- SMS (Mock)
- In-app Notification

---

## 7. Analytics & Audit Service

Consume Kafka Event

Bao gồm

- Dashboard
- Revenue
- Peak Hours
- Top Foods
- Audit Log

---

# 8. Chiến lược phát triển

## Phase 1

Monolith Modular

```
Single Database
Single Deployment
```

---

## Phase 2

Bắt đầu dùng

- Redis
- RabbitMQ hoặc Kafka
- Background Worker

---

## Phase 3

Deploy lên Kubernetes

- HPA
- Ingress
- Prometheus
- Grafana
- ELK

---

## Phase 4

Tách thành Microservices

Không nên tách quá sớm.

Nếu business logic chưa ổn định sẽ tạo ra:

> Distributed Monolith

Khó maintain hơn Monolith.

---

# 9. Những thứ Dev cần biết và SRE cần biết

| Thành phần | Góc độ Developer | Góc độ SRE / Platform |
|------------|------------------|------------------------|
| Idempotency | Viết duplicate check, atomic update | Thiết kế Retry Policy, DLQ, đảm bảo retry an toàn |
| Thread Safety | Lock, transaction, atomic operation | Chọn worker model, HPA, capacity planning |
| Structured Logging | Logging middleware, Request ID | ELK/Loki, OpenTelemetry, trace correlation |
| Health Check | `/health/live`, `/health/ready` | Readiness Probe, Liveness Probe |
| Graceful Shutdown | Xử lý SIGTERM | Rolling Update, PreStop Hook, Zero Downtime |
| DB Connection Pool | `CONN_MAX_AGE`, connection reuse | RDS sizing, max connections, pool tuning |

---

# 10. Nếu theo hướng SAP / Solution Architect / AZ-305

| Thành phần | Cần biết | Không cần biết |
|------------|----------|----------------|
| Idempotency | Retry Policy, DLQ, Eventual Consistency | Middleware duplicate check |
| Thread Safety | Capacity Planning, Scaling Strategy | `select_for_update()` |
| Structured Logging | CloudWatch, Azure Monitor, OTEL | Python logging formatter |
| Health Check | ALB Probe, App Gateway Probe | Code endpoint `/health/live` |
| Graceful Shutdown | Rolling Update, Termination Grace Period | Signal handling trong Django |
| DB Connection Pool | RDS/Azure DB sizing | `CONN_MAX_AGE` trong `settings.py` |

---

# 11. Kiến thức SRE quan trọng

Một SRE không nhất thiết phải viết business logic, nhưng cần hiểu các đặc tính của ứng dụng để vận hành đúng.

Các chủ đề quan trọng gồm:

- Idempotency
- Retry Policy
- Dead Letter Queue (DLQ)
- Eventual Consistency
- Thread Safety
- Request ID
- Structured Logging
- Health Check
- Readiness Probe
- Liveness Probe
- Graceful Shutdown
- SIGTERM
- Zero Downtime Deployment
- Database Connection Pool
- Capacity Planning
- Resource Sizing

Đây là những kiến thức ảnh hưởng trực tiếp đến:

- Availability
- Reliability
- Scalability
- Observability
- SLA/SLO
- Incident Response
