#? Models for the services app
from django.db import models
from django.conf import settings
from django.utils import timezone

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
    
    ALL_TYPES = BASE_TYPES
    
    #* Fields for the TypeService model
    type = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Type of service offered (auto-generated from name)"
    )
    
    #* name fields for the service type 
    name = models.CharField(
        max_length=100,
        help_text="Name of the service type"
    )

    #* description fields for the service type
    description = models.TextField(
        blank=True,
        help_text="Description of the service type"
    )
    
    #* short description field for the service type
    short_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Short description of the service"
    )
    
    #* base price field for the service type
    base_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Base price for the service"
    )
    
    #* active field for the service type
    active = models.BooleanField(
        default=True,
        help_text="Indicates if the service is active"
    )
    
    #* is_base_service field to identify the 5 main services
    is_base_service = models.BooleanField(
        default=False,
        help_text="Indicates if this is one of the 5 base services"
    )
    
    #* Order display field to control service order
    order_display = models.IntegerField(
        null=True,
        blank=True,
        help_text="Order for displaying services (auto-assigned)"
    )
    
    #* Featured service indicator
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured services appear prominently"
    )
    
    #* Image field for service representation
    image = models.ImageField(
        upload_to='service_images/',
        null=True,
        blank=True,
        help_text="Service image for display"
    )
    
    #* Metadata class for the TypeService model
    class Meta:
        ordering = ['order_display', 'name']
        verbose_name = "Type of Service"
        verbose_name_plural = "Types of Services"
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.type:
            self.type = self.name.lower().replace(' ', '_').replace('-', '_')
        super().save(*args, **kwargs)


#? <|--------------Company Configuration Model--------------|>
class CompanyConfiguration(models.Model):
    
    #* Company information fields
    company_name = models.CharField(
        max_length=100,
        default="AGAH Solutions",
        help_text="Name of the company"
    )
    
    company_tagline = models.CharField(
        max_length=200,
        default="Cutting-Edge Solutions, Crafted to Perfection",
        help_text="Company tagline or slogan"
    )
    
    about_us = models.TextField(
        blank=True,
        help_text="About us section content"
    )
    
    company_mission = models.TextField(
        blank=True,
        help_text="Company mission statement"
    )
    
    company_vision = models.TextField(
        blank=True,
        help_text="Company vision statement"
    )
    
    #* Contact information fields
    contact_email = models.EmailField(
        default="agahsolutions@gmail.com",
        help_text="Main contact email"
    )
    
    company_phone = models.CharField(
        max_length=20,
        default="+52 665 127 0811",
        help_text="Main phone number"
    )
    
    company_address = models.TextField(
        blank=True,
        help_text="Company address"
    )
    
    #* Business configuration
    company_time_response_hours = models.IntegerField(
        default=24,
        help_text="Expected response time in hours"
    )
    
    #* Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Company Configuration"
        verbose_name_plural = "Company Configuration"
    
    def __str__(self):
        return f"{self.company_name} - Configuration"


#? <|--------------Order Model--------------|>
class Order(models.Model):
    
    #* Order state choices
    ORDER_STATES = [
        ('pending', 'Pendiente'),
        ('estimated', 'Estimado'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('canceled', 'Cancelado'),
    ]

    #* Order number field
    order_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Unique order number (auto-generated)"
    )

    #* Customer information fields
    customer_name = models.CharField(
        max_length=100,
        help_text="Customer's full name"
    )

    customer_email = models.EmailField(
        help_text="Customer's email address"
    )

    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Customer's phone number"
    )

    #* Order state field
    state = models.CharField(
        max_length=20,
        choices=ORDER_STATES,
        default='pending',
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        help_text="User assigned to the order"
    )
    
    #* additional notes field
    additional_notes = models.TextField(
        blank=True,
        help_text="Additional notes for the order"
    )

    #* Metadata class for the Order model
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    #* SOLUCION PROBLEMA 4 - Método para calcular el precio total estimado
    def get_estimated_total_price(self):
        """Calculate total estimated price including all items and design costs"""
        total = 0
        for item in self.items.all():
            total += item.get_estimated_total_with_design()
        return total
    
    #* SOLUCION PROBLEMA 4 - Método para calcular el precio total final
    def get_final_total_price(self):
        """Calculate total final price including all items and design costs"""
        total = 0
        for item in self.items.all():
            total += item.get_final_total_with_design()
        return total


#? <|--------------Order Item Model--------------|>
class OrderItem(models.Model):
    
    #* Order relationship field
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Order to which this item belongs"
    )

    #* Service relationship field
    service = models.ForeignKey(
        TypeService,
        on_delete=models.CASCADE,
        help_text="Type of service requested"
    )

    #* Description field for additional details
    description = models.TextField(
        blank=True,
        help_text="Additional description for the service"
    )

    #* Design file upload field
    design_file = models.FileField(
        upload_to='order_files/',
        null=True,
        blank=True,
        help_text="Upload design files for the order"
    )

    #* Quantity field
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of the service the consumer wants"
    )

    #* Dimension fields
    length_dimensions = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length of the design in inches"
    )

    width_dimensions = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width of the design in inches"
    )

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
        help_text="Estimated unit price for the order item"
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
    
    #* B: Corte/Grabado (10 min minimo)
    laser_cutting_time = models.IntegerField(
        default=10,
        null=True,
        blank=True,
        help_text="Cutting/Engraving time in minutes (minimum 10)"
    )
    
    #* C: Post-proceso (10min minimo)
    laser_post_process_time = models.IntegerField(
        default=10,
        null=True,
        blank=True,
        help_text="Post-process time in minutes (minimum 10)"
    )
    
    #* E: Costo de Material
    laser_material_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Material cost"
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
        return f"{self.service.name} - {self.quantity}x"
    
    #* Method to calculate area in square inches (for formulas)
    def get_area_square_inches(self):
        if self.length_dimensions and self.width_dimensions:
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
    
    #* 3D/Resin printing price calculation
    def calculate_printing_price(self):
        #* Use minimum values for estimation
        A = self.printing_design_programming_time or 60
        B = self.printing_time or 30
        C = float(self.printing_material_used) if self.printing_material_used else 0
        D = self.printing_post_process_time or 60
        F = float(self.printing_material_cost) if self.printing_material_cost else 350.00
        G = float(self.printing_consumables) if self.printing_consumables else 30.00
        
        #* SUBTOTAL = ((A*2.7)+(B*1.9)+(C/1000)*F+(D*1.5)+G)*1.3
        subtotal = ((A * 2.7) + (B * 1.9) + (C / 1000) * F + (D * 1.5) + G) * 1.3
        
        #* TOTAL MXN = SUBTOTAL * 1.08
        total = subtotal * 1.08
        
        return total
    
    #* SOLUCION PROBLEMA 3 - Method to get estimated total including design price
    def get_estimated_total_with_design(self):
        """Calculate total estimated price including design price"""
        total = 0
        if self.estimated_unit_price:
            total += float(self.estimated_unit_price) * self.quantity
        
        if self.needs_custom_design and self.custom_design_price:
            total += float(self.custom_design_price)
        
        return total
    
    #* SOLUCION PROBLEMA 3 - Method to get final total including design price
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
    
    #* Method to save and auto-calculate prices - SOLUCION PROBLEMA 5
    def save(self, *args, **kwargs):
        #* Calculate prices based on calculation fields
        if self.service:
            calculated_price = self.calculate_service_price()
            
            #* Set estimated price only if not set
            if not self.estimated_unit_price:
                self.estimated_unit_price = calculated_price
            
            #* NO auto-update final price - solo cuando admin llene los campos
            # Solo actualiza si hay cambios en los campos de cálculo
            if self._state.adding == False:  # Es un update, no creación
                # Solo recalcula si hay valores en los campos de cálculo
                service_type = self.service.type
                has_calc_fields = False
                
                if service_type == 'plasma':
                    has_calc_fields = any([
                        self.plasma_design_programming_time,
                        self.plasma_cutting_time, 
                        self.plasma_material_cost
                    ])
                elif service_type in ['laser_engraving', 'laser_cutting']:
                    has_calc_fields = any([
                        self.laser_design_programming_time,
                        self.laser_cutting_time,
                        self.laser_material_cost
                    ])
                elif service_type in ['3D_printing', 'resin_printing']:
                    has_calc_fields = any([
                        self.printing_design_programming_time,
                        self.printing_time,
                        self.printing_material_used
                    ])
                
                # Solo recalcula el precio final si hay campos de cálculo llenos
                if has_calc_fields:
                    self.final_unit_price = calculated_price
        
        super().save(*args, **kwargs)
        
        #* Update order totals after saving item
        if self.order:
            self.order.estimated_price = self.order.get_estimated_total_price()
            self.order.final_price = self.order.get_final_total_price()
            self.order.save(update_fields=['estimaded_price', 'final_price'])