from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem, Coupon, Payment, AuditLog, Notification, InventoryLog


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'valid_from', 'valid_to', 'is_active', 'usage_limit', 'used_count')
    list_filter = ('is_active',)
    search_fields = ('code',)

    class Media:
        js = ('admin/js/vendor/jquery/jquery.min.js',)


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(AuditLog)
admin.site.register(Notification)
admin.site.register(InventoryLog)