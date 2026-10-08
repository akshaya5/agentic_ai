from django.urls import path
from . import views

urlpatterns =[
    path("", views.get_orders_list, name="orders_list"),
    path("<int:pk>/", views.get_order_detail, name = 'order_detail')
]