# HƯỚNG DẪN TEST API PHASE 1 - LITTLE LEMON

## 1. Chuẩn bị
- Tool: Postman / Insomnia
- Base URL: `http://localhost:8000`
- Tạo sẵn dữ liệu qua Admin:
  - 1 Category, 2 MenuItem (stock=10)
  - 1 Coupon (code=TEST10, discount=10%, active)
  - 3 Users: customer1, manager1, delivery1 (gán Group tương ứng)

## 2. Auth & RBAC
| Step | Method | Endpoint | Body/Header | Expected | Verify DB |
|------|--------|----------|-------------|----------|-----------|
| 1 | POST | `/auth/token/login/` | `{username, password}` | 200 + auth_token | - |
| 2 | GET | `/api/menu-items` | Header: `Token <token>` | 200 list menu | - |
| 3 | POST | `/api/menu-items` | Token customer | 403 Forbidden | Không tạo mới |
| 4 | POST | `/api/menu-items` | Token manager | 201 Created | MenuItem mới trong Admin |

## 3. Cart Flow
| Step | Method | Endpoint | Body | Expected | Verify DB |
|------|--------|----------|------|----------|-----------|
| 5 | POST | `/api/cart/menu-items` | `{menuitem:1, quantity:2}` | 201 | Cart có 1 item, qty=2 |
| 6 | POST | `/api/cart/menu-items` | `{menuitem:1, quantity:9}` | 400 Insufficient stock | Stock giữ nguyên=10 |
| 7 | GET | `/api/cart/menu-items` | - | 200 list cart items | - |
| 8 | DELETE | `/api/cart/menu-items` | - | 204 | Cart rỗng |

## 4. Order + Inventory + Coupon (Atomic)
| Step | Method | Endpoint | Body | Expected | Verify DB |
|------|--------|----------|------|----------|-----------|
| 9 | Add cart lại | POST `/api/cart/menu-items` | `{menuitem:1, qty:3}` | 201 | Cart có 3 items |
| 10 | Place order | POST `/api/orders` | `{coupon_code:"TEST10"}` | 201 + order_id | ✅ Order created<br>✅ Stock giảm 3 (còn 7)<br>✅ InventoryLog action=reserve<br>✅ Cart rỗng<br>✅ AuditLog action=create_order |
| 11 | Place order hết stock | Add cart 8 → POST `/api/orders` | - | 400 Insufficient stock | ✅ Stock vẫn=7 (rollback)<br>✅ KHÔNG có Order mới<br>✅ KHÔNG có InventoryLog mới |
| 12 | Get order detail | GET `/api/orders/<uuid>` | - | 200 + items + payment_status | OrderItem.unit_price = snapshot giá |

## 5. Order Status Flow
| Step | Method | Endpoint | Body | Expected | Verify DB |
|------|--------|----------|------|----------|-----------|
| 13 | Update status | PATCH `/api/orders` | `{id:<uuid>, status:"preparing"}` | 200 | Order.status = preparing |
| 14 | Invalid transition | PATCH `/api/orders` | `{id:<uuid>, status:"completed"}` | 400 Invalid transition | Status giữ nguyên |
| 15 | Assign delivery | PATCH `/api/orders` | `{id:<uuid>, delivery_crew:<id>}` | 200 | Order.delivery_crew updated |

## 6. Kiểm tra Data sau Test (Admin Panel)
- **MenuItem**: Stock giảm đúng số lượng order thành công
- **InventoryLog**: Mỗi order thành công = 1 log reserve; mỗi order fail = KHÔNG có log
- **Order**: Status đúng, total_price đã trừ coupon
- **Cart**: Rỗng sau khi place order thành công
- **AuditLog**: Ghi nhận create_order, update_order_status
- **Coupon**: used_count tăng sau mỗi lần apply thành công

## 7. Checklist Pass/Fail
- [ ] Customer KHÔNG thể tạo MenuItem
- [ ] Manager CÓ THỂ tạo MenuItem
- [ ] Add to cart validate stock
- [ ] Place order trừ stock atomic
- [ ] Coupon giảm giá đúng %
- [ ] Order fail KHÔNG trừ stock (rollback)
- [ ] Cart clear sau order success
- [ ] InventoryLog ghi đúng
- [ ] AuditLog ghi đúng
- [ ] Order status transition validate đúng