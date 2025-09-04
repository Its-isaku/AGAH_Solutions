import React, { useState, useEffect } from 'react';
import '../style/Services.css';

//? API import
import api from '../services/api';
import authAPI from '../services/AuthAPI';

//? Context imports
import { useCart } from '../context/CartContext';
import { useToastContext } from '../context/ToastContext';

//? Component 
function Services() {
    //? Hooks
    const { addToCart } = useCart();
    const { success, error: showError, warning } = useToastContext();
    
    //? State Variables 
    const [services, setServices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedService, setSelectedService] = useState(null);
    const [showModal, setShowModal] = useState(false);
    
    //* Modal form state
    const [orderForm, setOrderForm] = useState({
        customer_phone: '',
        additional_notes: '',
        items: []
    });
    
    //* Order item form state  
    const [itemForm, setItemForm] = useState({
        description: '',
        quantity: 1,
        length_dimensions: '',
        width_dimensions: '',
        height_dimensions: '',
        needs_custom_design: false,
        design_file: null
    });

    //? Functions
    //* Fetch services from API using api.js
    const loadServices = async () => {
        try {
            setLoading(true);
            if (error) setError(null);
            
            //* Using the API instance from api.js
            const servicesData = await api.services.getServices();
            
            if (servicesData) {
                setServices(servicesData);
            } else {
                setError('Failed to load services');
                // setError('Error al cargar los servicios');
            }
        } catch (err) {
            setError(err?.message || 'Failed to load services');
            // setError(err?.message || 'Error al cargar los servicios');
            console.error('Error loading services:', err);
        } finally {
            setLoading(false);
        }
    };

    //* Load services on component mount
    useEffect(() => {
        loadServices();
    }, []);

    //* Open modal with selected service
    const handleOpenModal = (service) => {
        setSelectedService(service);
        setShowModal(true);
        //* Reset forms
        setItemForm({
            description: '',
            quantity: 1,
            length_dimensions: '',
            width_dimensions: '',
            height_dimensions: '',
            needs_custom_design: false,
            design_file: null
        });
        setOrderForm({
            customer_phone: '',
            additional_notes: '',
            items: []
        });
    };

    //* Close modal
    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedService(null);
    };

    //* Handle form input changes
    const handleItemInputChange = (e) => {
        const { name, value, type, checked, files } = e.target;
        
        if (type === 'file') {
            setItemForm(prev => ({
                ...prev,
                [name]: files[0]
            }));
        } else {
            setItemForm(prev => ({
                ...prev,
                [name]: type === 'checkbox' ? checked : value
            }));
        }
    };

    //* Handle order form changes
    const handleOrderInputChange = (e) => {
        const { name, value } = e.target;
        setOrderForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    //* Add item to cart (updated to use context)
    const handleAddToCart = async () => {
        //* Check if user is authenticated
        if (!authAPI.isAuthenticated()) {
            showError('Debes iniciar sesión para agregar productos al carrito');
            return;
        }

        //* Validate required fields
        if (!orderForm.customer_phone) {
            warning('Por favor ingresa tu número de teléfono');
            return;
        }

        if (!itemForm.description) {
            warning('Por favor ingresa una descripción para tu pedido');
            return;
        }

        //* Create cart item
        const cartItem = {
            //* Service info
            service: selectedService.id,
            service_name: selectedService.name,
            service_type: selectedService.type,
            base_price: selectedService.base_price,
            
            //* Item details
            description: itemForm.description,
            quantity: parseInt(itemForm.quantity),
            length_dimensions: itemForm.length_dimensions ? parseFloat(itemForm.length_dimensions) : null,
            width_dimensions: itemForm.width_dimensions ? parseFloat(itemForm.width_dimensions) : null,
            height_dimensions: itemForm.height_dimensions ? parseFloat(itemForm.height_dimensions) : null,
            needs_custom_design: itemForm.needs_custom_design,
            design_file: itemForm.design_file,
            
            //* Customer info (saved for checkout)
            customer_phone: orderForm.customer_phone,
            additional_notes: orderForm.additional_notes,
            
            //* Estimated price (will be calculated by backend later)
            estimated_unit_price: selectedService.base_price || 0
        };

        try {
            //* Add to cart context
            addToCart(cartItem);
            
            success(`${selectedService.name} agregado al carrito exitosamente`);
            
            handleCloseModal();
        } catch (err) {
            showError('Error al agregar el artículo al carrito');
            console.error('Error adding to cart:', err);
        }
    };

    //? What is gonna be rendered
    if (loading) {
        return (
            <div className="service-container">
                <div className="service-loading">
                    <div className="spinner"></div>
                    <p>Loading services...</p>
                    {/* <p>Cargando servicios...</p> */}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="service-container">
                <div className="service-error">
                    <p>Error: {error}</p>
                    <button onClick={loadServices} className="retry-button">
                        Try Again
                        {/* Intentar de Nuevo */}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <>
            {/*//? Content */}
            <div className="service-container">
                <div className="service-header">
                    <h1 className='service-title'>Our Services</h1>
                    {/* <h1 className='service-title'>Nuestros Servicios</h1> */}
                    <p className='service-subtitle'>We offer a wide range of services to help you succeed.</p>
                    {/* <p className='service-subtitle'>Ofrecemos una amplia gama de servicios para ayudarte a tener éxito.</p> */}
                </div>

                {/*//? Service Cards Grid */}
                <div className="service-content">
                    <div className="service-grid">
                        {services.map((service) => (
                            <div key={service.id} className="service-card">
                                {service.image_url && (
                                    <div className="service-card-image">
                                        <img 
                                            src={service.image_url} 
                                            alt={service.name}
                                            onError={(e) => {
                                                e.target.style.display = 'none';
                                            }}
                                        />
                                    </div>
                                )}
                                <div className="service-card-body">
                                    <h3 className="service-card-title">{service.name}</h3>
                                    <p className="service-card-description">
                                        {service.short_description || service.description}
                                    </p>
                                    <div className="service-card-price">
                                        {service.price_display || 'Price not set'}
                                        {/* {service.price_display || 'Precio no establecido'} */}
                                    </div>
                                    <button 
                                        className="service-card-button"
                                        onClick={() => handleOpenModal(service)}
                                    >
                                        Create Order
                                        {/* Crear Orden */}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/*//? Order Modal */}
            {showModal && selectedService && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Create Order - {selectedService.name}</h2>
                            {/* <h2>Crear Orden - {selectedService.name}</h2> */}
                            <button className="modal-close" onClick={handleCloseModal}>
                                &times;
                            </button>
                        </div>

                        <div className="modal-body">
                            {/*//? Customer Information */}
                            <div className="form-section">
                                <h3>Contact Information</h3>
                                {/* <h3>Información de Contacto</h3> */}
                                <div className="form-group">
                                    <label htmlFor="customer_phone">
                                        Phone Number *
                                        {/* Número de Teléfono * */}
                                    </label>
                                    <input
                                        type="tel"
                                        id="customer_phone"
                                        name="customer_phone"
                                        value={orderForm.customer_phone}
                                        onChange={handleOrderInputChange}
                                        placeholder="(123) 456-7890"
                                        required
                                    />
                                </div>
                            </div>

                            {/*//? Item Details */}
                            <div className="form-section">
                                <h3>Order Details</h3>
                                {/* <h3>Detalles del Pedido</h3> */}
                                
                                <div className="form-group">
                                    <label htmlFor="description">
                                        Description *
                                        {/* Descripción * */}
                                    </label>
                                    <textarea
                                        id="description"
                                        name="description"
                                        value={itemForm.description}
                                        onChange={handleItemInputChange}
                                        placeholder="Please describe what you need..."
                                        // placeholder="Por favor describa lo que necesita..."
                                        rows="4"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="quantity">
                                        Quantity
                                        {/* Cantidad */}
                                    </label>
                                    <input
                                        type="number"
                                        id="quantity"
                                        name="quantity"
                                        value={itemForm.quantity}
                                        onChange={handleItemInputChange}
                                        min="1"
                                        required
                                    />
                                </div>

                                {/*//? Dimensions */}
                                <div className="form-section-dimensions">
                                    <h4>Dimensions (inches)</h4>
                                    {/* <h4>Dimensiones (pulgadas)</h4> */}
                                    <div className="form-row-dimensions">
                                        <div className="form-group">
                                            <label htmlFor="length_dimensions">
                                                Length
                                                {/* Largo */}
                                            </label>
                                            <input
                                                type="number"
                                                id="length_dimensions"
                                                name="length_dimensions"
                                                value={itemForm.length_dimensions}
                                                onChange={handleItemInputChange}
                                                step="0.01"
                                                placeholder="0.00"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="width_dimensions">
                                                Width
                                                {/* Ancho */}
                                            </label>
                                            <input
                                                type="number"
                                                id="width_dimensions"
                                                name="width_dimensions"
                                                value={itemForm.width_dimensions}
                                                onChange={handleItemInputChange}
                                                step="0.01"
                                                placeholder="0.00"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label htmlFor="height_dimensions">
                                                Height
                                                {/* Alto */}
                                            </label>
                                            <input
                                                type="number"
                                                id="height_dimensions"
                                                name="height_dimensions"
                                                value={itemForm.height_dimensions}
                                                onChange={handleItemInputChange}
                                                step="0.01"
                                                placeholder="0.00"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/*//? Custom Design & File Upload */}
                                <div className="form-group checkbox-group">
                                    <label>
                                        <input
                                            type="checkbox"
                                            name="needs_custom_design"
                                            checked={itemForm.needs_custom_design}
                                            onChange={handleItemInputChange}
                                        />
                                        <span>
                                            Needs Custom Design
                                            {/* Necesita Diseño Personalizado */}
                                        </span>
                                    </label>
                                </div>

                                {/*//? File Upload for Design */}
                                <div className="form-group">
                                    <label htmlFor="design_file">
                                        Upload Design File
                                        {/* Subir Archivo de Diseño */}
                                    </label>
                                    <input
                                        type="file"
                                        id="design_file"
                                        name="design_file"
                                        onChange={handleItemInputChange}
                                        accept=".pdf,.png,.jpg,.jpeg,.svg,.ai,.psd"
                                        className="file-input"
                                    />
                                    {itemForm.design_file && (
                                        <p className="file-name">
                                            Selected: {itemForm.design_file.name}
                                            {/* Seleccionado: {itemForm.design_file.name} */}
                                        </p>
                                    )}
                                </div>

                                {/*//? Additional Notes */}
                                <div className="form-group">
                                    <label htmlFor="additional_notes">
                                        Additional Notes
                                        {/* Notas Adicionales */}
                                    </label>
                                    <textarea
                                        id="additional_notes"
                                        name="additional_notes"
                                        value={orderForm.additional_notes}
                                        onChange={handleOrderInputChange}
                                        placeholder="Any special requirements or notes..."
                                        // placeholder="Cualquier requerimiento especial o notas..."
                                        rows="3"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="modal-footer">
                            <button 
                                className="modal-button-cancel"
                                onClick={handleCloseModal}
                            >
                                Cancel
                                {/* Cancelar */}
                            </button>
                            <button 
                                className="modal-button-submit"
                                onClick={handleAddToCart}
                            >
                                Add to Cart
                                {/* Agregar al Carrito */}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default Services;