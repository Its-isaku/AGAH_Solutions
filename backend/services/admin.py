#? Admin configuration for the services app
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TypeService, CompanyConfiguration, Order, OrderItem

#? <|--------------Helper Functions--------------|>
def create_base_services():
    """Create the 5 base services if they don't exist"""
    base_services = [
        {
            'name': 'Plasma Cutting',
            'type': 'plasma_cutting',
            'description': 'High-precision plasma cutting for metal fabrication',
            'short_description': 'Precision metal cutting with plasma technology'
        },
        {
            'name': 'Laser Engraving',
            'type': 'laser_engraving',
            'description': 'Detailed laser engraving for personalization and marking',
            'short_description': 'Professional laser engraving services'
        },
        {
            'name': 'Laser Cutting',
            'type': 'laser_cutting',
            'description': 'Precise laser cutting for various materials',
            'short_description': 'High-precision laser cutting'
        },
        {
            'name': '3D Printing',
            'type': '3d_printing',
            'description': 'Advanced 3D printing solutions for prototypes and production',
            'short_description': 'Professional 3D printing services'
        },
        {
            'name': 'Resin Printing',
            'type': 'resin_printing',
            'description': 'High-detail resin printing for precise applications',
            'short_description': 'Ultra-detailed resin 3D printing'
        }
    ]
    
    for service_data in base_services:
        TypeService.objects.get_or_create(
            type=service_data['type'],
            defaults={
                'name': service_data['name'],
                'description': service_data['description'],
                'short_description': service_data['short_description'],
                'is_base_service': True,
                'is_active': True
            }
        )


#? <|--------------Type Service Admin Configuration--------------|>
@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'name', 'type', 'is_base_service_display', 'base_price',
        'active', 'is_featured', 'order_display'
    ]
    
    #* Filters for the right sidebar
    list_filter = ['active', 'is_featured', 'is_base_service', 'type']
    
    #* Searchable fields
    search_fields = ['name', 'description', 'short_description']
    
    #* Fields that can be edited directly from the list view
    list_editable = ['active', 'is_featured', 'base_price']
    
    #* Default ordering
    ordering = ['order_display', 'name']
    
    #* Organization of fields in the detail form - CORREGIDO
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
    
    def is_base_service_display(self, obj):
        return "Base" if obj.is_base_service else "Additional"
    is_base_service_display.short_description = 'Service Type'
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj and obj.is_base_service:
            readonly_fields.extend(['type', 'is_base_service'])
        return readonly_fields
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} services marked as featured.')
    mark_as_featured.short_description = 'Mark as featured services'
    
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} services removed from featured.')
    mark_as_not_featured.short_description = 'Remove from featured'


#? <|--------------Company Configuration Admin - CORREGIDO--------------|>
@admin.register(CompanyConfiguration)
class CompanyConfigurationAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view - CAMPOS CORREGIDOS
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
        ('Service Configuration', {
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


#? <|--------------Order Item Inline Admin--------------|>
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
    #* Fields to show in the inline table - SIMPLIFICADO
    fields = [
        'service', 'quantity',
        'length_dimensions', 'width_dimensions', 'height_dimensions',
        'needs_custom_design', 'custom_design_price',
        'estimated_unit_price', 'final_unit_price'
    ]
    
    #* Fields that are read-only in the inline
    readonly_fields = ['estimated_unit_price']
    
    #* AGREGAR ESTE MÉTODO PARA CREAR LINK AL ORDERITEM INDIVIDUAL
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj: 
            fields.insert(0, 'edit_item_link')
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:  
            readonly.append('edit_item_link')
        return readonly
    
    def edit_item_link(self, obj):
        if obj.pk:
            return format_html(
                '<a href="/admin/services/orderitem/{}/change/" target="_blank">✏️ Edit Details</a>',
                obj.pk
            )
        return "Save order first"
    edit_item_link.short_description = 'Actions'


#? <|--------------Order Admin Configuration--------------|>
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    
    #* Fields to display in the list view
    list_display = [
        'order_number', 'customer_name', 'customer_email',
        'user_display', 'state_display', 'created_at',
        'get_total_items', 'get_estimated_total', 'state'
    ]
    
    #* Filters for the right sidebar
    list_filter = ['state', 'created_at']
    
    #* Searchable fields
    search_fields = [
        'order_number', 'customer_name', 'customer_email',
        'customer_phone', 'user__email', 'user__first_name', 'user__last_name'
    ]
    
    #* Fields that can be edited directly from the list view
    list_editable = ['state']
    
    #* Read-only fields in the detail form
    readonly_fields = [
        'order_number', 'created_at', 'user',
        'get_total_items', 'get_estimated_total', 'get_final_total'
    ]
    
    #* Organization of fields in the detail form - CORREGIDO
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'state', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'user')
        }),
        ('Order Management', {
            'fields': ('estimaded_price', 'final_price', 'estimated_completion_date_days', 'assigned_user')
        }),
        ('Additional Information', {
            'fields': ('additional_notes',),  
            'classes': ('collapse',)
        }),
        ('Calculations', {
            'fields': ('get_total_items', 'get_estimated_total', 'get_final_total'),
            'classes': ('collapse',)
        }),
    )
    
    #* Custom display methods
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.email
        return "Guest Order"
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user'
    
    def state_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'estimated': '#17a2b8',
            'confirmed': '#007bff',
            'in_progress': '#fd7e14',
            'completed': '#28a745',
            'canceled': 'red',
        }
        
        color = colors.get(obj.state, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_state_display()
        )
    state_display.short_description = 'Status'
    state_display.admin_order_field = 'state'
    
    def get_total_items(self, obj):
        return obj.items.count()
    get_total_items.short_description = 'Items'
    
    def get_estimated_total(self, obj):
        total = sum(item.get_estimated_total_with_design() for item in obj.items.all())
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"
    get_estimated_total.short_description = 'Estimated Total'
    
    def get_final_total(self, obj):
        total = sum(item.get_final_total_with_design() for item in obj.items.all())
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"
    get_final_total.short_description = 'Final Total'
    
    #* Custom mass actions for changing order status
    actions = ['mark_as_estimated', 'mark_as_confirmed', 'mark_as_in_progress', 'mark_as_completed']
    
    def mark_as_estimated(self, request, queryset):
        updated = queryset.update(state='estimated')
        self.message_user(request, f'{updated} orders marked as estimated.')
    mark_as_estimated.short_description = 'Mark as Estimated'
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(state='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark as Confirmed'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(state='in_progress')
        self.message_user(request, f'{updated} orders marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as In Progress'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(state='completed')
        self.message_user(request, f'{updated} orders marked as completed.')
    mark_as_completed.short_description = 'Mark as Completed'


#? <|--------------Order Item Admin Configuration--------------|>
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'id', 'order_number_display', 'service', 'quantity', 'dimensions_display',
        'needs_custom_design', 'custom_design_price',
        'estimated_unit_price', 'final_unit_price', 'get_total_display'
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'service__type', 'needs_custom_design', 'service'
    ]
    
    #* Searchable fields
    search_fields = [
        'order__order_number', 'order__customer_name',
        'service__name', 'description'
    ]
    
    #* Read-only fields
    readonly_fields = ['estimated_unit_price', 'area_display', 'total_price_display']
    
    #* MÉTODO DINÁMICO PARA MOSTRAR SOLO CAMPOS RELEVANTES POR SERVICIO
    def get_fieldsets(self, request, obj=None):
        
        base_fieldsets = [
            ('Order & Service', {
                'fields': ('order', 'service', 'description', 'quantity')
            }),
            ('Dimensions (in inches)', {
                'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions', 'area_display'),
                'description': 'All dimensions must be in inches'
            }),
            ('Files & Design', {
                'fields': ('design_file', 'needs_custom_design', 'custom_design_price')
            }),
        ]

        if obj and obj.service:
            service_type = obj.service.type
            
            if service_type == 'plasma_cutting':
                base_fieldsets.append(
                    ('Plasma Cutting Calculations', {
                        'fields': (
                            'plasma_design_programming_time', 'plasma_cutting_time',
                            'plasma_post_process_time', 'plasma_material_cost', 'plasma_consumables'
                        ),
                        'description': 'Formula: ((A*3.33)+(B*16.5)+(C*1.5)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3*1.08'
                    })
                )
            elif service_type in ['laser_cutting', 'laser_engraving']:
                base_fieldsets.append(
                    ('Laser Cutting/Engraving Calculations', {
                        'fields': (
                            'laser_design_programming_time', 'laser_cutting_time',
                            'laser_post_process_time', 'laser_material_cost', 'laser_consumables'
                        ),
                        'description': 'Formula: ((A*1.2)+(B*1.7)+(C*1)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3*1.08'
                    })
                )
            elif service_type == '3d_printing':
                base_fieldsets.append(
                    ('3D Printing Calculations', {
                        'fields': (
                            'printing_design_programming_time', 'printing_time', 'printing_material_used',
                            'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
                        ),
                        'description': 'Formula: (((B*2.7)+((D+B)*1.5)+(E)+(((C/1000)/F)*2))+G)*1.6*1.08'
                    })
                )
            elif service_type == 'resin_printing':
                base_fieldsets.append(
                    ('Resin Printing Calculations', {
                        'fields': (
                            'printing_design_programming_time', 'printing_time', 'printing_material_used',
                            'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
                        ),
                        'description': 'Formula: (((B*2.7)+((D+B)*1.5)+(E)+(((C/1000)/F)*2))+G)*1.6*1.08'
                    })
                )
        else:
            # Si no hay objeto (creando nuevo), mostrar todas las secciones colapsadas
            base_fieldsets.extend([
                ('Plasma Cutting Calculations', {
                    'fields': (
                        'plasma_design_programming_time', 'plasma_cutting_time',
                        'plasma_post_process_time', 'plasma_material_cost', 'plasma_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Solo visible si seleccionas servicio de Plasma Cutting'
                }),
                ('Laser Cutting/Engraving Calculations', {
                    'fields': (
                        'laser_design_programming_time', 'laser_cutting_time',
                        'laser_post_process_time', 'laser_material_cost', 'laser_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Solo visible si seleccionas servicio de Laser'
                }),
                ('3D Printing Calculations', {
                    'fields': (
                        'printing_design_programming_time', 'printing_time', 'printing_material_used',
                        'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Para servicios de 3D Printing'
                }),
                ('Resin Printing Calculations', {
                    'fields': (
                        'printing_design_programming_time', 'printing_time', 'printing_material_used',
                        'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Para servicios de Resin Printing'
                }),
            ])
        
        # Agregar la sección de Final Pricing al final
        base_fieldsets.append(
            ('Final Pricing', {
                'fields': ('estimated_unit_price', 'final_unit_price', 'total_price_display'),
                'description': 'Estimated price is from initial quote. Final price updates when you modify calculation fields above.'
            })
        )
        
        return base_fieldsets
    
    def order_number_display(self, obj):
        """Muestra el número de orden - NO REDIRECT AL ORDER"""
        return obj.order.order_number
    order_number_display.short_description = 'Order'
    order_number_display.admin_order_field = 'order'
    
    def dimensions_display(self, obj):
        """Muestra las dimensiones en formato legible"""
        if obj.length_dimensions and obj.width_dimensions:
            dims = f"{obj.length_dimensions} × {obj.width_dimensions}"
            if obj.height_dimensions:
                dims += f" × {obj.height_dimensions}"
            return f"{dims} in"
        return "Not specified"
    dimensions_display.short_description = 'Dimensions (L×W×H)'
    
    def get_total_display(self, obj):
        """Muestra el precio total incluyendo diseño"""
        total = obj.get_final_total_with_design()
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"
    get_total_display.short_description = 'Total Price'
    
    def area_display(self, obj):
        """Muestra el área calculada en in²"""
        if obj.length_dimensions and obj.width_dimensions:
            area = float(obj.length_dimensions) * float(obj.width_dimensions)
            return f"{area:.2f} in²"
        return "Not calculated"
    area_display.short_description = 'Area (in²)'
    
    def total_price_display(self, obj):
        """Muestra el precio total final (final_unit_price x quantity)"""
        if obj.final_unit_price and obj.quantity:
            total_final = float(obj.final_unit_price) * obj.quantity
            if obj.needs_custom_design and obj.custom_design_price:
                total_final += float(obj.custom_design_price)
            return f"${total_final:,.2f} MXN"
        return "Not calculated"
    total_price_display.short_description = 'Total Final Price'
    
    def save_model(self, request, obj, form, change):
        """Guarda el modelo y recalcula precios automáticamente"""
        super().save_model(request, obj, form, change)
        
        if hasattr(obj, 'calculate_automatic_pricing'):
            obj.calculate_automatic_pricing()
            obj.save()


#? <|--------------FUNCIONES AUXILIARES PARA EL ADMIN--------------|>

def get_service_calculation_fields(service_type):
    fields_map = {
        'plasma_cutting': [
            'plasma_design_programming_time', 'plasma_cutting_time',
            'plasma_post_process_time', 'plasma_material_cost', 'plasma_consumables'
        ],
        'laser_cutting': [
            'laser_design_programming_time', 'laser_cutting_time',
            'laser_post_process_time', 'laser_material_cost', 'laser_consumables'
        ],
        'laser_engraving': [
            'laser_design_programming_time', 'laser_cutting_time',
            'laser_post_process_time', 'laser_material_cost', 'laser_consumables'
        ],
        '3d_printing': [
            'printing_design_programming_time', 'printing_time', 'printing_material_used',
            'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
        ],
        'resin_printing': [
            'resin_design_programming_time', 'resin_printing_time', 'resin_material_used',
            'resin_post_process_time', 'resin_material_cost', 'resin_consumables'
        ]
    }
    return fields_map.get(service_type, [])