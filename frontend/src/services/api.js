//? Import Axios
import axios from 'axios';

//? Base API Class
class BaseAPI {
    //* Constructor for BaseAPI
    constructor() {
        this.baseURL = 'http://localhost:8000'; // AGREGAR ESTA LÍNEA
        this.api = axios.create({
            baseURL: this.baseURL, // AGREGAR ESTA LÍNEA
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        // Setup authentication interceptor automatically
        this.setupAuthInterceptor();
        
        // Response interceptor for error handling
        this.api.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.response?.data || error.message);
                
                // Handle 401 errors specifically
                if (error.response?.status === 401) {
                    console.error('Authentication failed - token may be invalid or expired');
                    // You could dispatch an event here to logout the user automatically
                    // window.dispatchEvent(new CustomEvent('auth-error', { detail: '401 Unauthorized' }));
                }
                
                return Promise.reject(error);
            }
        );
    }

    //* Setup authentication interceptor
    setupAuthInterceptor() {
        this.api.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('authToken');
                if (token) {
                    config.headers.Authorization = `Token ${token}`;
                } else {
                    console.warn('No auth token found in localStorage');
                }
                return config;
            },
            (error) => Promise.reject(error)
        );
    }

    //* Helper method to handle errors
    handleError(error, defaultMessage = 'An error occurred') {
        if (error.response?.data?.error) {
            throw new Error(error.response.data.error);
        }
        if (error.response?.data?.message) {
            throw new Error(error.response.data.message);
        }
        if (error.response?.data?.detail) {
            throw new Error(error.response.data.detail);
        }
        throw new Error(error.message || defaultMessage);
    }
}

//? <|------------------Home Page APIs------------------|>
class HomepageAPI extends BaseAPI {
    //* Get homepage data (featured services, stats, company info)
    async getHomepageData() {
        try {
            const response = await this.api.get('/api/homepage/');

            // Backend now returns {success, data}
            if (response.data.success) {
                return {
                    success: true,
                    data: response.data.data
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to load homepage data'
                };
            }
        } catch (error) {
            console.error('Homepage API Error:', error);
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Failed to load homepage data'
            };
        }
    }
}

//? <|------------------Services APIs-------------------|>
class ServicesAPI extends BaseAPI {
    //* Function to get all services
    async getServices() {
        try {
            const response = await this.api.get('/api/services/');
            
            // Backend now returns {success, data}
            if (response.data.success) {
                return response.data.data; // Array of services
            } else {
                throw new Error(response.data.error || 'Failed to load services');
            }
        } catch (error) {
            this.handleError(error, 'Failed to load services');
        }
    }

    //* Function to get service details by ID
    async getServiceDetail(serviceId) {
        try {
            const response = await this.api.get(`/api/services/${serviceId}/`);
            
            if (response.data.success) {
                return response.data.data;
            } else {
                throw new Error(response.data.error || 'Failed to load service details');
            }
        } catch (error) {
            this.handleError(error, `Failed to load service details for ${serviceId}`);
        }
    }

    //* Function to get active services
    async getActiveServices() {
        try {
            const services = await this.getServices();
            return services.filter(service => service.active);
        } catch (error) {
            this.handleError(error, 'Failed to load active services');
        }
    }

    //* Function to get services by type
    async getServicesByType(serviceType) {
        try {
            const services = await this.getServices();
            return services.filter(service => service.type === serviceType);
        } catch (error) {
            this.handleError(error, `Failed to load services of type ${serviceType}`);
        }
    }
}

//? <|-------------------About Us APIs------------------|>
class AboutUsAPI extends BaseAPI {
    //* Function to get company information
    async getCompanyInfo() {
        try {
            const response = await this.api.get('/api/company/');
            
            // Backend now returns {success, data}
            if (response.data.success) {
                return response.data.data;
            } else {
                throw new Error(response.data.error || 'Failed to load company information');
            }
        } catch (error) {
            this.handleError(error, 'Failed to load company information');
        }
    }

    //* Function to get About Us information (filtered)
    async getAboutInfo() {
        try {
            const companyInfo = await this.getCompanyInfo();
            return {
                aboutUs: companyInfo.about_us,
                mission: companyInfo.company_mission,
                vision: companyInfo.company_vision,
                responseTime: companyInfo.company_time_response_hours,
            };
        } catch (error) {
            this.handleError(error, 'Failed to load about information');
        }
    }
}

//? <|-------------------Contact APIs-------------------|>
class ContactAPI extends BaseAPI {
    //* Function to get company information (for contact info)
    async getCompanyInfo() {
        try {
            const response = await this.api.get('/api/company/');
            
            if (response.data.success) {
                return response.data.data;
            } else {
                throw new Error(response.data.error || 'Failed to load company information');
            }
        } catch (error) {
            this.handleError(error, 'Failed to load company information');
        }
    }

    //* Function to send contact form
    async sendContactForm(formData) {
        try {
            const response = await this.api.post('/api/contact/', formData);
            
            if (response.data.success) {
                return {
                    success: true,
                    message: response.data.message
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to send contact form'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Failed to send contact form'
            };
        }
    }

    //* Function to get contact information
    async getContactInfo() {
        try {
            const companyInfo = await this.getCompanyInfo();
            return {
                email: companyInfo.contact_email,
                phone: companyInfo.company_phone,
                address: companyInfo.company_address,
                name: companyInfo.company_name,
            };
        } catch (error) {
            this.handleError(error, 'Failed to load contact information');
        }
    }

    //* Function to validate contact form
    async validateContactForm(formData) {
        const errors = [];
        
        if (!formData.name?.trim()) {
            errors.push('Name is required');
        }
        
        if (formData.name && formData.name.length > 100) {
            errors.push('Name cannot exceed 100 characters');
        }
        
        if (!formData.email?.trim()) {
            errors.push('Email is required');
        }
        
        if (!formData.subject?.trim()) {
            errors.push('Subject is required');
        }
        
        if (formData.subject && formData.subject.length > 200) {
            errors.push('Subject cannot exceed 200 characters');
        }
        
        if (!formData.message?.trim()) {
            errors.push('Message is required');
        }
        
        if (formData.message && formData.message.trim().length < 10) {
            errors.push('Message must be at least 10 characters long');
        }
        
        //* Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (formData.email && !emailRegex.test(formData.email)) {
            errors.push('Invalid email format');
        }
        
        if (errors.length > 0) {
            throw new Error(errors.join(', '));
        }
        
        return true;
    }

    //* Function to send validated contact form
    async sendValidatedContactForm(formData) {
        await this.validateContactForm(formData);
        return await this.sendContactForm(formData);
    }
}

//? <|--------------------Cart APIs---------------------|>
class CartAPI extends BaseAPI {
    //* Function to add item to cart (cart managed in frontend)
    async addItemToCart(itemData) {
        try {
            // Since cart is managed in frontend, just validate the item
            await this.validateCartItem(itemData);
            return {
                success: true,
                data: itemData,
                message: 'Item added to cart'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    //* Function to calculate cart total
    async calculateCartTotal(cartItems) {
        try {
            // Calculate locally since we don't have a backend endpoint for this
            let subtotal = 0;
            let designTotal = 0;
            
            cartItems.forEach(item => {
                const itemPrice = item.estimated_price || 0;
                const quantity = item.quantity || 1;
                subtotal += itemPrice * quantity;
                
                if (item.needs_custom_design && item.custom_design_price) {
                    designTotal += item.custom_design_price;
                }
            });
            
            const total = subtotal + designTotal;
            
            return {
                success: true,
                data: {
                    subtotal,
                    design_total: designTotal,
                    total,
                    items_count: cartItems.length
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message || 'Failed to calculate cart total'
            };
        }
    }

    //* Function to validate cart item
    async validateCartItem(itemData) {
        const errors = [];
        
        if (!itemData.service_id) {
            errors.push('Service is required');
        }
        
        if (!itemData.quantity || itemData.quantity <= 0) {
            errors.push('Quantity must be greater than 0');
        }
        
        if (itemData.quantity > 100) {
            errors.push('Quantity cannot exceed 100');
        }
        
        if (!itemData.description?.trim()) {
            errors.push('Description is required');
        }
        
        if (itemData.needs_custom_design && !itemData.custom_design_price) {
            errors.push('Custom design price is required when design is needed');
        }
        
        if (errors.length > 0) {
            throw new Error(errors.join(', '));
        }
        
        return true;
    }

    //* Function to add validated item to cart
    async addValidatedItem(itemData) {
        await this.validateCartItem(itemData);
        return await this.addItemToCart(itemData);
    }
}

//? <|-------------------Orders APIs--------------------|>
class OrdersAPI extends BaseAPI {
    //* Function to create a new order
    async createOrder(orderData) {
        try {
            const response = await this.api.post('/api/orders/create/', orderData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 30000 // 30 seconds for file uploads
            });
            
            if (response.data.success) {
                return {
                    success: true,
                    order: response.data.data,
                    message: response.data.message || 'Order created successfully'
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to create order',
                    errors: response.data.errors || null
                };
            }
        } catch (error) {
            // Log the full error details for debugging
            console.error('Order creation error details:', {
                message: error.message,
                response: error.response?.data,
                errors: error.response?.data?.errors,
                status: error.response?.status
            });
            
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Failed to create order',
                errors: error.response?.data?.errors || null
            };
        }
    }

    //* Function to get orders by customer email
    async getOrdersByCustomer(email) {
        try {
            const response = await this.api.get(`/api/orders/customer/?email=${encodeURIComponent(email)}`);
            
            if (response.data.success) {
                return {
                    success: true,
                    orders: response.data.data || [],
                    count: response.data.count || 0
                };
            } else {
                throw new Error(response.data.error || 'Failed to load orders');
            }
        } catch (error) {
            console.error('Error fetching customer orders:', error);
            throw new Error(error.response?.data?.error || 'Failed to load orders');
        }
    }

    //* Function to get user's orders (requires authentication)
    async getUserOrders() {
        try {
            const response = await this.api.get('/api/orders/my-orders/');
            
            if (response.data.success) {
                return {
                    success: true,
                    orders: response.data.data || [],
                    count: response.data.count || 0
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to load orders'
                };
            }
        } catch (error) {
            console.error('Error fetching user orders:', error);
            
            // Mejorar el manejo de errores específicos
            if (error.response?.status === 500) {
                if (error.response?.data?.error && error.response.data.error.includes('Cannot resolve keyword')) {
                    throw new Error(`Database configuration error: ${error.response.data.error}`);
                }
                throw new Error(error.response?.data?.error || 'Internal server error');
            }
            
            throw new Error(error.response?.data?.error || 'Failed to load orders');
        }
    }

    //* Function to get specific order detail
    async getOrderDetail(orderId) {
        try {
            const response = await this.api.get(`/api/orders/my-orders/${orderId}/`);
            
            if (response.data.success) {
                return {
                    success: true,
                    order: response.data.data
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to load order details'
                };
            }
        } catch (error) {
            console.error('Error fetching order details:', error);
            throw new Error(error.response?.data?.error || 'Failed to load order details');
        }
    }

    //* Function to track order (public, no auth required)
    async trackOrder(orderNumber, customerEmail) {
        try {
            const response = await this.api.post('/api/orders/track/', {
                order_number: orderNumber,
                customer_email: customerEmail
            });
            
            if (response.data.success) {
                return {
                    success: true,
                    order: response.data.data
                };
            } else {
                throw new Error(response.data.error || 'Order not found');
            }
        } catch (error) {
            console.error('Error tracking order:', error);
            throw new Error(error.response?.data?.error || 'Failed to track order');
        }
    }

    //* Function to confirm order (accept final price)
    async confirmOrder(orderNumber, customerEmail) {
        try {
            const response = await this.api.post('/api/orders/confirm/', {
                order_number: orderNumber,
                customer_email: customerEmail
            });
            
            if (response.data.success) {
                return {
                    success: true,
                    message: response.data.message
                };
            } else {
                throw new Error(response.data.error || 'Failed to confirm order');
            }
        } catch (error) {
            console.error('Error confirming order:', error);
            throw new Error(error.response?.data?.error || 'Failed to confirm order');
        }
    }

    //* Function to cancel order
    async cancelOrder(orderNumber, customerEmail) {
        try {
            const response = await this.api.post('/api/orders/cancel/', {
                order_number: orderNumber,
                customer_email: customerEmail
            });
            
            if (response.data.success) {
                return {
                    success: true,
                    message: response.data.message
                };
            } else {
                throw new Error(response.data.error || 'Failed to cancel order');
            }
        } catch (error) {
            console.error('Error canceling order:', error);
            throw new Error(error.response?.data?.error || 'Failed to cancel order');
        }
    }

    //* Function to validate order data
    async validateOrderData(orderData) {
        const errors = [];
        
        if (!orderData.customer_phone?.trim()) {
            errors.push('Customer phone is required');
        }
        
        if (!orderData.items || orderData.items.length === 0) {
            errors.push('Order must have at least one item');
        }
        
        if (orderData.items && orderData.items.length > 50) {
            errors.push('Order cannot have more than 50 items');
        }
        
        if (errors.length > 0) {
            throw new Error(errors.join(', '));
        }
        
        return true;
    }

    //* Function to create validated order
    async createValidatedOrder(orderData) {
        await this.validateOrderData(orderData);
        return await this.createOrder(orderData);
    }

    //* Function to get order statistics
    async getOrderStatistics() {
        try {
            const result = await this.getUserOrders();
            
            if (!result.success) {
                return {
                    success: false,
                    error: result.error
                };
            }
            
            const orders = result.orders;
            
            const stats = {
                total: orders.length,
                pending: orders.filter(o => o.status === 'pendiente').length,
                estimated: orders.filter(o => o.status === 'cotizado').length,
                confirmed: orders.filter(o => o.status === 'confirmado').length,
                inProgress: orders.filter(o => o.status === 'en_proceso').length,
                completed: orders.filter(o => o.status === 'completado').length,
                canceled: orders.filter(o => o.status === 'cancelado').length,
            };
            
            return {
                success: true,
                data: stats
            };
        } catch (error) {
            return {
                success: false,
                error: error.message || 'Failed to load order statistics'
            };
        }
    }
}

//? <|--------------------Main API class---------------------|>
class AGAHAPI {
    constructor() {
        this.homepage = new HomepageAPI();
        this.services = new ServicesAPI();
        this.aboutUs = new AboutUsAPI();
        this.cart = new CartAPI();
        this.orders = new OrdersAPI();
        this.contact = new ContactAPI();
    }

    //* Method to set base URL if needed
    setBaseURL(url) {
        const apis = [this.homepage, this.services, this.aboutUs, this.cart, this.orders, this.contact];
        apis.forEach(api => {
            api.baseURL = url;
            api.api.defaults.baseURL = url;
        });
    }

    //* Method to add global headers (auth token)
    setAuthHeader(token) {
        const apis = [this.homepage, this.services, this.aboutUs, this.cart, this.orders, this.contact];
        apis.forEach(api => {
            api.api.defaults.headers.Authorization = `Bearer ${token}`;
        });
    }

    //* Method to remove auth headers (logout)
    removeAuthHeader() {
        const apis = [this.homepage, this.services, this.aboutUs, this.cart, this.orders, this.contact];
        apis.forEach(api => {
            delete api.api.defaults.headers.Authorization;
        });
    }
}

//* Create single instance (Singleton pattern)
const api = new AGAHAPI();

//* Export main instance and individual classes
export default api;
export { HomepageAPI, ServicesAPI, AboutUsAPI, CartAPI, OrdersAPI, ContactAPI, AGAHAPI };