#? Admin configuration for the services app
from django.contrib import admin                                                   #* Django admin import
from django.utils.html import format_html                                          #* HTML formatting for admin display
from django.forms import ModelForm                                                 #* Model forms for custom form handling
from django.core.exceptions import ValidationError                                 #* Validation error handling
from .models import TypeService, Order, OrderItem, CompanyConfiguration           #* Import all models from services app


#? <|--------------Custom Form for Type Service Admin--------------|>
class TypeServiceForm(ModelForm):
    """
    Custom form for TypeService admin
    Purpose: Simplify the add form to only show name field for new services
    """
    """
    Custom form for TypeService admin
    Purpose: Simplify the add form to only show name field for new services
    """
    class Meta:
        model = TypeService                                                         #* Which model this form is for
        fields = '__all__'                                                          #* Include all fields
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom behavior
        - For new services: Only focus on name field
        - Auto-generate type from name
        """
        super().__init__(*args, **kwargs)
        if not self.instance.pk:                                                    #* Only for new objects (no primary key yet)
            #* For new services, only show name and type fields
            self.fields['type'].widget.attrs['placeholder'] = 'Auto-generated from name'  #* Placeholder text
            self.fields['type'].required = False                                    #* Make type field optional
            #* Focus on the name field when form loads
            self.fields['name'].widget.attrs['autofocus'] = True                    #* Auto-focus on name field


#? <|--------------Type Service Admin Configuration--------------|>
@admin.register(TypeService)                                                       #* Register TypeService model with admin
class TypeServiceAdmin(admin.ModelAdmin):
    """
    Admin configuration for TypeService model
    Features:
    - Simplified form for adding new services (only name required)
    - Visual status indicators with colors
    - Mass actions for activate/deactivate
    - Auto-generation of type and order_display
    """
    form = TypeServiceForm                                                          #* Use custom form defined above
    
    #* Fields to display in the list view (like columns in a table)
    list_display = ['name', 'type', 'active_display', 'order_display', 'get_price_display', 'is_base_service', 'active']
    
    #* Filters that appear on the right side of the list view
    list_filter = ['active', 'is_base_service', 'type']                            #* Filter by active status, base service, and type
    
    #* Fields that can be searched from the search box
    search_fields = ['name', 'type', 'description']                                #* Search by name, type, or description
    
    #* Fields that can be edited directly in the list view (without opening detail)
    list_editable = ['active']                                                      #* Can toggle active status from list
    
    #* Fields that cannot be edited (read-only)
    readonly_fields = ['type', 'order_display']                                    #* Auto-generated fields
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Basic Information', {                                                     #* First section: Basic info
            'fields': ('name', 'type')
        }),
        ('Content', {                                                               #* Second section: Content
            'fields': ('description', 'short_description', 'principal_image')
        }),
        ('Pricing & Display', {                                                     #* Third section: Pricing and display
            'fields': ('base_price', 'active', 'order_display', 'is_base_service')
        }),
    )
    
    #* Special fieldset for adding new services (simpler form)
    add_fieldsets = (
        ('Add New Service', {
            'classes': ('wide',),                                                   #* Make form wider
            'fields': ('name',),                                                    #* Only show name field
            'description': 'Just enter the service name. Everything else will be auto-generated or can be edited later.'
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """
        Choose which fieldsets to use based on whether we're adding or editing
        - Adding new: Use simplified add_fieldsets
        - Editing existing: Use full fieldsets
        """
        if not obj:                                                                 #* Adding new object
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)                                  #* Editing existing object
    
    def active_display(self, obj):
        """
        Custom display method for active status with colors and icons
        Returns: HTML with colored text and checkmark/X icon
        """
        if obj.active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    active_display.short_description = 'Status'                                    #* Column header name
    active_display.admin_order_field = 'active'                                    #* Allow sorting by this field
    
    #* Custom mass actions that appear in the dropdown above the list
    actions = ['activate_services', 'deactivate_services']
    
    def activate_services(self, request, queryset):
        """
        Mass action to activate selected services
        Updates all selected services to active=True
        """
        updated = queryset.update(active=True)                                      #* Update all selected objects
        self.message_user(request, f'{updated} services activated.')               #* Show success message
    activate_services.short_description = 'Activate selected services'            #* Text shown in dropdown
    
    def deactivate_services(self, request, queryset):
        """
        Mass action to deactivate selected services
        Updates all selected services to active=False
        """
        updated = queryset.update(active=False)                                     #* Update all selected objects
        self.message_user(request, f'{updated} services deactivated.')             #* Show success message
    deactivate_services.short_description = 'Deactivate selected services'        #* Text shown in dropdown


#? <|--------------Order Item Inline Admin--------------|>
class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem within Order admin
    Purpose: Allow editing order items directly from the order detail page
    Layout: Tabular (table-like) instead of stacked (form-like)
    """
    model = OrderItem                                                               #* Model to inline
    extra = 0                                                                       #* Number of empty forms to show
    
    #* Fields to show in the inline table
    fields = [
        'service', 'description', 'quantity',                                      #* Basic info
        'length_dimensions', 'width_dimensions', 'height_dimensions',              #* Dimensions
        'design_file', 'needs_custom_design', 'custom_design_price',               #* Design and pricing
        'estimated_unit_price', 'final_unit_price'                                 #* Calculated prices
    ]
    
    #* Fields that are read-only in the inline
    readonly_fields = ['estimated_unit_price']                                     #* Auto-calculated field


#? <|--------------Order Admin Configuration--------------|>
@admin.register(Order)                                                             #* Register Order model with admin
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model
    Features:
    - Inline editing of order items
    - Color-coded status display
    - User type indicators
    - Calculated totals display
    - Mass status change actions
    """
    inlines = [OrderItemInline]                                                     #* Include OrderItem inline
    
    #* Fields to display in the list view
    list_display = [
        'order_number', 'customer_name', 'customer_email',                         #* Basic order info
        'user_display', 'state_display', 'created_at',                             #* User and status info
        'get_total_items', 'get_estimated_total', 'state'                           #* Calculated fields and state
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'state', 'created_at'                                                      #* Filter by status and date
    ]
    
    #* Searchable fields
    search_fields = [
        'order_number', 'customer_name', 'customer_email',                         #* Order and customer info
        'user__email', 'user__first_name', 'user__last_name'                       #* User info
    ]
    
    #* Fields that can be edited directly from the list view
    list_editable = ['state']                                                       #* Can change status from list
    
    #* Read-only fields in the detail form
    readonly_fields = [
        'order_number', 'created_at', 'user',                                      #* System-generated fields
        'get_total_items', 'get_estimated_total', 'get_final_total'                #* Calculated fields
    ]
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Order Information', {                                                     #* Order basics
            'fields': ('order_number', 'state', 'created_at')
        }),
        ('Customer Information', {                                                  #* Customer details
            'fields': ('user', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Order Details', {                                                         #* Order specifics
            'fields': ('additional_notes', 'assigned_user')
        }),
        ('Pricing Information', {                                                   #* Pricing details
            'fields': ('estimaded_price', 'final_price', 'estimated_completion_date_days')
        }),
        ('Calculated Totals', {                                                     #* Auto-calculated totals
            'fields': ('get_total_items', 'get_estimated_total', 'get_final_total'),
            'classes': ('collapse',)                                                #* Collapsible section
        }),
    )
    
    def user_display(self, obj):
        """
        Custom display for user field with icons and colors
        Shows: 👤 for registered users, 👥 for guest orders
        """
        if obj.user:
            return format_html(
                '<span style="color: blue;">👤 {}</span>',                         #* Blue icon for registered users
                obj.user.get_full_name()
            )
        else:
            return format_html('<span style="color: gray;">👥 Guest</span>')        #* Gray icon for guest orders
    user_display.short_description = 'User'                                        #* Column header
    user_display.admin_order_field = 'user'                                        #* Allow sorting
    
    def state_display(self, obj):
        """
        Custom display for order state with color-coded badges
        Each state has its own color for quick visual identification
        """
        colors = {
            'pending': 'orange',                                                    #* Orange for pending
            'estimated': 'blue',                                                    #* Blue for estimated
            'confirmed': 'green',                                                   #* Green for confirmed
            'in_progress': 'purple',                                                #* Purple for in progress
            'completed': 'darkgreen',                                               #* Dark green for completed
            'canceled': 'red',                                                      #* Red for canceled
        }
        
        color = colors.get(obj.state, 'gray')                                       #* Default to gray if state not found
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_state_display()
        )
    state_display.short_description = 'Status'                                     #* Column header
    state_display.admin_order_field = 'state'                                      #* Allow sorting
    
    def get_total_items(self, obj):
        """
        Calculate and display total number of items in the order
        """
        return obj.items.count()                                                    #* Count related OrderItems
    get_total_items.short_description = 'Items'                                    #* Column header
    
    def get_estimated_total(self, obj):
        """
        Calculate and display total estimated price for all items
        Includes custom design prices if applicable
        """
        total = sum(item.get_estimated_total_with_design() for item in obj.items.all())
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"             #* Format with currency
    get_estimated_total.short_description = 'Estimated Total'                      #* Column header
    
    def get_final_total(self, obj):
        """
        Calculate and display total final price for all items
        Includes custom design prices if applicable
        """
        total = sum(item.get_final_total_with_design() for item in obj.items.all())
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"             #* Format with currency
    get_final_total.short_description = 'Final Total'                              #* Column header
    
    #* Custom mass actions for changing order status
    actions = ['mark_as_estimated', 'mark_as_confirmed', 'mark_as_in_progress', 'mark_as_completed']
    
    def mark_as_estimated(self, request, queryset):
        """Mass action to mark orders as estimated"""
        updated = queryset.update(state='estimated')
        self.message_user(request, f'{updated} orders marked as estimated.')
    mark_as_estimated.short_description = 'Mark as Estimated'
    
    def mark_as_confirmed(self, request, queryset):
        """Mass action to mark orders as confirmed"""
        updated = queryset.update(state='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark as Confirmed'
    
    def mark_as_in_progress(self, request, queryset):
        """Mass action to mark orders as in progress"""
        updated = queryset.update(state='in_progress')
        self.message_user(request, f'{updated} orders marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as In Progress'
    
    def mark_as_completed(self, request, queryset):
        """Mass action to mark orders as completed"""
        updated = queryset.update(state='completed')
        self.message_user(request, f'{updated} orders marked as completed.')
    mark_as_completed.short_description = 'Mark as Completed'


#? <|--------------Order Item Admin Configuration--------------|>
@admin.register(OrderItem)                                                         #* Register OrderItem model with admin
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for OrderItem model
    Features:
    - Link to parent order
    - Dimensions display formatting
    - Collapsible calculation sections for each service type
    - Price calculations display
    """
    
    #* Fields to display in the list view
    list_display = [
        'order_link', 'service', 'quantity', 'dimensions_display',                 #* Basic item info
        'needs_custom_design', 'custom_design_price',                              #* Design info
        'estimated_unit_price', 'final_unit_price', 'get_total_display'            #* Pricing info
    ]
    
    #* Filters for the right sidebar
    list_filter = [
        'service__type', 'needs_custom_design', 'service'                          #* Filter by service type, design need, service
    ]
    
    #* Searchable fields
    search_fields = [
        'order__order_number', 'order__customer_name',                             #* Order info
        'service__name', 'description'                                             #* Item info
    ]
    
    #* Read-only fields
    readonly_fields = ['estimated_unit_price']                                     #* Auto-calculated field
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Order & Service', {                                                       #* Basic order and service info
            'fields': ('order', 'service', 'description', 'quantity')
        }),
        ('Dimensions', {                                                            #* Item dimensions
            'fields': ('length_dimensions', 'width_dimensions', 'height_dimensions')
        }),
        ('Files & Design', {                                                        #* Design files and custom design
            'fields': ('design_file', 'needs_custom_design', 'custom_design_price')
        }),
        ('Pricing', {                                                               #* Price information
            'fields': ('estimated_unit_price', 'final_unit_price')
        }),
        ('Plasma Cutting Calculations', {                                           #* Plasma-specific calculation fields
            'fields': (
                'plasma_design_programming_time', 'plasma_cutting_time',
                'plasma_post_process_time', 'plasma_material_cost', 'plasma_consumables'
            ),
            'classes': ('collapse',)                                                #* Collapsible section
        }),
        ('Laser Cutting/Engraving Calculations', {                                 #* Laser-specific calculation fields
            'fields': (
                'laser_design_programming_time', 'laser_cutting_time',
                'laser_post_process_time', 'laser_material_cost', 'laser_consumables'
            ),
            'classes': ('collapse',)                                                #* Collapsible section
        }),
        ('3D Printing Calculations', {                                              #* 3D printing-specific calculation fields
            'fields': (
                'printing_design_programming_time', 'printing_time', 'printing_material_used',
                'printing_post_process_time', 'printing_material_cost', 'printing_consumables'
            ),
            'classes': ('collapse',)                                                #* Collapsible section
        }),
    )
    
    def order_link(self, obj):
        """
        Create a clickable link to the parent order
        Allows easy navigation from item to order
        """
        return format_html(
            '<a href="/admin/services/order/{}/change/">{}</a>',                    #* Create HTML link
            obj.order.id, obj.order.order_number
        )
    order_link.short_description = 'Order'                                         #* Column header
    order_link.admin_order_field = 'order'                                         #* Allow sorting
    
    def dimensions_display(self, obj):
        """
        Format dimensions for better readability
        Shows: Length × Width × Height in inches
        """
        if obj.length_dimensions and obj.width_dimensions:
            dims = f"{obj.length_dimensions} × {obj.width_dimensions}"              #* Length × Width
            if obj.height_dimensions:
                dims += f" × {obj.height_dimensions}"                               #* Add height if present
            return f"{dims} in"                                                     #* Add units
        return "Not specified"                                                      #* No dimensions provided
    dimensions_display.short_description = 'Dimensions'                            #* Column header
    
    def get_total_display(self, obj):
        """
        Display total price for this item (including design if applicable)
        Shows final price with proper formatting
        """
        total = obj.get_final_total_with_design()                                   #* Get total including design
        return f"${total:,.2f} MXN" if total > 0 else "Not calculated"             #* Format with currency
    get_total_display.short_description = 'Total Price'                            #* Column header


#? <|--------------Company Configuration Admin--------------|>
@admin.register(CompanyConfiguration)                                              #* Register CompanyConfiguration model
class CompanyConfigurationAdmin(admin.ModelAdmin):
    """
    Admin configuration for CompanyConfiguration model
    Features:
    - Only one instance allowed (singleton pattern)
    - Cannot be deleted (protection)
    - Organized fieldsets for easy editing
    """
    
    #* Fields to display in the list view
    list_display = ['company_name', 'contact_email', 'company_phone', 'company_time_response_hours']
    
    #* Organization of fields in the detail form
    fieldsets = (
        ('Basic Information', {                                                     #* Company contact info
            'fields': ('company_name', 'contact_email', 'company_phone', 'company_address')
        }),
        ('About Company', {                                                         #* Company description
            'fields': ('about_us', 'company_mission', 'company_vision')
        }),
        ('Business Configuration', {                                                #* Business settings
            'fields': ('company_time_response_hours',)
        }),
    )
    
    def has_add_permission(self, request):
        """
        Only allow one company configuration to exist
        Prevents creating multiple company configurations
        """
        return not CompanyConfiguration.objects.exists()                           #* Only allow if none exists
    
    def has_delete_permission(self, request, obj=None):
        """
        Don't allow deletion of company configuration
        Protects essential company data
        """
        return False                                                                #* Never allow deletion


#? <|--------------Custom Admin Actions & Utilities--------------|>

def create_base_services():
    """
    Function to create the 5 base services automatically
    Purpose: Initialize the system with the main services AGAH offers
    Usage: Run this in Django shell after setting up the database
    
    Services created:
    1. Plasma Cutting
    2. Laser Engraving  
    3. Laser Cutting
    4. 3D Printing
    5. Resin Printing
    """
    
    base_services_data = [
        {
            'type': 'plasma',                                                       #* Service type identifier
            'name': 'Plasma Cutting',                                               #* Display name
            'short_description': 'Precision metal cutting with plasma technology', #* Brief description
            'is_base_service': True,                                                #* Mark as base service
            'order_display': 1                                                      #* Display order
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
    
    #* Create each service if it doesn't already exist
    for service_data in base_services_data:
        TypeService.objects.get_or_create(                                          #* Create only if doesn't exist
            type=service_data['type'],                                              #* Find by type
            defaults=service_data                                                   #* Use this data if creating new
        )


#? <|--------------Admin Panel Customization--------------|>

#* Customize the admin panel header and titles
admin.site.site_header = "AGAH Solutions Admin"                                    #* Main header text
admin.site.site_title = "AGAH Solutions Admin Portal"                             #* Browser tab title
admin.site.index_title = "Welcome to the AGAH Solutions Admin Portal"             #* Welcome message on admin home
