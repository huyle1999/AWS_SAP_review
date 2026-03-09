#menu api
from django.shortcuts import render
from rest_framework import generics
from .models import MenuItem
from .serializers import MenuItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['price']
    def get_permissions(self):
        if self.request.method == 'POST':
            if self.request.user.groups.filter(name='Manager').exists():
                return [IsAuthenticated()]
            return []
        return []
#CART API
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    user = request.user

    if request.method == 'GET':
        items = Cart.objects.filter(user=user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        item, created = Cart.objects.get_or_create(
            user=user,
            menuitem_id=request.data['menuitem'],
            defaults={'quantity': request.data['quantity']}
        )

        if not created:
            item.quantity += int(request.data['quantity'])
            item.save()
        else:
            item.quantity = request.data['quantity']
            item.save()
        return Response({"msg": "added"}, status=201)

    if request.method == 'DELETE':
        Cart.objects.filter(user=user).delete()
        return Response({"msg": "deleted"})
#ORDER API
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer

@api_view(['GET', 'POST','PATCH'])
def orders_view(request):
    user = request.user
    if request.method == 'PATCH':
        order = Order.objects.get(id=request.data['id'])
        if 'delivery_crew' in request.data:
            order.delivery_crew_id = request.data['delivery_crew']

        if 'status' in request.data:
            order.status = request.data['status']
        order.save()
        return Response({"msg": "assigned"})
        
    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists() or user.is_staff:
            orders = Order.objects.all()

        elif user.groups.filter(name='Delivery crew').exists():
            orders = Order.objects.filter(delivery_crew=user)

        else:
            orders = Order.objects.filter(user=user)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        cart = Cart.objects.filter(user=user)
        if not cart.exists():
            return Response({"error": "cart empty"}, status=400)
        order = Order.objects.create(user=user)

        for item in cart:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity
            )

        cart.delete()

        return Response({"msg": "order created"}, status=201)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        order = Order.objects.get(id=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "not found"}, status=404)

    serializer = OrderSerializer(order)
    return Response(serializer.data)