
#? Serializers for the services app
from rest_framework import serializers                                                                     #* Bidirectional traduction between django and React using JSON
from .models import TypeService, CompanyConfiguration, Order, OrderItem                                    #* Import models to serialize


#? <|-------------------Service Type Serializer------------------|>
class TypeServiceSerializer(serializers.ModelSerializer):
    
    #*  Add Calculated Field
    formatted_price = serializers.SerializerMMethodField()                                                 #* Custom field to format price

    #* Meta class to define model and fields
    class Meta:
        model = TypeService                                                                                #* Model to serialize
        fields = '__all__'                                                                                 #* All fields from the model
        
    
    # * Method to format price
    def get_formatted_price(self, obj):                                                                    #* Method to format price
        return obj.get_price_display()                                                                     #* Call method to get formatted price


#? <|--------------Company Configuration Serializer--------------|>
class CompanyConfigurationSerializer(serializers.ModelSerializer):
    
    #* Meta class to define model and fields
    class Meta:
        model = CompanyConfiguration                                                                       #* Model to serialize
        fields = '__all__'                                                                                 #* All fields from the model


#? <|-----------------Order Item Serializer Base-----------------|>
class OrderItemSerializer(serializers.ModelSerializer):
    
    #* Read-only fields
    service_name = serializers.CharField(source='service.name', read_only=True)                            #* Service name from related service
    service_type = serializers.CharField(source='service.type', read_only=True)                            #* Service type name from related service type

    #*Calculated Fields
    calculated_estimated_price = serializers.SerializerMethodField()                                       #* Custom field to calculate estimated price
    calculated_final_price = serializers.SerializerMethodField()                                           #* Custom field to calculate final price
    area_square_inches = serializers.SerializerMethodField()                                               #* Custom field to calculate area in square inches
    
    #* Meta class to define model and fields
    class Meta:
        model = OrderItem                                                                                  #* Model to serialize
        fields = [    
            
            #* All fields from the model
            'id',
            'service',
            'service_name',
            'service_type',
            'description',
            'design_file',
            'quantity',
            'length_dimensions',
            'width_dimensions', 
            'height_dimensions',
            'estimated_unit_price',
            'final_unit_price',
            'needs_custom_design',
            'custom_design_price',
            
            #* Plasma cutting calculation fields
            'plasma_design_programming_time',
            'plasma_cutting_time',
            'plasma_post_process_time',
            'plasma_material_cost',
            'plasma_consumables',
            
            #* Laser cutting/engraving calculation fields
            'laser_design_programming_time',
            'laser_cutting_time', 
            'laser_post_process_time',
            'laser_material_cost',
            'laser_consumables',
            
            #* 3D printing calculation fields
            'printing_design_programming_time',
            'printing_time',
            'printing_material_used',
            'printing_post_process_time',
            'printing_material_cost',
            'printing_consumables',
            
            #* Calculated fields
            'calculated_estimated_price',
            'calculated_final_price',
            'area_square_inches',
        ]   
        
        def get_calculated_estimated_price(self, obj):                                                  #* Method to calculate estimated price
            return obj.get_estimated_price()                                                            #* Call method to calculate estimated price                                                                               

        def get_calculated_final_price(self, obj):                                                      #* Method to calculate final price
            return obj.get_final_total_price()                                                          #* Call method to calculate final price

        def get_area_square_inches(self, obj):                                                          #* Method to calculate area in square inches
            return obj.get_area_square_inches()                                                         #* Call method to calculate area in square inches


#? <|----------------Order Item Create Serializer----------------|>
class OrderItemCreateSerializer(serializers.ModelSerializer):
    
    #* Meta class to define model and fields
    class Meta:
        model = OrderItem
        fields = [
            'service',
            'description',
            'design_file',
            'quantity',
            'length_dimensions',
            'width_dimensions',
            'height_dimensions',
            'needs_custom_design',
            'custom_design_price',
        ]
        
    #* Validation for quantity
    def validate_quantity(self, value):                                                              
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        if value > 100:
            raise serializers.ValidationError("Quantity must not exceed 100.")
        return value

    #* Validation for custom design price
    def validate(self, data):
        if data.get('needs_custom_design') and not data.get('custom_design_price'):
            raise serializers.ValidationError("Custom design price is required if custom design is needed.")
        return data
    
    
#? <|----------------------Order Serializers---------------------|>

#? Order List Serializer
class OrderListSerializer(serializers.ModelSerializer):
    
    #* Custom fields  
    items_count = serializers.SerializerMethodField()                                                   #* Custom field to count items in the order
    state_display = serializers.CharField(source='get_state_display', read_only=True)                   #* Custom field to get state display
    formatted_estimated_price = serializers.SerializerMethodField()                                     #* Custom field to format estimated price
    formatted_final_price = serializers.SerializerMethodField()                                         #* Custom field to format final price

    #* Meta class to define model and fields
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'customer_name',
            'customer_email',
            'state',
            'state_display',
            'estimaded_price',
            'final_price',
            'formatted_estimated_price',
            'formatted_final_price',
            'created_at',
            'items_count'
        ]

    #* Method to count items in the order
    def get_items_count(self, obj):
        return obj.items.count()                                                                        #* Return count of items in the order
    
    #* Method to format estimated price
    def get_formatted_estimated_price(self, obj):
        if obj.estimaded_price:
            return f"${obj.estimaded_price:,.2f}"                                                       #* Format estimated price to string with 2 decimal places
        return "Pending"
    
    #* Method to format final price
    def get_formatted_final_price(self, obj):
        if obj.final_price:
            return f"${obj.final_price:,.2f}"                                                           #* Format final price to string with 2 decimal places
        return "Pending"

#? Order Detail Serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    
    #* Include all Order Items
    items = OrderItemSerializer(many=True, read_only=True)                                              #* Include all order items in the order detail

    #* Calculated and formatted fields
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    total_items = serializers.SerializerMethodField()
    formatted_estimated_price = serializers.SerializerMethodField()
    formatted_final_price = serializers.SerializerMethodField()
    
    #* Meta class to define model and fields
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'customer_name',
            'customer_email',
            'customer_phone',
            'state',
            'state_display',
            'estimaded_price',
            'final_price',
            'formatted_estimated_price',
            'formatted_final_price',
            'estimated_completion_date_days',
            'created_at',
            'additional_notes',
            'items',
            'total_items'
        ]
        
        #* Methods to calculate and format fields
        def get_total_items(self, obj):
            return sum(item.quantity for item in obj.items.all())
    
        #* Method to format estimated price
        def get_formatted_estimated_price(self, obj):
            if obj.estimaded_price:
                return f"${obj.estimaded_price:,.2f} MXN"
            return "Calculating..."
        
        #* Method to format final price
        def get_formatted_final_price(self, obj):
            if obj.final_price:
                return f"${obj.final_price:,.2f} MXN"
            return "Pending admin review"
        
        
#? Order Create Serializer
class OrderCreateSerializer(serializers.ModelSerializer):
    
    #* Items array sent from the frontend cart
    items = OrderItemCreateSerializer(many=True, write_only=True)                                         #* Use OrderItemCreateSerializer to validate items
    
    #* Meta class to define model and fields
    class  Meta: 
        model = Order
        fields = [
            'customer_name',
            'customer_email', 
            'customer_phone',
            'items'
        ]
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        if len(value) > 50:
            raise serializers.ValidationError("Order cannot have more than 50 items.")
        return value
    
    def create(self, validated_data):
        from django.db import transaction                                                               #* Import transaction to handle atomic operations
        
        #* Start a transaction to ensure atomicity 
        items_data = validated_data.pop('items')                                                        #* Extract items data from validated data
    
        with transaction.atomic():                                                                      #* Start a transaction
            
            #* Create the main order
            order = Order.objects.create(**validated_data)                                              #* Create the order with validated data
            
            #* get Estimate
            total_estimated = 0                                                                         #* Initialize total estimated price

            #* Create each order item
            for item_data in items_data:
                order_item = OrderItem.objets.create(order=order, **item_data)                          #* Create order item with order and item data
    
                #* Total Price Calculation
                total_estimated += order_item.get_estimated_total_price()                               #* Add estimated price of the item to total estimated price

            order.estimated_price = total_estimated                                                     #* Set the total estimated price on the order
            order.save()                                                                                #* Save the order

        return order


#? <|--------------Contact Form Serializer--------------|>
class ContactFormSerializer(serializers.Serializer):
    
    #* Fields for the contact form
    name = serializers.CharField(
        max_length=100,
        error_messages={
            'required': 'Name is required',
            'max_length': 'Name cannot exceed 100 characters'
        }
    )
    
    #* Email field with validation 
    email = serializers.EmailField(
        error_messages={
            'required': 'Email is required',
            'invalid': 'Enter a valid email address'
        }
    )
    
    #* Phone field
    phone = serializers.CharField(
        max_length=15, 
        required=False,
        allow_blank=True
    )
    
    #* Subject and message fields
    subject = serializers.CharField(
        max_length=200,
        error_messages={
            'required': 'Subject is required',
            'max_length': 'Subject cannot exceed 200 characters'
        }
    )
    
    #* Message field with textarea style
    message = serializers.CharField(
        style={'base_template': 'textarea.html'},
        error_messages={
            'required': 'Message is required'
        }
    )
        
    # * Validate name field
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty or only spaces")
        
        #* Check for dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'"]
        if any(char in value for char in dangerous_chars):
            raise serializers.ValidationError("Name contains invalid characters")
        
        return value.strip()
    
    # * Validate email field
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        
        return value.strip()


#? <|--------------Cart Item Serializer--------------|>
class CartItemSerializer(serializers.Serializer):
    
    #* Fields for the cart item
    service_id = serializers.IntegerField()
    service_name = serializers.CharField(read_only=True)
    service_type = serializers.CharField(read_only=True)
    description = serializers.CharField(max_length=1000)
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    length_dimensions = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    width_dimensions = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    height_dimensions = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    needs_custom_design = serializers.BooleanField(default=False)
    custom_design_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    
    #* Calculated fields for frontend
    estimated_unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    estimated_total_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    
    #* Validation for service ID 
    def validate_service_id(self, value):
        try:
            service = TypeService.objects.get(id=value, active=True)
            return value
        except TypeService.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive")
    
    #* Validation
    def validate(self, data):
        if data.get('needs_custom_design') and not data.get('custom_design_price'):
            raise serializers.ValidationError({
                'custom_design_price': 'Price is required when custom design is requested'
            })
        
        return data