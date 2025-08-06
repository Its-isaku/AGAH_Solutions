#? Admin configuration for the services app
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TypeService, CompanyConfiguration, Order, OrderItem


#? <|--------------Service Type Admin Panel--------------|>
@admin.register(TypeService)
class TypeServiceAdmin(admin.ModelAdmin):
    
    #* Display fields in the admin panel for TypeService 
    list_display = (
        'name',
        'type',
        'formated_price',
        'active_status',
        'active',
        'is_base_service_display',
        'order_display',
        'image_thumbnail',
        )
    
    #* Filter options for the admin panel
    list_filter = [
        'type',                                                            #* Filter by service type
        'active',                                                          #* Filter by active status
        'is_base_service',                                                 #* Filter by base service
    ]
    
    #* Search fields for the admin panel
    search_fields = [
        'name',                                                            #* Search by service name
        'description',                                                     #* Search by service description
        'short_description',                                               #* Search by short description
    ]
    
    #* Fields that can be edited directly in the list view 
    list_editable = [
        'active',                                                          #* Allow editing of active status
    ]
    
    #* Organize the fields in the admin panel
    fieldsets = (
        ('Basic Information',{                                             #* Group basic information fields
            'fields':('name', 'type', 'short_description', 'is_base_service')
        }),
        ('Detailed Information',{                                          #* Group detailed information fields
            'fields':('description',),
            'classes': ('wide',)
        }),                                                            
        ('Price and Configuration',{                                       #* Group price and configuration fields
            'fields':('base_price', 'active', 'order_display')
        }),
        ('Image',{                                                         #* Group image fields
            'fields':('principal_image',)
        }),
    )
    
    #* Default ordering for the admin panel
    ordering = ['is_base_service', 'order_display', 'name']                #* Order by base service first, then order display field
    
    #* Prevent creating duplicates of base services and control readonly fields
    def get_readonly_fields(self, request, obj=None):
        readonly = ['order_display']                                       #* order_display is always readonly (auto-assigned)
        if obj and obj.is_base_service:
            readonly.extend(['type', 'is_base_service'])                   #* Base services can't change type
        else:
            readonly.append('is_base_service')                             #* New services auto-set to non-base
        return readonly
    
    #* Customize add form to show only essential fields
    def get_fieldsets(self, request, obj=None):
        if not obj:                                                        #* For new services (add form)
            return (
                ('New Service',{
                    'fields':('name',),
                    'description': 'Only provide the service name - everything else is automatic'
                }),
            )
        else:                                                              #* For existing services (edit form)
            return super().get_fieldsets(request, obj)
    
    #* function to format the price for display 
    def formated_price(self, obj):
        if obj.base_price:
            return f"${obj.base_price:.2f}"                                #* Format the price for display
        return "Not set"                                                   #* Show "Not set" if no price

    #* Short description and admin order field for the formatted price 
    formated_price.short_description = 'Price'                            #* Set the short description for the formatted price field
    formated_price.admin_order_field = 'base_price'                       #* Allow ordering by the base price field
    
    #* function to display the active status of the service type 
    def active_status(self, obj):
        if obj.active:                                                     #* Check if the service type is active
            color = 'green'                                                #* Set the color to green if active
            text = 'Active'                                                #* Set the text to "Active"
        else:                                                              #* If not active
            color = 'red'                                                  #* Set the color to red
            text = 'Inactive'                                              #* Set the text to "Inactive"
        return format_html(                                                #* Format the text with the appropriate color
            '<span style="color: {};">{}</span>',
            color, text
        )
    
    #* Short description for the active status field    
    active_status.short_description = 'Status'                            #* Set the short description for the active status field
    
    #* Function to display if it's a base service
    def is_base_service_display(self, obj):
        if obj.is_base_service:
            return format_html('<span style="color: blue;">Base</span>')
        return format_html('<span style="color: gray;">Additional</span>')
    is_base_service_display.short_description = 'Type'
    
    #* function to display a thumbnail of the service image
    def image_thumbnail(self, obj):
        if obj.principal_image:                                            #* Check if the service has a principal image
            return format_html(                                            #* Format the image as HTML
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 5px;" />',
                obj.principal_image.url                                    #* Use the URL of the principal image
            )
        return "No Image"                                                  #* Return "No Image" if no image is set
    
    #* Short description for the image thumbnail field
    image_thumbnail.short_description = 'Image'                           #* Set the short description for the image

#? <|--------------Company Configuration Admin Panel--------------|>
@admin.register(CompanyConfiguration)
class CompanyConfigurationAdmin(admin.ModelAdmin):
    
    #* Display fields in the admin panel for CompanyConfiguration
    list_display = (
        'company_name',                                                    #* Display the company name
        'contact_email',                                                   #* Display the company email
        'company_phone',                                                   #* Display the company phone number
    )
    
    #* Organize the fields in the admin panel
    fieldsets = (
        ('Contact Information',{
            'fields':('company_name','contact_email','company_phone', 'company_address')
        }),
        ('Institutional Texts',{
            'fields':('about_us','company_mission','company_vision'),
            'classes': ('wide',)
        }),
        ('Business Configuration',{
            'fields':('company_time_response_hours',)
        }),
    )

    #* Only allow one configuration to exist
    def has_add_permission(self, request):
        return not CompanyConfiguration.objects.exists()                  #* Prevent multiple configurations

#? <|--------------Order Items Admin Panel--------------|>
#* Admin configuration for the Order Items model
class OrderItemInline(admin.TabularInline):
    
    model = OrderItem                                                      #* Specify the model for the admin panel
    extra = 1                                                              #* Allow one extra empty form for adding new items

    #* Display simplified fields for inline editing
    fields = [
        'service',                                                         #* Field for selecting the service type
        'quantity',                                                        #* Field for entering the quantity of the service
        'description',                                                     #* Field for entering a description of the order item
        'length_dimensions',                                               #* Length dimension field
        'width_dimensions',                                                #* Width dimension field
        'height_dimensions',                                               #* Height dimension field
        'needs_custom_design',                                             #* Custom design checkbox
        'custom_design_price',                                             #* Custom design price field
        'design_file',                                                     #* Design file upload
        'estimated_unit_price',                                            #* Field for entering the estimated unit price of the service
        'final_unit_price',                                                #* Field for entering the final unit price of the service
    ]

    readonly_fields = ['estimated_unit_price']                            #* Make the estimated price read-only (auto-calculated)

#? <|--------------Order Admin Panel--------------|>
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    #* Display fields in the admin panel for Order
    list_display = (
        'order_number',
        'customer_name',
        'customer_email',
        'colored_state',
        'state',
        'estimated_formated_price',
        'final_formated_price',
        'created_at',
        'assigned_user',
        'see_items',
    )
    
    #* filter the fields in the admin panel for Order
    list_filter = [
        'state',                                                           #* Filter by order state
        'created_at',                                                      #* Filter by creation date
        'assigned_user',                                                   #* Filter by assigned user
    ]

    #* Search fields for the admin panel
    search_fields = [
        'order_number',                                                    #* Search by order number
        'customer_name',                                                   #* Search by customer name
        'customer_email',                                                  #* Search by customer email
        'customer_phone',                                                  #* Search by customer phone
    ]

    #* Fields that can be edited directly in the list view
    list_editable = [
        'state',                                                           #* Allow editing state directly
        'assigned_user',                                                   #* Allow editing of the assigned user directly in the list view
    ]

    #* Organize fields in the admin form
    fieldsets = (
        ('Order Information', {                                            #* Group order information fields
            'fields': ('order_number', 'state', 'assigned_user')
        }),
        ('Customer Details', {                                             #* Group customer details fields
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
            'classes': ('wide',)                                           #* Make the customer details fields wide
        }),
        ('Prices & Times', {                                               #* Group prices and times fields
            'fields': ('estimaded_price', 'final_price', 'estimated_completion_date_days')
        }),
        ('Process Dates', {                                                #* Group process dates fields
            'fields': ('created_at',),
            'classes': ('collapse',)                                       #* Collapse by default
        }),
        ('Admin Notes', {                                                  #* Group admin notes fields
            'fields': ('additional_notes',),
            'classes': ('wide',)                                           #* Make the admin notes fields wide
        })
    )
    
    #* Read-only fields (auto-generated or calculated)
    readonly_fields = [
        'order_number',                                                    #* Make the order number field read-only
        'created_at',                                                      #* Make the creation date field read-only
        'estimaded_price',                                                 #* Make the estimated price field read-only
    ]

    inlines = [OrderItemInline]                                            #* Include the OrderItemInline for managing order items

    ordering = ['-created_at']                                             #* Order the orders by creation date in descending order

    actions = ['mark_as_estimated', 'mark_as_completed']                   #* Define actions for marking orders as completed or canceled
    
    #* Function to display colored state
    def colored_state(self, obj):
        
        colors = {                                                         #* Define color classes for different states of the order
            'pending': '#ffc107',
            'estimated': '#17a2b8',
            'confirmed': '#28a745',
            'in_progress': '#6f42c1',
            'completed': '#28a745',
            'canceled': '#dc3545',
        }
    
        color = colors.get(obj.state, '#6c757d')                          #* Get the color class for the current state of the order
        return format_html(                                                #* Format the state with the appropriate color
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_state_display()                                 #* Capitalize the state for display
        )
    colored_state.short_description = 'State'                             #* Set the short description for the colored state field
    
    #* Function to display formatted estimated price
    def estimated_formated_price(self, obj):
        if obj.estimaded_price :
            return f"${obj.estimaded_price:.2f}"                           #* Format the estimated price for display
        return "-"
    estimated_formated_price.short_description = 'Estimated Price'        #* Set the short description for the estimated price field
    
    #* Function to display formatted final price
    def final_formated_price(self, obj):
        if obj.final_price:
            return f"${obj.final_price:.2f}"                               #* Format the final price for display
        return "Pending"                                                   #* Return "Pending" if the final price is not set
    final_formated_price.short_description = 'Final Price'                #* Set the short description for the final price field
    
    #* Function to display link to view order items
    def see_items(self, obj):
        count = obj.items.count()                                          #* Count the number of items in the order
        if count > 0:                                                      #* If there are items in the order
            url = reverse('admin:services_orderitem_changelist') + f'?order__id={obj.id}'
            return format_html(                                            #* Format the link to view the items in the order
                '<a href="{}">View Items ({})</a>',
                url, count                                                 #* Include the count of items in the link text
            )
            
        return "No Items"                                                  #* Return "No Items" if there are no items in the order
    see_items.short_description = 'Items'                                 #* Set the short description for the order items field

    #* Custom action to mark orders as estimated
    def mark_as_estimated(self, request, queryset):
        from django.utils import timezone
        for order in queryset:
            order.state = 'estimated'
            order.save()
        self.message_user(request, f"{queryset.count()} orders marked as estimated.")
    mark_as_estimated.short_description = 'Mark orders as Estimated'
    
    #* Custom action to mark orders as completed
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        for order in queryset:                                             #* Iterate through the selected orders
            order.state = 'completed'                                      #* Set the state of the order to 'completed'
            order.save()                                                   #* Save the changes to the order
        self.message_user(request, f"{queryset.count()} orders marked as completed.")
    mark_as_completed.short_description = 'Mark orders as Completed'       #* Set the short description for the mark as completed action


#? <|--------------Order Item Admin Panel con Secciones de Calculo--------------|>
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    
    #* Display fields in the list view
    list_display = [
        'order',                                                           #* Display the order associated with the order item
        'service',                                                         #* Display the service type of the order item
        'quantity',                                                        #* Display the quantity of the service in the order item
        'dimensions_display',                                              #* Display dimensions summary
        'needs_custom_design',                                             #* Display if needs custom design
        'custom_design_price',                                             #* Display custom design price
        'estimated_unit_price',                                            #* Display the estimated unit price of the service
        'final_unit_price',                                                #* Display the final unit price of the service
        'total_price_display',                                             #* Display total price (NEW)
        'calculated_price_display',                                        #* Display auto-calculated price
    ]
    
    #* Filter options
    list_filter = [
        'service',                                                         #* Filter by service type
        'order__state',                                                    #* Filter by order status
        'needs_custom_design',                                             #* Filter by custom design need
        'service__type',                                                   #* Filter by service type (plasma, laser, etc.)
    ]
    
    #* Search fields
    search_fields = [
        'order__order_number',                                             #* Search by order number
        'description',                                                     #* Search by description of the order item
        'service__name',                                                   #* Search by service name
    ]
    
    #* Make calculated prices readonly
    readonly_fields = [
        'estimated_unit_price',                                            #* Precio estimado original (no editable)
        'calculated_price_display',                                        #* Display calculated price
        'area_display',                                                    #* Display calculated area
        'total_price_display',                                             #* Display total price (NEW)
        'estimated_total_display',                                         #* Display estimated total (NEW)
    ]

    #* Dynamic fieldsets based on service type
    def get_fieldsets(self, request, obj=None):
        #* Base fieldsets that always appear
        base_fieldsets = [
            ('Order & Service Information', {
                'fields': ('order', 'service', 'quantity', 'description')
            }),
            ('Design Files & Custom Work', {
                'fields': ('design_file', 'needs_custom_design', 'custom_design_price'),
                'classes': ('wide',)
            }),
            ('Dimensions (in inches)', {
                'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions', 'area_display'),
                'description': 'All dimensions must be in inches'
            }),
            ('Final Pricing', {
                'fields': (
                    'estimated_unit_price',      # Row 1: Estimated unit price
                    'final_unit_price',           # Row 2: Final unit price
                    'total_price_display',        # Row 3: Total price with breakdown
                    'calculated_price_display'    # Row 4: Auto-calculated price
                ),
                'classes': ('wide',),
                'description': 'Unit prices and total calculations. Estimated price is from initial quote. Final price updates when you modify calculation fields above.'
            }),
        ]
        
        #* Add service-specific calculation fieldsets based on service type
        if obj and obj.service:
            service_type = obj.service.type
            
            if service_type == 'plasma':
                calculation_fieldset = ('Plasma Cutting Calculations', {
                    'fields': (
                        'plasma_design_programming_time',
                        'plasma_cutting_time', 
                        'plasma_post_process_time',
                        'plasma_material_cost',
                        'plasma_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Formula: ((A*3.33)+(B*16.5)+(C*1.5)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3*1.08'
                })
                #* Insert calculation fieldset before Final Pricing
                base_fieldsets.insert(-1, calculation_fieldset)
                
            elif service_type in ['laser_engraving', 'laser_cutting']:
                calculation_fieldset = ('Laser Cutting/Engraving Calculations', {
                    'fields': (
                        'laser_design_programming_time',
                        'laser_cutting_time',
                        'laser_post_process_time', 
                        'laser_material_cost',
                        'laser_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Formula: ((A*1.2)+(B*1.7)+(C*1)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3*1.08'
                })
                base_fieldsets.insert(-1, calculation_fieldset)
                
            elif service_type in ['3D_printing', 'resin_printing']:
                calculation_fieldset = ('3D Printing Calculations', {
                    'fields': (
                        'printing_design_programming_time',
                        'printing_time',
                        'printing_material_used',
                        'printing_post_process_time',
                        'printing_material_cost', 
                        'printing_consumables'
                    ),
                    'classes': ('collapse',),
                    'description': 'Formula: (((B*2.7)+((D+B)*1.5)+(E)+(((C/1000)/F))*2)+G)*1.6*1.08'
                })
                base_fieldsets.insert(-1, calculation_fieldset)
        
        return base_fieldsets

    #* Method to display dimensions summary
    def dimensions_display(self, obj):
        dims = []
        if obj.length_dimensions:
            dims.append(f"L:{obj.length_dimensions}")
        if obj.width_dimensions:
            dims.append(f"W:{obj.width_dimensions}")
        if obj.height_dimensions:
            dims.append(f"H:{obj.height_dimensions}")
        
        if dims:
            return " × ".join(dims) + " in"
        return "Not specified"
    dimensions_display.short_description = 'Dimensions'
    
    #* Method to display calculated area
    def area_display(self, obj):
        area = obj.get_area_square_inches()
        if area > 0:
            return f"{area:.2f} in²"
        return "Not calculated"
    area_display.short_description = 'Area (in²)'
    
    #* Method to display auto-calculated price with color coding
    def calculated_price_display(self, obj):
        if obj.service:
            calculated_price = obj.calculate_service_price()
            manual_price = obj.final_unit_price
            
            #* Ensure calculated_price is a float for formatting
            try:
                price_value = float(calculated_price)
            except (ValueError, TypeError):
                price_value = 0.0
            
            #* Format the price as string first
            formatted_price = f"${price_value:.2f}"
            
            #* Color code based on whether manual price matches calculated
            if manual_price and abs(float(manual_price) - price_value) > 0.01:
                #* Manual price differs from calculated
                color = '#ff6b35'  #* Orange for different
                status = 'Manual Override'
            else:
                #* Using calculated price
                color = '#28a745'  #* Green for auto-calculated
                status = 'Auto-Calculated'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span><br>'
                '<small style="color: gray;">{}</small>',
                color, formatted_price, status
            )
        return "No service selected"
    calculated_price_display.short_description = 'Auto-Calculated Price'
    
    #* Method to display total price based on final unit price
    def total_price_display(self, obj):
        if obj.final_unit_price and obj.quantity:
            total_service = float(obj.final_unit_price) * obj.quantity
            
            #* Add custom design price if applicable
            total_final = total_service
            if obj.needs_custom_design and obj.custom_design_price:
                total_final += float(obj.custom_design_price)
            
            #* Build breakdown parts as plain strings
            breakdown_parts = []
            breakdown_parts.append(f"${obj.final_unit_price:.2f} × {obj.quantity} = ${total_service:.2f}")
            
            if obj.needs_custom_design and obj.custom_design_price:
                breakdown_parts.append(f"+ Custom Design: ${obj.custom_design_price:.2f}")
            
            # Build the complete HTML manually without format_html to avoid SafeString issues
            breakdown_text = "<br>".join(breakdown_parts)
            
            html = f'''
            <div style="text-align: center;">
                <div style="font-size: 16px; font-weight: bold; color: #059669; margin-bottom: 4px;">
                    ${total_final:.2f} MXN
                </div>
                <div style="font-size: 11px; color: #6b7280; line-height: 1.3;">
                    {breakdown_text}
                </div>
            </div>
            '''
            
            return mark_safe(html)
        return format_html('<span style="color: #ef4444;">Not calculated</span>')
    total_price_display.short_description = 'Total Price'
    
    #* Method to display estimated total price for comparison
    def estimated_total_display(self, obj):
        if obj.quantity:
            # Try estimated_unit_price first, fall back to final_unit_price if estimated is not set
            unit_price = obj.estimated_unit_price if obj.estimated_unit_price else obj.final_unit_price
            
            if unit_price:
                total_service = float(unit_price) * obj.quantity
                
                #* Add custom design price if applicable
                total_estimated = total_service
                if obj.needs_custom_design and obj.custom_design_price:
                    total_estimated += float(obj.custom_design_price)
                
                # Show different styling based on whether we're using estimated or final price
                if obj.estimated_unit_price:
                    label = "Initial Estimate"
                    color = "#6b7280"
                else:
                    label = "Based on Final Price"
                    color = "#9ca3af"
                
                return format_html(
                    '<div style="text-align: center; color: {};">'
                    '<div style="font-size: 14px;">${:.2f} MXN</div>'
                    '<div style="font-size: 10px;">{}</div>'
                    '</div>',
                    color, total_estimated, label
                )
        return format_html('<span style="color: #6b7280;">Not calculated</span>')
    estimated_total_display.short_description = 'Estimated Total'
    
    #* Method to show price comparison
    def price_comparison_display(self, obj):
        estimated_total = obj.get_estimated_total_with_design()
        final_total = obj.get_final_total_with_design()
        
        if estimated_total > 0 and final_total > 0:
            difference = final_total - estimated_total
            percentage = (difference / estimated_total) * 100
            
            if abs(difference) < 0.01:  # Practically the same
                color = '#10b981'  # Green
                status = 'Same as estimate'
                arrow = '='
            elif difference > 0:  # Final price higher
                color = '#ef4444'  # Red
                status = f'${difference:.2f} higher ({percentage:+.1f}%)'
                arrow = '↑'
            else:  # Final price lower
                color = '#10b981'  # Green
                status = f'${abs(difference):.2f} lower ({percentage:.1f}%)'
                arrow = '↓'
            
            return format_html(
                '<div style="text-align: center;">'
                '<div style="font-size: 20px; color: {}; font-weight: bold;">{}</div>'
                '<div style="font-size: 11px; color: #6b7280;">{}</div>'
                '</div>',
                color, arrow, status
            )
        return format_html('<span style="color: #6b7280;">-</span>')
    price_comparison_display.short_description = 'vs Estimate'
    
    #* Save method override to recalculate when admin saves
    def save_model(self, request, obj, form, change):
        #* Si es un objeto existente (change=True), mantener el estimated_unit_price original
        if change and obj.estimated_unit_price:
            #* Guardar el precio estimado original
            original_estimated_price = obj.estimated_unit_price
        else:
            #* Si es nuevo, calcular el precio estimado
            original_estimated_price = obj.calculate_service_price() if obj.service else 0
        
        #* SIEMPRE calcular el precio final basado en los campos actuales
        if obj.service:
            calculated_final_price = obj.calculate_service_price()
            
            #* Actualizar SOLO el final_unit_price con el nuevo cálculo
            obj.final_unit_price = calculated_final_price
            
            #* Mantener o establecer el estimated_unit_price original
            obj.estimated_unit_price = original_estimated_price
        
        #* Guardar el objeto
        super().save_model(request, obj, form, change)
        
        #* Update order totals
        if obj.order:
            #* Recalcular total de la orden basado en final_unit_price si existe, sino estimated_unit_price
            total_estimated = 0
            total_final = 0
            
            for item in obj.order.items.all():
                if item.estimated_unit_price:
                    total_estimated += float(item.estimated_unit_price) * item.quantity
                if item.final_unit_price:
                    total_final += float(item.final_unit_price) * item.quantity
            
            #* Actualizar precios de la orden
            obj.order.estimaded_price = total_estimated
            if total_final > 0:
                obj.order.final_price = total_final
            
            obj.order.save()


#? <|--------------Custom Admin Actions--------------|>

#* Function to create the 5 base services automatically
def create_base_services():
    
    base_services_data = [
        {
            'type': 'plasma',
            'name': 'Plasma Cutting',
            'short_description': 'Precision metal cutting with plasma technology',
            'is_base_service': True,
            'order_display': 1
        },
        {
            'type': 'laser_engraving', 
            'name': 'Laser Engraving',
            'short_description': 'Detailed engraving on wood and other materials',
            'is_base_service': True,
            'order_display': 2
        },
        {
            'type': 'laser_cutting',
            'name': 'Laser Cutting', 
            'short_description': 'Precise cutting of wood and thin materials',
            'is_base_service': True,
            'order_display': 3
        },
        {
            'type': '3D_printing',
            'name': '3D Printing',
            'short_description': 'Additive manufacturing with filament technology',
            'is_base_service': True, 
            'order_display': 4
        },
        {
            'type': 'resin_printing',
            'name': 'Resin Printing',
            'short_description': 'High-detail 3D printing with resin technology',
            'is_base_service': True,
            'order_display': 5
        }
    ]
    
    for service_data in base_services_data:
        TypeService.objects.get_or_create(
            type=service_data['type'],
            defaults=service_data
        )


#? <|--------------Change Admin Panel Titles--------------|>

admin.site.site_header = "AGAH Solutions Admin"                           #* Set the site header for the admin panel
admin.site.site_title = "AGAH Solutions Admin Portal"                     #* Set the site title for the admin panel
admin.site.index_title = "Welcome to the AGAH Solutions Admin Portal"     #* Set the index title for the admin panel