
#? Serializers for the services app
from rest_framework import serializers
from .models import TypeService, Order, OrderItem, CompanyConfiguration


#? <|--------------Type Service Serializer--------------|>
class TypeServiceSerializer(serializers.ModelSerializer):
    
    #* Read-only fields
    price_display = serializers.CharField(source='get_price_display', read_only=True)
    
    class Meta:
        model = TypeService
        fields = [
            'id',
            'type',
            'name',
            'description',
            'short_description',
            'base_price',
            'price_display',
            'principal_image',
            'active',
            'order_display',
            'is_base_service',
            'is_featured'
        ]
        read_only_fields = [
            'id',
            'type',
            'order_display',
            'is_base_service'
        ]


#? <|--------------Order Item Serializer--------------|>
class OrderItemSerializer(serializers.ModelSerializer):
    
    #* Nested service information
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_type = serializers.CharField(source='service.type', read_only=True)
    
    #* Price calculations (read-only)
    estimated_total_price = serializers.DecimalField(
        source='get_estimated_total_with_design',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    final_total_price = serializers.DecimalField(
        source='get_final_total_with_design',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    formatted_total_price = serializers.CharField(
        source='get_formatted_total_price',
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
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
            'estimated_total_price',
            'final_total_price',
            'formatted_total_price',
            
            # Plasma cutting fields
            'plasma_design_programming_time',
            'plasma_cutting_time',
            'plasma_post_process_time',
            'plasma_material_cost',
            'plasma_consumables',
            
            # Laser cutting/engraving fields
            'laser_design_programming_time',
            'laser_cutting_time',
            'laser_post_process_time',
            'laser_material_cost',
            'laser_consumables',
            
            # 3D printing fields
            'printing_design_programming_time',
            'printing_time',
            'printing_material_used',
            'printing_post_process_time',
            'printing_material_cost',
            'printing_consumables',
        ]
        
        read_only_fields = [
            'id',
            'service_name',
            'service_type',
            'estimated_total_price',
            'final_total_price',
            'formatted_total_price',
        ]


#? <|--------------Order Serializer--------------|>
class OrderSerializer(serializers.ModelSerializer):
    
    #* Nested order items
    items = OrderItemSerializer(many=True, read_only=True)
    
    #* User information (read-only)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    #* State display with color
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    state_color = serializers.CharField(source='get_state_display_color', read_only=True)
    
    #* Calculated fields
    total_items = serializers.SerializerMethodField()
    estimated_total = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'user_email',
            'user_full_name',
            'customer_name',
            'customer_email',
            'customer_phone',
            'state',
            'state_display',
            'state_color',
            'created_at',
            'estimaded_price',
            'final_price',
            'estimated_completion_date_days',
            'assigned_user',
            'additional_notes',
            'items',
            'total_items',
            'estimated_total',
            'final_total',
        ]
        
        read_only_fields = [
            'id',
            'order_number',
            'user',
            'user_email',
            'user_full_name',
            'created_at',
            'state_display',
            'state_color',
            'items',
            'total_items',
            'estimated_total',
            'final_total',
        ]
    
    def get_total_items(self, obj):
        """Get total number of items in the order"""
        return obj.items.count()
    
    def get_estimated_total(self, obj):
        """Get total estimated price for all items"""
        return sum(item.get_estimated_total_with_design() for item in obj.items.all())
    
    def get_final_total(self, obj):
        """Get total final price for all items"""
        return sum(item.get_final_total_with_design() for item in obj.items.all())


#? <|--------------Company Configuration Serializer--------------|>
class CompanyConfigurationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompanyConfiguration
        fields = [
            'id',
            'company_name',
            'contact_email',
            'company_phone',
            'company_address',
            'about_us',
            'company_mission',
            'company_vision',
            'company_time_response_hours',
        ]
        read_only_fields = ['id']


#? <|--------------Contact Form Serializer--------------|>
class ContactFormSerializer(serializers.Serializer):
    """
    Serializer for contact form submissions
    Not linked to any model - just for validation
    """
    
    name = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Full name of the person contacting"
    )
    
    email = serializers.EmailField(
        required=True,
        help_text="Email address for response"
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Phone number (optional)"
    )
    
    subject = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Subject of the inquiry"
    )
    
    message = serializers.CharField(
        required=True,
        help_text="Message content"
    )
    
    # Custom validation for message length
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters long."
            )
        return value.strip()
    
    # Custom validation for name
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value.strip()


        #? <|--------------Order Item Create Serializer--------------|>

class OrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating order items within an order
    """
    class Meta:
        model = OrderItem
        fields = [
            'service',
            'description', 
            'quantity',
            'length_dimensions',
            'width_dimensions', 
            'height_dimensions',
            'needs_custom_design',
            'design_file'
        ]
#? <|--------------Order Creation Serializer--------------|>
class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for creating orders with nested items
    """
    items = OrderItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_email',
            'customer_phone',
            'additional_notes',
            'items'
        ]
    
    def create(self, validated_data):
        #* Extract items data
        items_data = validated_data.pop('items', [])
        
        #* Create the order
        order = Order.objects.create(**validated_data)
        
        #* Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        #* Calculate estimated price
        order.estimaded_price = order.calculate_estimated_price()
        order.save()
        
        return order
    
    def validate_items(self, value):
        """Ensure at least one item is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one item is required.")
        return value
    
    def validate(self, data):
        """Validate the entire order data"""
        #* Check required fields
        if not data.get('customer_name'):
            raise serializers.ValidationError({"customer_name": "Customer name is required"})
        if not data.get('customer_email'):
            raise serializers.ValidationError({"customer_email": "Customer email is required"})
        if not data.get('customer_phone'):
            raise serializers.ValidationError({"customer_phone": "Customer phone is required"})
        
        return data