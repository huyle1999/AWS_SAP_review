from django.urls import path
from .views import MenuItemsView, cart_view, orders_view, order_detail, create_coupon

urlpatterns = [
    path('menu-items', MenuItemsView.as_view()),
    path('cart/menu-items', cart_view),
    path('orders', orders_view),
    path('orders/<int:pk>', order_detail), # Lưu ý: Order ID giờ là UUID, nên có thể cần đổi sang <uuid:pk> nếu dùng UUID primary key
    path('coupons', create_coupon),
]