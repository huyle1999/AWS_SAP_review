from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem, Coupon, Payment, AuditLog, Notification, InventoryLog

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(AuditLog)
admin.site.register(Notification)
admin.site.register(InventoryLog)