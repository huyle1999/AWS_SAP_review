from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem, Coupon, Payment, AuditLog, Notification

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.ReadOnlyField(source='menuitem.title')
    unit_price = serializers.ReadOnlyField(source='menuitem.price')
    
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_title', 'quantity', 'unit_price']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.ReadOnlyField(source='menuitem.title')
    
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'menuitem_title', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.ReadOnlyField(source='payment.status')
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'delivery_crew', 'items', 'payment_status', 'created_at']
        read_only_fields = ['id', 'status', 'total_price', 'created_at']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'valid_from', 'valid_to']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'details', 'timestamp']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'