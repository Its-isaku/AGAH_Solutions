#? Models for the services app
from django.db import models                                                                                                #* models import for database tables 
from django.contrib.auth.models import User                                                                                 #* User model import for user-related fields
from django.utils import timezone                                                                                           #* timezone import for date and time handling

#? <|--------------Type of service Model--------------|>
class TypeService(models.Model): 

    #* Base service types - Only the 5 main services your company offers
    BASE_TYPES = [
        ('plasma', 'Plasma Cutting'),
        ('laser_engraving', 'Laser Engraving'),
        ('laser_cutting', 'Laser Cutting'),
        ('3D_printing', '3D Printing'),
        ('resin_printing', 'Resin Printing'),
    ]
    
    #* Use only base types (no additional types for your company)
    ALL_TYPES = BASE_TYPES
    
    #* Fields for the TypeService model
    type = models.CharField(
        max_length=50,
        unique=True,                                                                                                        #* Ensures each type is unique / cant be duplicated
        blank=True,                                                                                                         #* Allow blank - will be auto-generated from name
        help_text="Type of service offered (auto-generated from name)"
    )
    
    #* name fields for the service type 
    name = models.CharField(
        max_length=100,
        help_text="Name of the service type"
    )

    #* description fields for the service type
    description = models.TextField(
        blank=True,                                                                                                         #* Allow empty initially
        help_text="Description of the service type"
    )
    
    #* short description field for the service type
    short_description = models.CharField(
        max_length=200,
        blank=True,                                                                                                         #* Allow empty initially
        help_text="Short description of the service type"
    )
    
    #* base price field for the service type
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,                                                                                                          #* Allow NULL for services without initial price
        blank=True,                                                                                                         #* Allow empty initially
        help_text="Base price for the service type"
    )
    
    #* image field for the service type 
    principal_image = models.ImageField(
        upload_to='service_images/',                                                                                         #* Directory to upload images
        blank=True,                                                                                                          #* Allows the field to be blank
        null=True,                                                                                                           #* Allows the field to be null
        help_text="Principal image for the service type"
    )
    
    #* active field to indicate if the service type is active
    active = models.BooleanField(
        default=True,                                                                                                        #* Default value is True
        help_text="If active show the service type in the frontend"
    )
    
    #* order display field - now automatic
    order_display = models.IntegerField(
        default=0,
        help_text="Order display for the service type (auto-assigned)"
    )
    
    #* Indicates if this is one of the 5 base services or an additional one
    is_base_service = models.BooleanField(
        default=False,
        help_text="Indicates if this is one of the 5 base services"
    )
    
    #* Metadata class for the TypeService model 
    class Meta:
        ordering = ['order_display', 'name']                                                                                 #* Orders by order_display and then by name
        verbose_name = "Type of Service"                                                                                     #* Human-readable name for the model
        verbose_name_plural = "Types of Services"                                                                            #* Human-readable plural name for the model     
    
    def __str__(self):         
        return self.name                                                                                                     #* Returns the name of the service type when the object is printed
    
    #* Method to auto-generate type from name and assign order_display
    def save(self, *args, **kwargs):
        if not self.type:                                                                                                    #* If type is not set, auto-generate from name
            #* Generate type from name (lowercase, replace spaces with underscores)
            self.type = self.name.lower().replace(' ', '_').replace('-', '_')
            #* Remove special characters and limit length
            import re
            self.type = re.sub(r'[^a-z0-9_]', '', self.type)[:50]
            
            #* Check if this type already exists, if so add number
            base_type = self.type
            counter = 1
            while TypeService.objects.filter(type=self.type).exists():
                self.type = f"{base_type}_{counter}"
                counter += 1
        
        if not self.order_display or self.order_display == 0:                                                               #* If order_display is not set
            from django.db.models import Max
            max_order = TypeService.objects.aggregate(Max('order_display'))['order_display__max']                          #* Get the maximum order_display value
            self.order_display = (max_order or 0) + 1                                                                       #* Set order_display to max + 1
        super().save(*args, **kwargs)                                                                                       #* Call the parent save method
    
    def get_price_display(self):
        if self.base_price:
            return f"${self.base_price:.2f} MXN"                                                                             #* Returns the base price formatted as a string with two decimal places
        return "Price not set"

#? <|--------------Company Configuration Model--------------|>
class CompanyConfiguration(models.Model):
    
    #* Company name field 
    company_name = models.CharField(
        max_length=100,
        default="AGAH Solutions",
        help_text="AGAH Solutions"
    )
    
    #* Company email field
    contact_email = models.EmailField(
        help_text="Contact email for the company"
    )
    
    #* Company phone field
    company_phone = models.CharField(
        max_length=150,
        help_text="Contact phone number for the company"
    )

    #* Company address field
    company_address = models.TextField(
        help_text="Contact address for the company"
    )

    #* About Us field
    about_us = models.TextField(
        help_text="About us section for the company"
    )

    #* Company mission field
    company_mission = models.TextField(
        blank=True,
        help_text="Company mission statement"
    )

    #* Company vision field
    company_vision = models.TextField(
        blank=True,
        help_text="Company vision statement"
    )

    #* company time response hours field
    company_time_response_hours = models.IntegerField(
        default=24,
        help_text="Average response time in hours"
    )
    
    #* Company Meta 
    class Meta:
        verbose_name_plural = "Company Configurations"                                                                      #* Human-readable plural name for the model
        
    def __str__(self):
        return self.company_name                                                                                            #* Returns the company name when the object is printed


#? <|--------------Order Model--------------|>
class Order(models.Model):
    
    #* Fields for the Order model
    STATES = [
        ('pending', 'Pending'),
        ('estimated', 'Estimated - waiting for confirmation'),
        ('confirmed', 'Confirmed by the customer'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    
    #* Unique order number field
    order_number = models.CharField(
        max_length=20,
        unique=True,                                                                                                        #* Ensures each order number is unique
        blank=True,                                                                                                         #* Allows the field to be blank
        help_text="Unique order number for the order"
    )

    #* Customer name field 
    customer_name = models.CharField(
        max_length=100,
        help_text="Name of the customer placing the order"
    )
    
    #* Customer email field
    customer_email = models.EmailField(
        help_text="Email of the customer placing the order"
    )
    
    #* Customer phone field
    customer_phone = models.CharField(
        max_length=15, 
        help_text="Phone number of the customer placing the order"
    )

    #* Order state field
    state = models.CharField(
        max_length=20,
        choices=STATES,                                                                                                     #* Choices for the state of the order
        default='pending',                                                                                                  #* Default state is pending
        help_text="Current state of the order"
    )

    #* Order creation timestamp field 
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the order was created"
    )

    #* Order estimated price field 
    estimaded_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Automated estimated price for the order"
    )

    #* Order final price field
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final price for the order"
    )

    #* estimated completion date field 
    estimated_completion_date_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated completion time in days"
    )
    
    #* Assigned user field
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,                                                                                         #* If the user is deleted, set this field to null
        null=True,
        blank=True,
        help_text="User assigned to the order"
    )
    
    #* additional notes field
    additional_notes = models.TextField(
        blank=True,
        help_text="Additional notes for the order"
    )

    #* Metadata class for the Order model
    class Meta:
        ordering = ['-created_at']                                                                                         #* Orders are ordered by creation date (newest first) 
        verbose_name = "Order"                                                                                             #* Human-readable name for the model
        verbose_name_plural = "Orders"                                                                                     #* Human-readable plural name for the model
        
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"                                                         #* Returns a string representation of the order with order number and customer name
    
    #* Method to save the order and generate a unique order number if not set
    def save(self, *args, **kwargs):
        if not self.order_number:                                                                                          #* If order number is not set, generate a unique one
            today = timezone.now().date()                                                                                  #* Get the current date and time
            self.order_number = f"ORD-{today.strftime('%Y%m%d')}-{self.pk or '001'}"                                       #* Generate a unique order number
        super().save(*args, **kwargs)                                                                                      #* Call the parent save method

    #* Method to calculate the estimated price of the order based on items
    def calculate_estimated_price(self):
        total = sum(item.estimated_unit_price * item.quantity              
                    for item in self.items.all()
                    if item.estimated_unit_price)
        return total
    
    def get_state_display_color(self):
        colors = {
            'pending': 'text-gray-500',
            'estimated': 'text-yellow-500',
            'confirmed': 'text-blue-500',
            'in_progress': 'text-green-500',
            'completed': 'text-purple-500',
            'canceled': 'text-red-500',
        }
        return colors.get(self.state, 'text-gray-500')                                                                     #* Returns the color class for the current state of the order

#? <|--------------Order Item Model--------------|>

class OrderItem(models.Model):

    #* order foreign key field
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',                                                                                                 #* Related name for accessing order items from the order
        help_text="Order to which this item belongs"
    )

    #* type of service foreign key field
    service = models.ForeignKey(
        TypeService,
        on_delete=models.CASCADE,
        help_text="Type of service requested"
    )
    
    #* description field for the order item
    description = models.TextField(
        help_text="Description of the service the consumer wants"
    )
    
    #* design file field for the order item    
    design_file = models.FileField(
        upload_to='design_files/%Y/%m/',                                                                                     #* Directory to upload design files organized by year/month
        blank=True,                                                                                                          #* Allows the field to be blank
        null=True,                                                                                                           #* Allows the field to be null
        help_text="Design file for the order item"
    )
    
    #* Item quantity field 
    quantity = models.IntegerField(
        default=1,
        help_text="Quantity of the service the consumer wants"
    )

    #* Length dimensions field
    length_dimensions = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length of the design in inches"
    )

    #* width dimensions field 
    width_dimensions = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width of the design in inches"
    )
    
    #* height dimensions field
    height_dimensions = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height of the design in inches"
    )
    
    #* Estimated unit price field 
    estimated_unit_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Estimated unit price for the order item"                                                                #* Estimated price for the order item
    )
    
    #* Final unit price field 
    final_unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final unit price for the order item"
    )
    
    #* Indicates if this item needs custom design service
    needs_custom_design = models.BooleanField(
        default=False,
        help_text="Indicates if this item needs custom design service"
    )
    
    #* Custom design price field - individual per item
    custom_design_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price for custom design service for this specific item"
    )
    
    #? <|--------------Plasma Cutting Calculation Fields--------------|>
    #* A: Diseño y Programacion (60min minimo)
    plasma_design_programming_time = models.IntegerField(
        default=60,
        null=True,
        blank=True,
        help_text="Design and programming time in minutes (minimum 60)"
    )
    
    #* B: Corte (30 min minimo)
    plasma_cutting_time = models.IntegerField(
        default=30,
        null=True,
        blank=True,
        help_text="Cutting time in minutes (minimum 30)"
    )
    
    #* C: Post-proceso (60min minimo)
    plasma_post_process_time = models.IntegerField(
        default=60,
        null=True,
        blank=True,
        help_text="Post-process time in minutes (minimum 60)"
    )
    
    #* E: Costo de Material (Placa 4'x8')
    plasma_material_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Material cost for 4'x8' plate"
    )
    
    #* G: Consumibles (162.30 como default)
    plasma_consumables = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=162.30,
        null=True,
        blank=True,
        help_text="Consumables cost (default 162.30)"
    )
    
    #? <|--------------Laser Cutting/Engraving Calculation Fields--------------|>
    #* A: Diseño y Programacion (30min minimo)
    laser_design_programming_time = models.IntegerField(
        default=30,
        null=True,
        blank=True,
        help_text="Design and programming time in minutes (minimum 30)"
    )
    
    #* B: Corte (10 min minimo)
    laser_cutting_time = models.IntegerField(
        default=10,
        null=True,
        blank=True,
        help_text="Cutting time in minutes (minimum 10)"
    )
    
    #* C: Post-proceso (10min minimo)
    laser_post_process_time = models.IntegerField(
        default=10,
        null=True,
        blank=True,
        help_text="Post-process time in minutes (minimum 10)"
    )
    
    #* E: Costo de Material (Hoja 4'x8')
    laser_material_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Material cost for 4'x8' sheet"
    )
    
    #* G: Consumibles (30 como default)
    laser_consumables = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=30.00,
        null=True,
        blank=True,
        help_text="Consumables cost (default 30.00)"
    )
    
    #? <|--------------3D Printing Calculation Fields--------------|>
    #* A: Diseño y Programacion (60min minimo)
    printing_design_programming_time = models.IntegerField(
        default=60,
        null=True,
        blank=True,
        help_text="Design and programming time in minutes (minimum 60)"
    )
    
    #* B: Impresion (30 min minimo)
    printing_time = models.IntegerField(
        default=30,
        null=True,
        blank=True,
        help_text="Printing time in minutes (minimum 30)"
    )
    
    #* C: Material utilizado (g)
    printing_material_used = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Material used in grams"
    )
    
    #* D: Post-proceso (60min minimo)
    printing_post_process_time = models.IntegerField(
        default=60,
        null=True,
        blank=True,
        help_text="Post-process time in minutes (minimum 60)"
    )
    
    #* F: Costo de Material (Rollo de 1Kg) (350 por default)
    printing_material_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=350.00,
        null=True,
        blank=True,
        help_text="Material cost per 1Kg roll (default 350.00)"
    )
    
    #* G: Consumibles (30 como default)
    printing_consumables = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=30.00,
        null=True,
        blank=True,
        help_text="Consumables cost (default 30.00)"
    )
    
    #* Metadata class for the OrderItem model
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        
    def __str__(self):
        return f"{self.service.name} - {self.quantity}x"                                                                  #* Returns a string representation of the order item with service name and quantity
    
    #* Method to calculate area in square inches (for formulas)
    def get_area_square_inches(self):
        if self.length_dimensions and self.width_dimensions:
            #* Already in inches, no conversion needed
            return float(self.length_dimensions) * float(self.width_dimensions)
        return 0
    
    #* Method to calculate estimated price based on service type
    def calculate_service_price(self):
        if not self.service:
            return 0
            
        service_type = self.service.type
        
        if service_type == 'plasma':
            return self.calculate_plasma_price()
        elif service_type in ['laser_engraving', 'laser_cutting']:
            return self.calculate_laser_price()
        elif service_type in ['3D_printing', 'resin_printing']:
            return self.calculate_printing_price()
        else:
            return float(self.service.base_price) if self.service.base_price else 0
    
    #* Plasma cutting price calculation
    def calculate_plasma_price(self):
        #* Use minimum values for estimation
        A = self.plasma_design_programming_time or 60
        B = self.plasma_cutting_time or 30
        C = self.plasma_post_process_time or 60
        D = 0.09524 * B  #* Luz (kW/min)
        E = float(self.plasma_material_cost) if self.plasma_material_cost else 0
        F = self.get_area_square_inches()
        G = float(self.plasma_consumables) if self.plasma_consumables else 162.30
        
        #* SUBTOTAL = ((A*3.33)+(B*16.5)+(C*1.5)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3
        subtotal = ((A * 3.33) + (B * 16.5) + (C * 1.5) + (D * 0.03211) + (((E * F) / 4608) * 2) + G) * 1.3
        
        #* TOTAL MXN = SUBTOTAL * 1.08
        total = subtotal * 1.08
        
        return total
    
    #* Laser cutting/engraving price calculation
    def calculate_laser_price(self):
        #* Use minimum values for estimation
        A = self.laser_design_programming_time or 30
        B = self.laser_cutting_time or 10
        C = self.laser_post_process_time or 10
        D = 0.09524 * B  #* Luz (kW/min)
        E = float(self.laser_material_cost) if self.laser_material_cost else 0
        F = self.get_area_square_inches()
        G = float(self.laser_consumables) if self.laser_consumables else 30.00
        
        #* SUBTOTAL = ((A*1.2)+(B*1.7)+(C*1)+(D*0.03211)+(((E*F)/4608)*2)+G)*1.3
        subtotal = ((A * 1.2) + (B * 1.7) + (C * 1) + (D * 0.03211) + (((E * F) / 4608) * 2) + G) * 1.3
        
        #* TOTAL MXN = SUBTOTAL * 1.08
        total = subtotal * 1.08
        
        return total
    
    #* 3D printing price calculation
    def calculate_printing_price(self):
        #* Use minimum values for estimation
        A = self.printing_design_programming_time or 60
        B = self.printing_time or 30
        C = float(self.printing_material_used) if self.printing_material_used else 0
        D = self.printing_post_process_time or 60
        E = 0.0208333333333333 * B  #* Luz (kW/min)
        F = float(self.printing_material_cost) if self.printing_material_cost else 350.00
        G = float(self.printing_consumables) if self.printing_consumables else 30.00
        
        #* SUBTOTAL = (((B*2.7)+((D+B)*1.5)+(E)+(((C/1000)/F))*2)+G)*1.6
        subtotal = (((B * 2.7) + ((D + B) * 1.5) + E + (((C / 1000) / F) * 2) + G) * 1.6)
        
        #* TOTAL MXN = SUBTOTAL * 1.08
        total = subtotal * 1.08
        
        return total
    
    #* Method to calculate estimated total price of the item
    def get_estimated_total_price(self):
        #* Calculate service price automatically
        service_price = self.calculate_service_price()
        total = service_price * self.quantity
        
        #* Add custom design price if needed
        if self.needs_custom_design and self.custom_design_price:
            total += float(self.custom_design_price)
        
        #* Update estimated_unit_price with calculated value
        self.estimated_unit_price = service_price
        
        return total
    
    #* Method to calculate final total price of the item
    def get_final_total_price(self):
        total = 0
        if self.final_unit_price:
            total += float(self.final_unit_price) * self.quantity                                                               #* Add service price
        if self.needs_custom_design and self.custom_design_price:
            total += float(self.custom_design_price)                                                                            #* Add design price if needed
        return total
    
    #* Method to get estimated total including design price
    def get_estimated_total_with_design(self):
        """Calculate total estimated price including design price"""
        total = 0
        if self.estimated_unit_price:
            total += float(self.estimated_unit_price) * self.quantity
        
        if self.needs_custom_design and self.custom_design_price:
            total += float(self.custom_design_price)
        
        return total
    
    #* Method to get final total including design price
    def get_final_total_with_design(self):
        """Calculate total final price including design price"""
        total = 0
        if self.final_unit_price:
            total += float(self.final_unit_price) * self.quantity
        
        if self.needs_custom_design and self.custom_design_price:
            total += float(self.custom_design_price)
        
        return total
    
    #* Method to get savings/difference between estimated and final
    def get_price_difference(self):
        """Calculate difference between estimated and final total"""
        estimated_total = self.get_estimated_total_with_design()
        final_total = self.get_final_total_with_design()
        
        if estimated_total > 0 and final_total > 0:
            return final_total - estimated_total
        return 0
    
    #* Method to format total price for display
    def get_formatted_total_price(self):
        """Get formatted total price string"""
        total = self.get_final_total_with_design()
        if total > 0:
            return f"${total:,.2f} MXN"
        return "Not calculated"
    
    #* Method to save and auto-calculate prices
    def save(self, *args, **kwargs):
        #* ONLY calculate estimated_unit_price if it's a NEW object (doesn't have pk)
        if not self.pk and not self.estimated_unit_price and self.service:
            #* It's a new object, calculate estimated price
            self.estimated_unit_price = self.calculate_service_price()
        
        #* ALWAYS recalculate final_unit_price if there are changes in calculation fields
        #* or if final_unit_price doesn't exist
        if self.service and (not self.final_unit_price or self._state.adding == False):
            #* Recalculate final price based on current fields
            self.final_unit_price = self.calculate_service_price()
        
        super().save(*args, **kwargs)