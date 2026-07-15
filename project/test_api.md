# 🚀 LittleLemon API - SRE & DevOps Testing Guide

Tài liệu này giúp SRE/DevOps nắm vững **Luồng nghiệp vụ cốt lõi (Core Business Flow)** trước khi triển khai Platform. 
Mục tiêu: Hiểu request đi qua những đâu, tác động gì đến DB/Cache, và đâu là điểm nóng (hotspot) cần monitor khi scale.

---

## 📋 1. Chuẩn bị Data Mẫu (Setup 1 lần)
Trước khi test, vào Django Admin (`/admin/`) tạo sẵn:
1. **Category**: `Main Course`
2. **MenuItem**: `Pizza` | Price: `10.00` | **Stock: `10`** (Quan trọng: Để test Inventory Lock)
3. **User**: `customer1` | Password: `test123`
4. **Coupon**: `SUMMER10` | Discount: `10%` | Active

---

## 🔄 2. Core Business Flow (The Happy Path)

Đây là luồng request quan trọng nhất. Mọi thiết kế K8s HPA, Redis Cache, hay Kafka Events sau này đều xoay quanh luồng này.

| Step | Endpoint | Method | Mục đích | 🚨 SRE Perspective (Điểm nóng & Rủi ro) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `/auth/token/login/` | POST | Login, lấy Auth Token | **High Traffic**. Cần Rate Limiting để chống Brute-force. Candidate cho Redis Cache session. |
| **2** | `/api/menu-items/` | GET | Xem danh sách món ăn | **Read-Heavy**. Endpoint này sẽ được Cache (Redis) ở Phase 3 để giảm tải cho PostgreSQL. |
| **3** | `/api/cart/menu-items/` | POST | Thêm món vào giỏ hàng | **Write DB**. Cần validate Stock sớm để chặn request rác đi sâu vào hệ thống. |
| **4** | `/api/orders/` | POST | **Chốt đơn (Place Order)** | 🔥 **CRITICAL HOTSPOT**.<br>- Atomic Transaction (Reserve Stock -> Create Order -> Payment).<br>- **Rủi ro**: Race condition (Oversell) khi traffic cao.<br>- **Monitor**: P99 Latency, DB Lock wait time. |
| **5** | `/api/orders/` | PATCH | Update Status (Preparing/Delivering) | **State Machine**. Trigger Notification/Kafka Events sau này. |

---

## 🛠️ 3. Quick Test Commands (cURL)

Dùng terminal để test nhanh, không cần Postman. Giả sử server chạy ở `http://localhost:8000`.

### Step 1: Login lấy Token
```bash
curl -X POST http://localhost:8000/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "customer1", "password": "test123"}'
# 👉 Copy chuỗi "auth_token" từ response, gán vào biến TOKEN
export TOKEN="your_token_here"
