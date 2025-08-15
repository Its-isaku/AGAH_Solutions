//? Import Axios
import axios from 'axios';                                                                      //* Import Axios for making HTTP requests

//? Base API Class
class BaseAPI {

    //* Constructor for BaseAPI
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000';                                                 //* Base URL for the API
        this.api = axios.create({                                                               //* Axios instance
            baseURL: this.baseURL,                                                              //* Base URL for the Axios instance
            headers: {                                                                          //* Headers for the Axios instance
                'Content-Type': 'application/json',
            },
        });

        //* Interceptor to handle errors globally
        this.api.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    //* Helper method to handle errors
    handleError(error, defaultMessage = 'An error occurred') {
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
class HomepageAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.api = axios.create({ 
            baseURL: this.baseURL,
            timeout: 10000,  // 10 second timeout
            headers: {
                'Content-Type': 'application/json',
            }
        });
    }

    //* Get homepage data (featured services, stats, company info)
    async getHomepageData() {
        try {
            console.log('Making request to:', `${this.baseURL}/homepage/`);
            const response = await this.api.get('/homepage/');
            
            console.log('Raw response:', response);
            console.log('Response data:', response.data);
            console.log('Response status:', response.status);
            
            // Check if response is successful
            if (response.status === 200 && response.data) {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                console.warn('Unexpected response format:', response);
                return {
                    success: false,
                    error: 'Formato de respuesta inesperado'
                };
            }
        } catch (error) {
            console.error('Homepage API Error:', error);
            console.error('Error details:', {
                message: error.message,
                status: error.response?.status,
                data: error.response?.data,
                config: error.config
            });
            
            return {
                success: false,
                error: error.response?.data?.message || error.message || 'Error al cargar datos del homepage'
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
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to load services');
        }
    }

    //* Function to get service details from a specific service type
    async getServiceDetail(serviceType) {
        try {
            const response = await this.api.get(`/api/services/${serviceType}/`);
            return response.data;
        } catch (error) {
            this.handleError(error, `Failed to load service details for ${serviceType}`);
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
class AboutUsAPI extends BaseAPI{

    //* Class to get About Us information
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

    //* Function to get company information
    async getCompanyInfo() {
        try {
            const response = await this.api.get('/api/company/');
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to load company information');
        }
    }
}

//? <|-------------------Contact APIs-------------------|>
class ContactAPI extends BaseAPI {
    
    //* Function to send contact form
    async sendContactForm(formData) {
        try {
            const response = await this.api.post('/api/contact/', formData);
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to send contact form');
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
        
        //* Validate dangerous characters
        const dangerousChars = ['<', '>', '&', '"', "'"];
        if (formData.name && dangerousChars.some(char => formData.name.includes(char))) {
            errors.push('Name contains invalid characters');
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


//? <|-------------------Orders APIs--------------------|>
class OrdersAPI extends BaseAPI {

    //* Function to create a new order
    async createOrder(orderData) {
        try {
            const response = await this.api.post('/api/orders/create/', orderData);
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to create order');
        }
    }

    //* Function to get orders by customer email
    async getOrdersByCustomer(email) {
        try {
            const response = await this.api.get(`/api/orders/customer/?email=${encodeURIComponent(email)}`);
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to load customer orders');
        }
    }

    //* Function to track order by order number
    async trackOrder(orderNumber) {
        try {
            const response = await this.api.get(`/api/orders/track/${encodeURIComponent(orderNumber)}/`);
            return response.data;
        } catch (error) {
            this.handleError(error, `Failed to track order ${orderNumber}`);
        }
    }

    //* Function to validate order data
    async validateOrderData(orderData) {
        const errors = [];
        
        if (!orderData.customer_name?.trim()) {
            errors.push('Customer name is required');
        }
        
        if (!orderData.customer_email?.trim()) {
            errors.push('Customer email is required');
        }
        
        if (!orderData.customer_phone?.trim()) {
            errors.push('Customer phone is required');
        }
        
        if (!orderData.items || orderData.items.length === 0) {
            errors.push('Order must have at least one item');
        }
        
        if (orderData.items && orderData.items.length > 50) {
            errors.push('Order cannot have more than 50 items');
        }
        
        //* Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (orderData.customer_email && !emailRegex.test(orderData.customer_email)) {
            errors.push('Invalid email format');
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

    //* Function to get order statistics by customer email
    async getOrderStatistics(email) {
        try {
            const orders = await this.getOrdersByCustomer(email);
            
            const stats = {
                total: orders.length,
                pending: orders.filter(o => o.state === 'pending').length,
                estimated: orders.filter(o => o.state === 'estimated').length,
                confirmed: orders.filter(o => o.state === 'confirmed').length,
                inProgress: orders.filter(o => o.state === 'in_progress').length,
                completed: orders.filter(o => o.state === 'completed').length,
                canceled: orders.filter(o => o.state === 'canceled').length,
            };
            
            return stats;
        } catch (error) {
            this.handleError(error, 'Failed to load order statistics');
        }
    }
}


//? <|--------------------Cart APIs---------------------|>
class CartAPI extends BaseAPI {

    //* Function to add item to cart
    async addItemToCart(itemData) {
        try {
            const response = await this.api.post('/api/cart/add-item/', itemData);
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to add item to cart');
        }
    }

    //* Function to calculate cart total
    async calculateCartTotal(cartItems) {
        try {
            const response = await this.api.post('/api/cart/calculate-total/', {
                cart_items: cartItems
            });
            return response.data;
        } catch (error) {
            this.handleError(error, 'Failed to calculate cart total');
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


//? <|--------------------Main  API class---------------------|>
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
        const apis = [this.homepage, this.services, this.cart, this.orders, this.contact];
        apis.forEach(api => {
            api.baseURL = url;
            api.api.defaults.baseURL = url;
        });
    }

    //* Method to add global headers (Login, auth token)
    setAuthHeader(token) {
        const apis = [this.homepage, this.services, this.cart, this.orders, this.contact];
        apis.forEach(api => {
            api.api.defaults.headers.Authorization = `Bearer ${token}`;
        });
    }

    //* Method to remove auth headers (Logout)
    removeAuthHeader() {
        const apis = [this.homepage, this.services, this.cart, this.orders, this.contact];
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