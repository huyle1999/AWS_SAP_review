````md
# API App for Restaurant Deploy in AWS

## Setup Project

```bash
pipenv install django djangorestframework djoser

pipenv shell

django-admin startproject LittleLemon

cd LittleLemon

python manage.py startapp LittleLemonAPI
````

## Run Project

```bash
cd LittleLemon

pipenv shell

pipenv install

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
```

## Logic

* logic for database model

---

## Migration Issue

Lúc migrate, bị hang không biết lỗi do gì.

```text
django June 15, 2026, 18:44
[2026-06-15 11:44:01 +0000] [1] [ERROR] Worker (pid:9) was sent SIGKILL! Perhaps out of memory?
b55c476d2dc94c2cb9d98cc63cb79c22 django
```

=> là do chưa migrate để nó có bảng mặc định của Django.

---

## Future Microservices Architecture

Dựa trên plan.md và kiến trúc distributed system bạn đang hướng tới, khi tách Microservices từ Monolith hiện tại, bạn sẽ có tổng cộng 7 Services (bao gồm cả API Gateway):

* API Gateway / Auth Service: Xử lý Authentication (JWT), RBAC, Rate Limiting và định tuyến request.
* Restaurant & Menu Service: Quản lý Restaurant, Category, MenuItem, Item of the Day, Search/Filter.
* Cart & Order Service: Quản lý Giỏ hàng, Đặt món, Order Status Flow, Coupon validation.
* Inventory Service: Quản lý Stock, Reserve/Release/Reduce stock (tách riêng để đảm bảo tính nhất quán cao và chịu tải độc lập).
* Payment Service: Mock Payment Gateway, Payment Status, Refund, Transaction Log.
* Notification Service: Gửi Email, SMS (Mock), In-app Notification (consume event từ Kafka).
* Analytics & Audit Service: Tổng hợp Dashboard, Revenue, Top Foods, Peak Hours + Lưu trữ Audit Log (consume event từ Kafka).

> **Lưu ý chiến lược**
>
> Trong giai đoạn đầu (Phase 1-3), bạn nên giữ Monolith Modular (tách code thành các Django Apps hoặc Service Layer rõ ràng như tôi đã hướng dẫn trước đó). Chỉ khi traffic đủ lớn hoặc team đủ đông thì mới tách vật lý thành 7 microservices này.
>
> Việc tách quá sớm khi business logic chưa ổn định sẽ tạo ra "distributed monolith" rất khó maintain.

---

## Dev vs SRE/DevOps

| Thành phần                      | Góc độ Dev (Code)                             | Góc độ SRE/DevOps (Vận hành & Kiến trúc)                                                                                                                                                                  |
| ------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Idempotency                     | Viết logic check duplicate key, atomic update | Thiết kế Retry Policy & DLQ: Nếu API không idempotent, SRE không dám bật auto-retry trên Load Balancer/Kafka Consumer. Hệ thống sẽ không thể self-heal khi có network glitch.                             |
| Thread Safety                   | Dùng lock, atomic transaction trong code      | Tuning Gunicorn & HPA: SRE cần biết app có thread-safe không để chọn worker class (sync vs gthread vs gevent), set số workers/threads đúng, và dự đoán chính xác resource usage khi scale ngang.          |
| Structured Logging + Request ID | Thêm middleware gắn log                       | Observability Pipeline: SRE thiết kế log aggregation (ELK/Loki), trace correlation (OTEL). Không có Request ID → không thể debug incident lúc 3AM khi traffic đi qua 5 service.                           |
| Health Check                    | Viết view /health/live, /health/ready         | K8s Probe Config: SRE quyết định initialDelaySeconds, periodSeconds, failureThreshold. Config sai → pod restart loop hoặc nhận traffic khi chưa sẵn sàng → downtime.                                      |
| Graceful Shutdown               | Xử lý signal SIGTERM trong code               | Zero-Downtime Deploy: SRE config terminationGracePeriodSeconds trong K8s, preStop hook. Không có → mỗi lần deploy mất request đang xử lý → SLA vi phạm.                                                   |
| DB Connection Pool              | Set CONN_MAX_AGE trong settings               | Capacity Planning & RDS Tuning: SRE tính toán max connections = workers × pool_size, monitor connection saturation, tune RDS/ElastiCache parameters. Pool sai → DB overload trước khi app chạm CPU limit. |

---

## SAP / AZ-305

| Thành phần         | Cần biết cho SAP/AZ-305                                             | KHÔNG cần biết                                        |
| ------------------ | ------------------------------------------------------------------- | ----------------------------------------------------- |
| Idempotency        | Thiết kế retry policy, DLQ, eventual consistency trên Cloud         | Cách viết middleware check duplicate key trong Django |
| Thread Safety      | Chọn instance type, tuning auto-scaling, capacity planning          | Cách dùng select_for_update hay threading.local()     |
| Structured Logging | Thiết kế log pipeline (CloudWatch/Azure Monitor), trace correlation | Cách viết Python logging formatter                    |
| Health Check       | Config ALB/App Gateway probes, zero-downtime deploy strategy        | Cách viết /health/live endpoint trong Django          |
| Graceful Shutdown  | Set termination grace period, preStop hook, rolling update          | Cách xử lý SIGTERM signal trong code                  |
| DB Connection Pool | Tune RDS/Azure DB max connections, sizing instance                  | Cách set CONN_MAX_AGE trong settings.py               |

---

## PostgreSQL

```bash
sudo docker exec -it postgres psql -U django restaurant
```

```sql
UPDATE auth_user
SET password = 'fAkEpAs5w0rd'
WHERE username = 'huy';
```

---

## Docker

```bash
docker build -t huyle99/littlelemon-api:v2 .
```

```bash
docker run -d \
  --name littlelemon-test \
  --network bridge \
  -p 8001:8000 \
  huyle99/littlelemon-api:v2
```

```bash
docker network connect littlelemon-net littlelemon-test
```

```
```
