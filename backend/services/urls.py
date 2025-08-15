
#? Nesesary imports
from django.urls import path
from .views import (
    #* Public Views
    HomepageView,
    TypeServiceListView,
    TypeServiceDetailView,
    CompanyConfigurationView,
    ContactFormView,
    OrderTrackingView,
    
    #* Protected Views (User Authentication Required)
    OrderCreateView,
    UserOrdersListView,
    UserOrderDetailView,
    
    #* Admin Views (Staff/Admin Only)
    AdminOrderListView,
    AdminOrderDetailView,
)

urlpatterns = [
    
    #? <|--------------Public API Endpoints (No Authentication Required)--------------|>
    
    #* Homepage endpoint
    path('api/homepage/', HomepageView.as_view(), name='homepage-data'),
    
    #* Services endpoints
    path('api/services/', TypeServiceListView.as_view(), name='service-list'),
    path('api/services/<int:pk>/', TypeServiceDetailView.as_view(), name='service-detail'),
    
    #* Company information endpoint
    path('api/company/', CompanyConfigurationView.as_view(), name='company-info'),
    
    #* Contact form endpoint
    path('api/contact/', ContactFormView.as_view(), name='contact-form'),
    
    #* Order tracking endpoint (public - requires order number + email)
    path('api/orders/track/', OrderTrackingView.as_view(), name='order-tracking'),
    
    
    #? <|--------------Protected API Endpoints (Authentication Required)--------------|>
    
    #* Order creation (requires authentication)
    path('api/orders/create/', OrderCreateView.as_view(), name='order-create'),
    
    #* User's personal orders
    path('api/orders/my-orders/', UserOrdersListView.as_view(), name='user-orders-list'),
    path('api/orders/my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='user-order-detail'),
    
    
    #? <|--------------Admin API Endpoints (Staff/Admin Only)--------------|>
    
    #* Admin order management
    path('api/admin/orders/', AdminOrderListView.as_view(), name='admin-orders-list'),
    path('api/admin/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
]