
#? Nesesary imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    #* Public Views
    HomepageView,
    TypeServiceListView,
    TypeServiceDetailView,
    CompanyConfigurationView,
    ContactFormView,
    OrderTrackingView,
    PublicOrderCreateView,
    CustomerOrdersView,
    ConfirmOrderView, 
    CancelOrderView,
    
    #* Protected Views (User Authentication Required)
    OrderCreateView,
    UserOrdersListView,
    UserOrderDetailView,
    
    #* Admin Views (Staff/Admin Only)
    AdminOrderListView,
    AdminOrderDetailView,
)

urlpatterns = [

    #* Customer orders endpoint (public - requires email)
    path('api/orders/customer/', CustomerOrdersView.as_view(), name='customer-orders'),
    
    #* Order confirmation endpoints (public)
    path('api/orders/confirm/', ConfirmOrderView.as_view(), name='confirm-order'),
    path('api/orders/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    
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
    
    path('api/orders/create/', PublicOrderCreateView.as_view(), name='public-order-create'),
    
    
    #? <|--------------Protected API Endpoints (Authentication Required)--------------|>
    
    #* Order creation (requires authentication)
path('api/orders/create-auth/', OrderCreateView.as_view(), name='order-create-auth'),
    
    #* User's personal orders
    path('api/orders/my-orders/', UserOrdersListView.as_view(), name='user-orders-list'),
    path('api/orders/my-orders/<int:pk>/', UserOrderDetailView.as_view(), name='user-order-detail'),
    
    
    #? <|--------------Admin API Endpoints (Staff/Admin Only)--------------|>
    
    #* Admin order management
    path('api/admin/orders/', AdminOrderListView.as_view(), name='admin-orders-list'),
    path('api/admin/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)