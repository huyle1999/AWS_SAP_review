APi app for restaurant deploy in aws
pipenv install django djangorestframework djoser
pipenv shell
django-admin startproject LittleLemon
cd LittleLemon
python manage.py startapp LittleLemonAPI


cd LittleLemon
pipenv shell
pipenv install
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

logic for database model


luc migrate , bi hang ko biet loi do gi 
django June 15, 2026, 18:44 [2026-06-15 11:44:01 +0000] [1] [ERROR] Worker (pid:9) was sent SIGKILL! Perhaps out of memory? b55c476d2dc94c2cb9d98cc63cb79c22 django
=> la do chua migrate de no co bang mac dinh cua django

Dựa trên plan.md và kiến trúc distributed system bạn đang hướng tới, khi tách Microservices từ Monolith hiện tại, bạn sẽ có tổng cộng 7 Services (bao gồm cả API Gateway):
API Gateway / Auth Service: Xử lý Authentication (JWT), RBAC, Rate Limiting và định tuyến request.
Restaurant & Menu Service: Quản lý Restaurant, Category, MenuItem, Item of the Day, Search/Filter.
Cart & Order Service: Quản lý Giỏ hàng, Đặt món, Order Status Flow, Coupon validation.
Inventory Service: Quản lý Stock, Reserve/Release/Reduce stock (tách riêng để đảm bảo tính nhất quán cao và chịu tải độc lập).
Payment Service: Mock Payment Gateway, Payment Status, Refund, Transaction Log.
Notification Service: Gửi Email, SMS (Mock), In-app Notification (consume event từ Kafka).
Analytics & Audit Service: Tổng hợp Dashboard, Revenue, Top Foods, Peak Hours + Lưu trữ Audit Log (consume event từ Kafka).
Lưu ý chiến lược: Trong giai đoạn đầu (Phase 1-3), bạn nên giữ Monolith Modular (tách code thành các Django Apps hoặc Service Layer rõ ràng như tôi đã hướng dẫn trước đó). Chỉ khi traffic đủ lớn hoặc team đủ đông thì mới tách vật lý thành 7 microservices này. Việc tách quá sớm khi business logic chưa ổn định sẽ tạo ra "distributed monolith" rất khó maintain.