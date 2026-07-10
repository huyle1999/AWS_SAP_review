from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db import transaction as db_transaction
from .models import MenuItem, Cart, Order, OrderItem, Coupon
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, CouponSerializer
from .services import InventoryService, CouponService, PaymentService, NotificationService, AuditService

# --- MENU API ---
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['price']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Chỉ Manager/Admin được tạo món
            if self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_staff:
                return [IsAuthenticated()]
            return []
        return []

# --- CART API ---
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    user = request.user

    if request.method == 'GET':
        items = Cart.objects.filter(user=user).select_related('menuitem')
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        menuitem_id = request.data.get('menuitem')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "MenuItem not found"}, status=404)
        
        # Validate Stock
        existing_item = Cart.objects.filter(user=user, menuitem_id=menuitem_id).first()
        current_qty = existing_item.quantity if existing_item else 0
        total_requested = current_qty + quantity
        
        if menuitem.stock < total_requested:
            return Response({
                "error": f"Insufficient stock. Available: {menuitem.stock}, "
                         f"In cart: {current_qty}, Adding: {quantity}"
            }, status=400)
        
        item, created = Cart.objects.get_or_create(
            user=user,
            menuitem_id=menuitem_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
            
        AuditService.log_action(user, 'add_to_cart', f"Added {quantity} of {menuitem.title}")
        return Response({"msg": "added"}, status=201)

    if request.method == 'DELETE':
        Cart.objects.filter(user=user).delete()
        AuditService.log_action(user, 'clear_cart')
        return Response({"msg": "deleted"})

# --- ORDER API ---
@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    user = request.user
    
    if request.method == 'PATCH':
        # Chỉ Manager/Delivery Crew được update status/delivery crew
        if not (user.groups.filter(name='Manager').exists() or 
                user.groups.filter(name='Delivery crew').exists() or 
                user.is_staff):
            return Response({"error": "Permission denied"}, status=403)
            
        order_id = request.data.get('id')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
            
        if 'delivery_crew' in request.data:
            order.delivery_crew_id = request.data['delivery_crew']
        if 'status' in request.data:
            # Validate state transition đơn giản
            valid_transitions = {
                'pending': ['preparing', 'cancelled'],
                'preparing': ['delivering', 'cancelled'],
                'delivering': ['completed', 'cancelled'],
                'completed': [],
                'cancelled': []
            }
            new_status = request.data['status']
            if new_status not in valid_transitions.get(order.status, []):
                return Response({"error": f"Invalid status transition from {order.status} to {new_status}"}, status=400)
            order.status = new_status
            
        order.save()
        AuditService.log_action(user, 'update_order_status', f"Order {order.id} -> {order.status}")
        return Response({"msg": "updated"})
        
    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            orders = Order.objects.all().prefetch_related('items')
        elif user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew=user).prefetch_related('items')
        else:
            orders = Order.objects.filter(user=user).prefetch_related('items')
            
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=user).select_related('menuitem')
        if not cart_items.exists():
            return Response({"error": "cart empty"}, status=400)
        
        # Tính tổng tiền
        total = sum(ci.menuitem.price * ci.quantity for ci in cart_items)
        
        # Xử lý Coupon nếu có
        coupon_code = request.data.get('coupon_code')
        coupon_instance = None
        if coupon_code:
            try:
                total, coupon_instance = CouponService.validate_and_apply(coupon_code, total)
                AuditService.log_action(user, 'apply_coupon', f"Coupon {coupon_code} applied")
            except ValueError as e:
                return Response({"error": str(e)}, status=400)
        
        # Chuẩn bị data cho inventory
        items_data = [
            {'menuitem_id': ci.menuitem_id, 'quantity': ci.quantity}
            for ci in cart_items
        ]
        
        try:
            with db_transaction.atomic():
                # 1. Reserve Stock
                InventoryService.reserve_stock(items_data)
                
                # 2. Create Order
                order = Order.objects.create(
                    user=user,
                    total_price=total
                )
                
                # 3. Create Order Items
                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        menuitem=ci.menuitem,
                        quantity=ci.quantity,
                        unit_price=ci.menuitem.price
                    )
                    for ci in cart_items
                ])
                
                # 4. Process Payment (Mock)
                payment_method = request.data.get('payment_method', 'cod')
                payment = PaymentService.process_payment(order, payment_method, total)
                
                if payment.status == 'failed':
                    # Nếu thanh toán thất bại, rollback stock (do atomic block, nếu raise exception thì rollback tự động)
                    # Nhưng ở đây ta muốn trả về lỗi cụ thể nên raise
                    raise ValueError("Payment failed")
                
                # 5. Clear Cart
                cart_items.delete()
                
                # 6. Send Notification
                NotificationService.send_notification(
                    user, 
                    "Order Placed", 
                    f"Your order {order.id} has been placed successfully."
                )
                
                AuditService.log_action(user, 'create_order', f"Order {order.id} created")
                
            return Response({"msg": "order created", "order_id": order.id}, status=201)
            
        except ValueError as e:
            # Nếu có lỗi (stock hoặc payment), atomic block sẽ rollback DB changes
            return Response({"error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        order = Order.objects.get(id=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "not found"}, status=404)

    serializer = OrderSerializer(order)
    return Response(serializer.data)

# --- COUPON API (Cho Manager/Admin) ---
@api_view(['POST'])
@permission_classes([IsAdminUser]) # Hoặc custom permission cho Manager
def create_coupon(request):
    serializer = CouponSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)