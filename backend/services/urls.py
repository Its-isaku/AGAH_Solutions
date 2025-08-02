
#? Nesesary imports
from django.urls import path
from .views import (
    HomepageDataView,
    ServiceTypeListView,
    ServiceTypeDetailView, 
    CompanyConfigurationView,
    OrderListByCustomerView,
    OrderCreateView,
    OrderTrackingView,
    AddItemToCartView,
    CalculateCartTotalView,
    ContactFormView
)

urlpatterns = [
    #* Homepage data endpoint
    path('api/homepage/', HomepageDataView.as_view(), name='homepage-data'),
    
    #* Service Types endpoints (Services page)
    path('api/services/', ServiceTypeListView.as_view(), name='service-list'),
    path('api/services/<str:type>/', ServiceTypeDetailView.as_view(), name='service-detail'),
    
    #* Company Configuration endpoint (About Us page)
    path('api/company/', CompanyConfigurationView.as_view(), name='company-config'),
    
    #* Orders endpoints (Orders page - list by customer)
    path('api/orders/customer/', OrderListByCustomerView.as_view(), name='orders-by-customer'),
    path('api/orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('api/orders/track/<str:order_number>/', OrderTrackingView.as_view(), name='order-tracking'),
    
    #* Cart functionality endpoints
    path('api/cart/add-item/', AddItemToCartView.as_view(), name='cart-add-item'),
    path('api/cart/calculate-total/', CalculateCartTotalView.as_view(), name='cart-calculate-total'),
    
    #* Contact endpoint (Contact Us page)
    path('api/contact/', ContactFormView.as_view(), name='contact-form'),
]