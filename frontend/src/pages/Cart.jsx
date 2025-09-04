//? Imports
import React, { useState, useEffect } from 'react';
import '../style/Cart.css';

//? Context and API imports
import { useCart } from '../context/CartContext';
import { useToastContext } from '../context/ToastContext';
import ConfirmationModal from '../components/common/ConfirmationModal';
import api from '../services/api';
import authAPI from '../services/AuthAPI';

//? Component
function Cart() {
    //? State Variables
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [additionalNotes, setAdditionalNotes] = useState('');
    const [userInfo, setUserInfo] = useState(null);
    const [phoneNumber, setPhoneNumber] = useState('');
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    
    //* Context
    const { 
        cartItems, 
        updateQuantity, 
        removeFromCart, 
        clearCart, 
        calculateTotal,
        getCartItemCount 
    } = useCart();

    //* Toast notifications
    const { success, error: showError, warning, promise } = useToastContext();

    //? Effects
    //* Load user data on component mount
    useEffect(() => {
        const user = authAPI.getUser();
        if (user) {
            setUserInfo(user);
            // Initialize phone number if user has one
            if (user.phone) {
                setPhoneNumber(user.phone);
            }
        }
    }, []);

    //? Functions
    //* Submit order for review
    const handleSubmitForReview = async () => {
    //* Validate user is logged in
    if (!userInfo) {
        warning('Por favor inicia sesión para enviar tu pedido');
        return;
    }

    //* Validate phone number is provided
    if (!phoneNumber.trim()) {
        warning('Por favor ingresa tu número de teléfono');
        return;
    }

    if (cartItems.length === 0) {
        warning('Tu carrito está vacío');
        return;
    }

    setIsSubmitting(true);

    try {
        // CORRECCIÓN: Crear FormData para manejar archivos
        const formData = new FormData();
        
        // Datos básicos del cliente
        formData.append('customer_name', userInfo.first_name && userInfo.last_name 
            ? `${userInfo.first_name} ${userInfo.last_name}` 
            : userInfo.username);
        formData.append('customer_email', userInfo.email);
        formData.append('customer_phone', phoneNumber.trim());
        formData.append('additional_notes', additionalNotes || '');

        // Preparar items SIN archivos para JSON
        const itemsForJson = cartItems.map((item, index) => {
            // Si hay archivo, lo agregaremos por separado al FormData
            if (item.design_file) {
                formData.append(`item_${index}_design_file`, item.design_file);
                console.log(`Added file for item ${index}: ${item.design_file.name}`);
            }
            
            return {
                service: parseInt(item.service),
                description: item.description?.trim() || "",
                quantity: parseInt(item.quantity) || 1,
                length_dimensions: item.length_dimensions ? parseFloat(item.length_dimensions) : null,
                width_dimensions: item.width_dimensions ? parseFloat(item.width_dimensions) : null,
                height_dimensions: item.height_dimensions ? parseFloat(item.height_dimensions) : null,
                needs_custom_design: Boolean(item.needs_custom_design),
                has_design_file: Boolean(item.design_file)
            };
        });

        // Agregar items como JSON
        formData.append('items', JSON.stringify(itemsForJson));

        // Debug - mostrar contenido del FormData
        console.log('FormData contents:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + (pair[1] instanceof File ? pair[1].name : pair[1]));
        }

        const result = await promise(
            api.orders.api.post('/api/orders/create/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 30000
            }),
            {
                loading: 'Enviando tu pedido...',
                success: 'Pedido enviado exitosamente. Te enviaremos una cotización pronto',
                error: 'Error al enviar el pedido'
            }
        );

        //* Debug: Log the result
        console.log('Order creation result:', result);
        
        if (result && result.errors) {
            console.error('Validation errors:', result.errors);
        }

        if (result.data && result.data.success) {
            //* Clear cart after successful submission
            clearCart();
            
            //* Redirect to services or reload page
            setTimeout(() => {
                window.location.href = '/services';
            }, 1500);
        } else {
            // If there are specific validation errors, format them nicely
            let errorMessage = result.data?.error || result.error || 'Failed to submit order';
            if (result.data?.errors) {
                const errorDetails = Object.entries(result.data.errors)
                    .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
                    .join('\n');
                errorMessage = `${errorMessage}\n${errorDetails}`;
            }
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error('Error submitting order:', error);
        if (showError) {
            showError(`Error: ${error.message || 'Error al enviar el pedido'}`);
        }
    } finally {
        setIsSubmitting(false);
    }
};

    //* Handle cancel cart
    const handleCancelCart = () => {
        setShowConfirmModal(true);
    };

    const confirmClearCart = () => {
        clearCart();
        success('Carrito vaciado exitosamente');
        setShowConfirmModal(false);
    };

    const cancelClearCart = () => {
        setShowConfirmModal(false);
    };

    //* Calculate estimated total
    const estimatedTotal = calculateTotal();
    const itemCount = getCartItemCount();

    //? What is gonna be rendered
    if (cartItems.length === 0) {
        return (
            <div className="cart-container">
                <div className="cart-empty">
                    <h2>Your Cart is Empty</h2>
                    {/* <h2>Su Carrito está Vacío</h2> */}
                    <p>Add some items from our services to get started!</p>
                    {/* <p>¡Agregue algunos artículos de nuestros servicios para comenzar!</p> */}
                    <a 
                        href="/services"
                        className="continue-shopping-btn"
                    >
                        Continue Shopping
                        {/* Continuar Comprando */}
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="cart-container">
            <div className="cart-header">
                <h1>Shopping Cart</h1>
                {/* <h1>Carrito de Compras</h1> */}
                <p className="cart-subtitle">
                    {itemCount} {itemCount === 1 ? 'item' : 'items'} in your cart
                    {/* {itemCount} {itemCount === 1 ? 'artículo' : 'artículos'} en su carrito */}
                </p>
            </div>

            <div className="cart-content">
                {/*//? Left side - Cart Items */}
                <div className="cart-items-section">
                    <h2>Order Items</h2>
                    {/* <h2>Artículos del Pedido</h2> */}
                    
                    <div className="cart-items-list">
                        {cartItems.map((item) => (
                            <div key={item.cartItemId} className="cart-item">
                                <div className="item-details">
                                    <h3>{item.service_name}</h3>
                                    <p className="item-description">{item.description}</p>
                                    
                                    {/*//? Display dimensions if provided */}
                                    {(item.length_dimensions || item.width_dimensions || item.height_dimensions) && (
                                        <p className="item-dimensions">
                                            Dimensions: {item.length_dimensions || '-'}" L x {item.width_dimensions || '-'}" W x {item.height_dimensions || '-'}" H
                                            {/* Dimensiones: {item.length_dimensions || '-'}" L x {item.width_dimensions || '-'}" A x {item.height_dimensions || '-'}" Alt */}
                                        </p>
                                    )}
                                    
                                    {item.needs_custom_design && (
                                        <span className="custom-design-badge">
                                            Custom Design Required
                                            {/* Diseño Personalizado Requerido */}
                                        </span>
                                    )}
                                </div>

                                <div className="item-controls">
                                    <div className="quantity-controls">
                                        <button 
                                            className="quantity-btn"
                                            onClick={() => updateQuantity(item.cartItemId, item.quantity - 1)}
                                        >
                                            -
                                        </button>
                                        <span className="quantity-display">{item.quantity}</span>
                                        <button 
                                            className="quantity-btn"
                                            onClick={() => updateQuantity(item.cartItemId, item.quantity + 1)}
                                        >
                                            +
                                        </button>
                                    </div>
                                    
                                    <div className="item-price">
                                        ${(item.estimated_unit_price * item.quantity).toFixed(2)}
                                    </div>
                                    
                                    <button 
                                        className="remove-item-btn"
                                        onClick={() => removeFromCart(item.cartItemId)}
                                        title="Remove item"
                                    >
                                        ✕
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/*//? Customer Information Display & Additional Notes */}
                    <div className="customer-info-section">
                        <h2>Customer Information</h2>
                        
                        {/* Display user info */}
                        {userInfo && (
                            <div className="user-info-display">
                                <div className="info-row">
                                    <span className="info-label">Name:</span>
                                    <span className="info-value">
                                        {userInfo.first_name && userInfo.last_name 
                                            ? `${userInfo.first_name} ${userInfo.last_name}` 
                                            : userInfo.username}
                                    </span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label">Email:</span>
                                    <span className="info-value">{userInfo.email}</span>
                                </div>
                                {userInfo.phone && (
                                    <div className="info-row">
                                        <span className="info-label">Phone:</span>
                                        <span className="info-value">{userInfo.phone}</span>
                                    </div>
                                )}
                            </div>
                        )}
                        
                        <div className="customer-form">
                            {/* Phone Number Input */}
                            <div className="form-group">
                                <label htmlFor="phone_number">
                                    Phone Number *
                                    {/* Número de Teléfono * */}
                                </label>
                                <input
                                    type="tel"
                                    id="phone_number"
                                    name="phone_number"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                    placeholder="Enter your phone number"
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="additional_notes">
                                    Additional Notes
                                    {/* Notas Adicionales */}
                                </label>
                                <textarea
                                    id="additional_notes"
                                    name="additional_notes"
                                    value={additionalNotes}
                                    onChange={(e) => setAdditionalNotes(e.target.value)}
                                    rows="4"
                                    placeholder="Any special requirements or notes for your order..."
                                    // placeholder="Cualquier requerimiento especial o notas para su pedido..."
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/*//? Right side - Order Summary */}
                <div className="cart-summary-section">
                    <div className="summary-card">
                        <h2>Order Summary</h2>
                        {/* <h2>Resumen del Pedido</h2> */}
                        
                        <div className="summary-details">
                            <div className="summary-row">
                                <span>Subtotal ({itemCount} items)</span>
                                {/* <span>Subtotal ({itemCount} artículos)</span> */}
                                <span>${estimatedTotal.toFixed(2)}</span>
                            </div>
                            
                            <div className="summary-row total">
                                <span>Estimated Total</span>
                                {/* <span>Total Estimado</span> */}
                                <span className="total-price">${estimatedTotal.toFixed(2)}</span>
                            </div>
                        </div>

                        <div className="estimation-notice">
                            <p>
                                <strong>Important:</strong> This is an <strong>ESTIMATION</strong> only. 
                                The final price will be calculated after reviewing your designs and 
                                requirements. We will send you a detailed quote for approval.
                                <br />
                                <br />
                                Payment information will be collected at the time of the final checkout.

                                {/* <strong>Importante:</strong> Esto es solo una <strong>ESTIMACIÓN</strong>. 
                                El precio final se calculará después de revisar sus diseños y 
                                requerimientos. Le enviaremos una cotización detallada para su aprobación.
                                <br />
                                <br />
                                La información de pago se recopilará al momento del pago final. */} 
                            </p>
                        </div>

        <div className="summary-actions">
            <button 
                className="modal-button-submit"
                onClick={handleSubmitForReview}
                disabled={isSubmitting}
            >
                {isSubmitting ? 'Submitting...' : 'Submit for Review'}
                {/* {isSubmitting ? 'Enviando...' : 'Enviar para Revisión'} */}
            </button>
            
            <button 
                className="modal-button-cancel"
                onClick={handleCancelCart}
                disabled={isSubmitting}
            >
                Clear Cart
                {/* Vaciar Carrito */}
            </button>
        </div>
                    </div>
                </div>
            </div>
            
            {/* Confirmation Modal */}
            <ConfirmationModal
                isOpen={showConfirmModal}
                onClose={cancelClearCart}
                onConfirm={confirmClearCart}
                title="Vaciar Carrito"
                message="¿Estás seguro de que deseas eliminar todos los productos de tu carrito? Esta acción no se puede deshacer."
                confirmText="Sí, vaciar"
                cancelText="Cancelar"
            />
        </div>
    );
}

export default Cart;