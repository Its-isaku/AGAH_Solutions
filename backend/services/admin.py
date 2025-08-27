#? Admin configuration for the services app
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TypeService, CompanyConfiguration, Order, OrderItem

#? <|--------------Helper Functions for Base Services--------------|>

def create_base_services():
    """Create the 5 base services for AGAH Solutions"""
    
    base_services = [
        {
            'type': 'PLASMA_CUTTING',
            'name': 'Plasma Cutting',
            'short_description': 'High-precision plasma cutting service',
            'description': 'Professional plasma cutting services for metal fabrication',
            'active': True,
            'is_base_service': True,
            'order_display': 1
        },
        {
            'type': 'LASER_ENGRAVING', 
            'name': 'Laser Engraving',
            'short_description': 'Detailed laser engraving on various materials',
            'description': 'Precision laser engraving for personalization and branding',
            'active': True,
            'is_base_service': True,
            'order_display': 2
        },
        {
            'type': 'LASER_CUTTING',
            'name': 'Laser Cutting', 
            'short_description': 'Precise laser cutting service',
            'description': 'High-precision laser cutting for various materials',
            'active': True,
            'is_base_service': True,
            'order_display': 3
        },
        {
            'type': '3D_PRINTING',
            'name': '3D Printing',
            'short_description': 'Professional 3D printing service',
            'description': 'High-quality 3D printing for prototypes and final products',
            'active': True,
            'is_base_service': True,
            'order_display': 4
        },
        {
            'type': 'RESIN_PRINTING',
            'name': 'Resin Printing',
            'short_description': 'High-detail resin printing',
            'description': 'Ultra-detailed resin printing for precision parts',
            'active': True,
            'is_base_service': True,
            'order_display': 5
        }
    ]
    
    for service_data in base_services:
        TypeService.objects.get_or_create(
            type=service_data['type'],
            defaults={
                'name': service_data['name'],
                'short_description': service_data['short_description'],
                'description': service_data['description'],
                'active': service_data['active'],
                'is_base_service': service_data['is_base_service'],
                'order_display': service_data['order_display']
            }
        )

#? <|--------------Type Service Admin Configuration--------------|>
@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'name', 
        'type', 
        'base_price',
        'active', 
        'is_featured', 
        'order_display'
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'active', 
        'is_featured', 
        'is_base_service', 
        'type'
    ]
    
    #* Searchable fields
    search_fields = [
        'name', 
        'description', 
        'short_description'
    ]
    
    #* Fields that can be edited directly from the list view
    list_editable = [
        'active', 
        'is_featured', 
        'base_price'
    ]
    
    #* Default ordering
    ordering = ['order_display', 'name']
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('base_price',)
        }),
        ('Display Settings', {
            'fields': ('active', 'is_featured', 'order_display')
        }),
        ('Media', {
            'fields': ('principal_image',),
            'classes': ('collapse',)
        }),
    )
    
    #* Custom mass actions
    actions = ['mark_as_featured', 'mark_as_not_featured']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} services marked as featured.')
    mark_as_featured.short_description = 'Mark as featured services'
    
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} services removed from featured.')
    mark_as_not_featured.short_description = 'Remove from featured'


#? <|--------------Company Configuration Admin--------------|>
@admin.register(CompanyConfiguration)
class CompanyConfigurationAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'company_name', 
        'company_tagline',
        'company_phone', 
        'contact_email',
        'updated_at'
    ]
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_tagline', 'about_us', 'company_mission', 'company_vision')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'company_phone', 'company_address')
        }),
        ('Business Configuration', {
            'fields': ('company_time_response_hours',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    #* Read-only fields
    readonly_fields = ['created_at', 'updated_at']
    
    #* Search functionality
    search_fields = ['company_name', 'company_tagline', 'contact_email']
    
    def has_add_permission(self, request):
        if CompanyConfiguration.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False


#? <|--------------Order Item Inline Configuration--------------|>
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = [
        'service', 
        'quantity',
        'length_dimensions', 
        'width_dimensions', 
        'height_dimensions',
        'needs_custom_design',
        'custom_design_price',
        'estimated_unit_price', 
        'final_unit_price'
    ]


#? <|--------------Order Admin Configuration--------------|>
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'order_number',
        'customer_name', 
        'customer_email',
        'order_status_display',
        'final_price',
        'created_at'
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'state',
        'created_at'
    ]
    
    #* Searchable fields
    search_fields = [
        'order_number',
        'customer_name', 
        'customer_email', 
        'customer_phone'
    ]
    
    #* Default ordering
    ordering = ['-created_at']
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('order_number', 'state', 'estimaded_price', 'final_price', 'additional_notes')
        }),
        ('Assignment & Timeline', {
            'fields': ('assigned_user', 'estimated_completion_date_days', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    #* Read-only fields
    readonly_fields = ['order_number', 'created_at']
    
    #* Inline editing for order items
    inlines = [OrderItemInline]
    
    #* Custom methods for display
    def order_status_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'estimated': '#17a2b8', 
            'confirmed': '#007bff',
            'in_progress': '#fd7e14',
            'completed': '#28a745',
            'canceled': '#dc3545'
        }
        color = colors.get(obj.state, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display()
        )
    order_status_display.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not obj.order_number:
            import uuid
            obj.order_number = str(uuid.uuid4())[:8].upper()
        super().save_model(request, obj, form, change)


#? <|--------------Order Item Admin Configuration--------------|>
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'order_link',
        'service', 
        'quantity',
        'dimensions_display',
        'needs_custom_design',
        'custom_design_price',
        'estimated_unit_price', 
        'final_unit_price'
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'service',
        'needs_custom_design'
    ]
    
    #* Searchable fields
    search_fields = [
        'order__order_number',
        'order__customer_name', 
        'service__name'
    ]
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Service Information', {
            'fields': ('order', 'service', 'quantity')
        }),
        ('Dimensions', {
            'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions')
        }),
        ('Design & Pricing', {
            'fields': ('needs_custom_design', 'custom_design_price', 'estimated_unit_price', 'final_unit_price')
        }),
        ('Files', {
            'fields': ('design_file',),
            'classes': ('collapse',)
        }),
    )
    
    #* Custom methods for display
    def order_link(self, obj):
        url = reverse('admin:services_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'
    
    def dimensions_display(self, obj):
        if obj.length_dimensions and obj.width_dimensions and obj.height_dimensions:
            return f"{obj.length_dimensions} × {obj.width_dimensions} × {obj.height_dimensions}"
        return "Not specified"
    dimensions_display.short_description = 'Dimensions (L×W×H)'