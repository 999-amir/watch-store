from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('show/', views.OrderView.as_view(), name='show_order'),
    path('add/<int:variant_id>/', views.CartAddView.as_view(), name='add_order'),
    path('add/one/<int:variant_id>/', views.CartAddOneView.as_view(), name='add_one_order'),
    path('remove/one/<int:variant_id>/', views.CartRemoveOneView.as_view(), name='remove_one_order'),
    path('remove/<int:variant_id>/', views.CartRemoveView.as_view(), name='remove_order'),
    path('submit/', views.OrderSubmitView.as_view(), name='submit_order'),
    path('coupon/', views.CouponView.as_view(), name='coupon_order'),
    path('set/new/order/', views.CreateOrderView.as_view(), name='create_order'),
    path('zpRequest/<authority>/', views.SendRequest.as_view(), name='zp_send_request'),
    path('zpVerify/<authority>', views.VerifyPay.as_view(), name='zp_verify_pay'),
    path('zpSimulator/', views.ZarinPalSimulator.as_view(), name='zp_simulator'),
    path('last/order/', views.LastOrdersView.as_view(), name='last_order')
]
