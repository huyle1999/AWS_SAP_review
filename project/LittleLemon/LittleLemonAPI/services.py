from django.db import transaction
from django.utils import timezone
from .models import MenuItem, InventoryLog, Order, OrderItem, Cart, Payment, Coupon, AuditLog, Notification
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    @staticmethod
    @transaction.atomic
    def reserve_stock(items_data: list[dict], order=None):
        """
        Trừ kho an toàn với SELECT FOR UPDATE chống race condition.
        items_data: [{'menuitem_id': 1, 'quantity': 2}, ...]
        """
        menu_ids = [item['menuitem_id'] for item in items_data]
        menus = MenuItem.objects.filter(id__in=menu_ids).select_for_update()
        menu_map = {m.id: m for m in menus}

        for item_data in items_data:
            menu = menu_map.get(item_data['menuitem_id'])
            if not menu:
                raise ValueError(f"MenuItem {item_data['menuitem_id']} không tồn tại")
            
            if menu.stock < item_data['quantity']:
                raise ValueError(
                    f"'{menu.title}' không đủ hàng. "
                    f"Còn: {menu.stock}, Cần: {item_data['quantity']}"
                )
            
            menu.stock -= item_data['quantity']
            menu.save(update_fields=['stock'])
            
            # Ghi log inventory (Chuẩn bị cho Audit/Kafka)
            InventoryLog.objects.create(
                menu_item=menu,
                action='reserve',
                quantity=item_data['quantity'],
                order=order
            )

    @staticmethod
    @transaction.atomic
    def release_stock(items_data: list[dict], order=None):
        """Hoàn trả kho khi hủy đơn hoặc lỗi"""
        menu_ids = [item['menuitem_id'] for item in items_data]
        menus = MenuItem.objects.filter(id__in=menu_ids).select_for_update()
        menu_map = {m.id: m for m in menus}

        for item_data in items_data:
            menu = menu_map.get(item_data['menuitem_id'])
            if menu:
                menu.stock += item_data['quantity']
                menu.save(update_fields=['stock'])
                
                InventoryLog.objects.create(
                    menu_item=menu,
                    action='release',
                    quantity=item_data['quantity'],
                    order=order
                )

class CouponService:
    @staticmethod
    def validate_and_apply(coupon_code: str, total_amount: float):
        """
        Kiểm tra coupon và tính toán số tiền sau giảm giá.
        Trả về: (final_amount, coupon_instance)
        """
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            raise ValueError("Mã coupon không tồn tại")
        
        if not coupon.is_valid():
            raise ValueError("Mã coupon đã hết hạn hoặc không còn hiệu lực")
        
        discount = total_amount * (coupon.discount_percentage / 100)
        final_amount = total_amount - discount
        
        # Tăng usage count (Lưu ý: Trong production thật sự cần lock row coupon để tránh race condition)
        coupon.used_count += 1
        coupon.save(update_fields=['used_count'])
        
        return final_amount, coupon

class PaymentService:
    @staticmethod
    def process_payment(order: Order, method: str, amount: float):
        """
        Mock payment gateway. Trong thực tế sẽ gọi API bên thứ 3.
        Ở đây giả lập thành công ngẫu nhiên hoặc luôn thành công cho demo.
        """
        # Giả lập xử lý thanh toán
        import random
        success = random.choice([True, True, True, False]) # 75% thành công
        
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            method=method,
            status='paid' if success else 'failed',
            transaction_id=f"TXN_{uuid.uuid4().hex[:8].upper()}"
        )
        
        if success:
            order.status = 'preparing' # Chuyển trạng thái đơn hàng sang preparing nếu thanh toán thành công
            order.save(update_fields=['status'])
            logger.info(f"Payment successful for Order {order.id}")
        else:
            logger.error(f"Payment failed for Order {order.id}")
            
        return payment

class NotificationService:
    @staticmethod
    def send_notification(user, subject, message, type='in_app'):
        """
        Tạo notification record. Sau này có thể hook vào Celery/Kafka để gửi email/SMS thật.
        """
        Notification.objects.create(
            user=user,
            type=type,
            subject=subject,
            message=message,
            status='sent' # Giả lập đã gửi ngay
        )
        logger.info(f"Notification sent to {user.username}: {subject}")

class AuditService:
    @staticmethod
    def log_action(user, action, details="", ip_address=None):
        """Ghi log audit cho mọi hành động quan trọng"""
        AuditLog.objects.create(
            user=user,
            action=action,
            details=details,
            ip_address=ip_address
        )