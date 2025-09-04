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
            'type': 'plasma',
            'name': 'Plasma Cutting',
            'short_description': 'High-precision plasma cutting service',
            'description': 'Professional plasma cutting services for metal fabrication',
            'active': True,
            'is_base_service': True,
            'order_display': 1
        },
        {
            'type': 'laser_engraving', 
            'name': 'Laser Engraving',
            'short_description': 'Detailed laser engraving on various materials',
            'description': 'Precision laser engraving for personalization and branding',
            'active': True,
            'is_base_service': True,
            'order_display': 2
        },
        {
            'type': 'laser_cutting',
            'name': 'Laser Cutting', 
            'short_description': 'Precise laser cutting service',
            'description': 'High-precision laser cutting for various materials',
            'active': True,
            'is_base_service': True,
            'order_display': 3
        },
        {
            'type': '3D_printing',
            'name': '3D Printing',
            'short_description': 'Professional 3D printing service',
            'description': 'High-quality 3D printing for prototypes and final products',
            'active': True,
            'is_base_service': True,
            'order_display': 4
        },
        {
            'type': 'resin_printing',
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

#? <|--------------TypeService Admin Configuration--------------|>
@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'order_display',
        'name',
        'type',
        'is_featured',
        'active',
        'image_preview'
    ]
    
    #* Filters for the right sidebar  
    list_filter = [
        'is_featured',
        'active',
        'is_base_service'
    ]
    
    #* Searchable fields
    search_fields = ['name', 'type', 'description']
    
    #* Default ordering
    ordering = ['order_display']
    
    #* Make order_display editable
    list_editable = ['is_featured']
    
    #* Readonly fields - order_display auto-assigned
    readonly_fields = ['type', 'order_display', 'image_preview']
    
    #* Custom form for adding new services - ONLY name field
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Adding new service
            return (
                ('Nuevo Servicio', {
                    'fields': ('name',),
                    'description': 'Solo introduce el nombre del nuevo servicio'
                }),
            )
        else:  # Editing existing service
            return (
                ('Service Details', {
                    'fields': ('name', 'type', 'short_description', 'description')
                }),
                ('Display Settings', {
                    'fields': ('order_display', 'active', 'is_featured', 'is_base_service')
                }),
                ('Media', {
                    'fields': ('image', 'image_preview'),
                    'classes': ('collapse',)
                }),
                ('Pricing', {
                    'fields': ('base_price',),
                    'classes': ('collapse',)
                }),
            )
    
    #* Custom form to show only name field for new services
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Adding new service
            # Remove all fields except name
            for field_name in list(form.base_fields.keys()):
                if field_name != 'name':
                    del form.base_fields[field_name]
        return form
    
    #* Save method to handle type generation and order_display
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            # Auto-generate type from name
            obj.type = obj.name.lower().replace(' ', '_')
            
            # Auto-assign order_display
            max_order = TypeService.objects.aggregate(models.Max('order_display'))['order_display__max']
            obj.order_display = (max_order or 0) + 1
            
            # Set defaults
            obj.active = True
            obj.is_base_service = False
        
        super().save_model(request, obj, form, change)
    
    #* Actions for bulk operations
    actions = ['mark_as_featured', 'mark_as_not_featured']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} services marked as featured.')
    mark_as_featured.short_description = 'Mark as featured services'
    
    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} services removed from featured.')
    mark_as_not_featured.short_description = 'Remove from featured'
    
    #* Image preview method
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


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
    extra = 0
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
    readonly_fields = ['estimated_unit_price', 'final_unit_price']


#? <|--------------Order Admin Configuration--------------|>
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'order_number',
        'customer_name', 
        'customer_email',
        'order_status_display',
        'estimated_total_display',
        'final_total_display',
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
    readonly_fields = ['order_number', 'created_at', 'estimaded_price', 'final_price']
    
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
    
    def estimated_total_display(self, obj):
        total = obj.get_estimated_total_price()
        if total > 0:
            return f"${total:,.2f} MXN"
        return "-"
    estimated_total_display.short_description = 'Estimated Total'
    
    def final_total_display(self, obj):
        total = obj.get_final_total_price()
        if total > 0:
            return f"${total:,.2f} MXN"
        return "-"
    final_total_display.short_description = 'Final Total'
    
    def save_model(self, request, obj, form, change):
        if not obj.order_number:
            import uuid
            obj.order_number = str(uuid.uuid4())[:8].upper()
        
        # Auto-calculate totals
        super().save_model(request, obj, form, change)
        
        # Update estimated and final prices
        obj.estimaded_price = obj.get_estimated_total_price()
        obj.final_price = obj.get_final_total_price()
        obj.save(update_fields=['estimaded_price', 'final_price'])


#? <|--------------Order Item Admin Configuration--------------|>
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    
    #* Fields to display in the list view
    list_display = [
        'item_display',
        'order_number_display',
        'service', 
        'quantity',
        'dimensions_display',
        'needs_custom_design',
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
    
    #* CRÍTICO: Solo este campo debe ser clickeable
    list_display_links = ['item_display']
    
    #* Read-only fields - DEBE IR ANTES DE LOS MÉTODOS
    readonly_fields = [
        'estimated_unit_price', 
        'final_unit_price',
        'area_display',
        'estimated_total_display',
        'final_total_display',
        'plasma_formula_display',
        'laser_formula_display', 
        'printing_formula_display'
    ]
    
    def item_display(self, obj):
        return f"Item #{obj.id}"
    item_display.short_description = 'Item ID'
    
    def order_number_display(self, obj):
        return obj.order.order_number
    order_number_display.short_description = 'Order'
    
    #* Organization of fields in the detail form
    def get_fieldsets(self, request, obj=None):
        if obj and obj.service:
            service_type = obj.service.type
            
            # DEBUG - REMOVER DESPUÉS
            print(f"DEBUG: service_type = '{service_type}'")
            print(f"DEBUG: service.name = '{obj.service.name}'")
            
            # Base fieldsets
            fieldsets = [
                ('Service Information', {
                    'fields': ('order', 'service', 'quantity')
                }),
                ('Dimensions', {
                    'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions', 'area_display')
                }),
                ('Design & Pricing', {
                    'fields': ('needs_custom_design', 'custom_design_price')
                })
            ]
            
            # Add calculation fields based on service type - CORREGIDO
            if service_type == 'plasma' or service_type == 'PLASMA_CUTTING' or 'plasma' in service_type.lower():
                fieldsets.append(
                    ('🔥 Plasma Cutting Calculations', {
                        'fields': (
                            'plasma_formula_display',
                            'plasma_design_programming_time',
                            'plasma_cutting_time',
                            'plasma_post_process_time',
                            'plasma_material_cost',
                            'plasma_consumables'
                        ),
                        'description': 'Complete estos campos para calcular el precio final automáticamente'
                    })
                )
            elif service_type in ['laser_engraving', 'laser_cutting'] or service_type in ['LASER_ENGRAVING', 'LASER_CUTTING'] or any(x in service_type.lower() for x in ['laser']):
                fieldsets.append(
                    ('⚡ Laser Calculations', {
                        'fields': (
                            'laser_formula_display',
                            'laser_design_programming_time',
                            'laser_cutting_time',
                            'laser_post_process_time',
                            'laser_material_cost',
                            'laser_consumables'
                        ),
                        'description': 'Complete estos campos para calcular el precio final automáticamente'
                    })
                )
            elif service_type in ['3D_printing', 'resin_printing'] or service_type in ['3D_PRINTING', 'RESIN_PRINTING'] or any(x in service_type.lower() for x in ['3d', 'printing', 'resin']):
                fieldsets.append(
                    ('🖨️ 3D Printing Calculations', {
                        'fields': (
                            'printing_formula_display',
                            'printing_design_programming_time',
                            'printing_time',
                            'printing_material_used',
                            'printing_post_process_time',
                            'printing_material_cost',
                            'printing_consumables'
                        ),
                        'description': 'Complete estos campos para calcular el precio final automáticamente'
                    })
                )
            
            # Final pricing section
            fieldsets.append(
                ('💰 Final Pricing', {
                    'fields': (
                        'estimated_unit_price',
                        'final_unit_price',
                        'estimated_total_display',
                        'final_total_display'
                    ),
                    'description': 'El precio final se calcula automáticamente basado en los campos de arriba'
                })
            )
            
            fieldsets.append(
                ('Files', {
                    'fields': ('design_file',),
                    'classes': ('collapse',)
                })
            )
            
            return fieldsets
        else:
            # Default fieldset for new items
            return (
                ('Service Information', {
                    'fields': ('order', 'service', 'quantity')
                }),
                ('Dimensions', {
                    'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions')
                }),
                ('Design & Pricing', {
                    'fields': ('needs_custom_design', 'custom_design_price', 'estimated_unit_price', 'final_unit_price')
                }),
            )
    
    #* Custom methods for display
    def dimensions_display(self, obj):
        if obj.length_dimensions and obj.width_dimensions and obj.height_dimensions:
            return f"{obj.length_dimensions} × {obj.width_dimensions} × {obj.height_dimensions}"
        return "Not specified"
    dimensions_display.short_description = 'Dimensions (L×W×H)'
    
    def estimated_total_display(self, obj):
        total = obj.get_estimated_total_with_design()
        return f"${total:,.2f} MXN"
    estimated_total_display.short_description = 'Estimated Total'
    
    def final_total_display(self, obj):
        total = obj.get_final_total_with_design()
        return f"${total:,.2f} MXN"
    final_total_display.short_description = 'Final Total'
    
    def area_display(self, obj):
        area = obj.get_area_square_inches()
        return f"{area:.2f} in²" if area > 0 else "Not calculated"
    area_display.short_description = 'Area'
    
    # Formula displays - CORREGIDO PARA MOSTRAR COMO TEXTO
    def plasma_formula_display(self, obj):
        area = obj.get_area_square_inches()
        return format_html(
            '<div style="background: #f0f0f0; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; font-size: 12px;">'
            '<strong>Fórmula Plasma Cutting:</strong><br><br>'
            'SUBTOTAL = ((A×3.33)+(B×16.5)+(C×1.5)+(D×0.03211)+(((E×F)/4608)×2)+G)×1.3<br>'
            'TOTAL MXN = SUBTOTAL × 1.08<br><br>'
            '<strong>Variables:</strong><br>'
            'A = Diseño y Programación (min)<br>'
            'B = Corte (min)<br>'
            'C = Post-proceso (min)<br>'
            'D = Luz (kW/min) = 0.09524 × B<br>'
            'E = Costo Material (placa 4\'×8\')<br>'
            'F = Área (in²) = <strong>{:.2f}</strong><br>'
            'G = Consumibles<br>'
            '</div>'.format(area)
        )
    plasma_formula_display.short_description = 'Calculation Formula'
    
    def laser_formula_display(self, obj):
        area = obj.get_area_square_inches()
        return f"""
Fórmula Laser:
SUBTOTAL = ((A×1.2)+(B×1.7)+(C×1)+(D×0.03211)+(((E×F)/4608)×2)+G)×1.3
TOTAL MXN = SUBTOTAL × 1.08

Variables:
A = Diseño y Programación (min)
B = Corte/Grabado (min)
C = Post-proceso (min)
D = Luz (kW/min) = 0.09524 × B
E = Costo Material
F = Área (in²) = {area:.2f}
G = Consumibles
        """.strip()
    laser_formula_display.short_description = 'Calculation Formula'
    
    def printing_formula_display(self, obj):
        return f"""
Fórmula 3D Printing:
SUBTOTAL = ((A×2.7)+(B×1.9)+(C/1000)×F+(D×1.5)+G)×1.3
TOTAL MXN = SUBTOTAL × 1.08

Variables:
A = Diseño y Programación (min)
B = Impresión (min)
C = Material Utilizado (g)
D = Post-proceso (min)
F = Costo Material (por 1Kg)
G = Consumibles
        """.strip()
    printing_formula_display.short_description = 'Calculation Formula'
    
    #* IMPORTANTE: Override para forzar que vaya al item específico
    def response_change(self, request, obj):
        """Stay on the item edit page after saving"""
        res = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return res
        return res