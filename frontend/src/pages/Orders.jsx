// frontend/src/pages/Orders.jsx

import React, { useState, useEffect } from 'react';
import { useAuthContext } from '../context/AuthContext';
import { useToastContext } from '../context/ToastContext';
import api from '../services/api';
import '../style/Orders.css';

// Icons
import { 
    MdPhone, 
    MdCalendarToday, 
    MdAttachment,
    MdVisibility,
    MdPrint,
    MdRefresh 
} from 'react-icons/md';

// Text constants for bilingual support
const TEXT = {
    // Page titles and headers
    pageTitle: 'My Orders', // 'Mis Órdenes'
    pageSubtitle: 'Check the status and details of all your orders', // 'Consulta el estado y detalles de todas tus órdenes'
    
    // Loading and empty states
    loading: 'Loading orders...', // 'Cargando órdenes...'
    updating: 'Updating...', // 'Actualizando...'
    update: 'Update', // 'Actualizar'
    noOrdersTitle: "You don't have any orders yet", // 'No tienes órdenes aún'
    noOrdersSubtitle: 'When you place your first order, it will appear here.', // 'Cuando realices tu primera orden, aparecerá aquí.'
    viewServices: 'View Services', // 'Ver Servicios'
    
    // Order statuses
    firstEstimate: 'First Estimate', // 'Primera Estimación'
    estimated: 'Estimated', // 'Estimado'
    confirmed: 'Confirmed', // 'Confirmado'
    inProgress: 'In Progress', // 'En Proceso'
    completed: 'Completed', // 'Completado'
    canceled: 'Canceled', // 'Cancelado'
    
    // Order details
    orderNumber: 'Order #', // 'Orden #'
    item: 'item', // 'artículo'
    items: 'items', // 'artículos'
    hideDetails: 'Hide', // 'Ocultar'
    showDetails: 'View Details', // 'Ver Detalles'
    toBeDetermined: 'To be quoted', // 'Por cotizar'
    
    // Customer info section
    customerInfo: 'Customer Information', // 'Información del Cliente'
    name: 'Name:', // 'Nombre:'
    email: 'Email:', // 'Email:'
    phone: 'Phone:', // 'Teléfono:'
    
    // Order items section
    orderItems: 'Order Items', // 'Artículos de la Orden'
    itemNumber: 'Item #', // 'Artículo #'
    service: 'Service', // 'Servicio'
    quantity: 'Quantity:', // 'Cantidad:'
    dimensions: 'Dimensions:', // 'Dimensiones:'
    customDesign: 'Custom Design', // 'Diseño Personalizado'
    attachedFile: 'Attached File', // 'Archivo Adjunto'
    unitPrice: 'Unit price:', // 'Precio unitario:'
    subtotal: 'Subtotal:', // 'Subtotal:'
    
    // Pricing section
    pricingSummary: 'Pricing Summary', // 'Resumen de Precios'
    estimatedPrice: 'Estimated Price:', // 'Precio Estimado:'
    finalPrice: 'Final Price:', // 'Precio Final:'
    
    // Additional notes
    additionalNotes: 'Additional Notes', // 'Notas Adicionales'
    
    // Actions
    printOrder: 'Print Order', // 'Imprimir Orden'
    
    // Toast messages
    toastInvalidSession: 'Invalid session. Please log in again.', // 'Sesión no válida. Por favor, inicia sesión nuevamente.'
    toastOrdersCount: (count) => `You have ${count} ${count === 1 ? 'order' : 'orders'}`, // `Tienes ${count} ${count === 1 ? 'orden' : 'órdenes'}`
    toastNoOrders: 'You have no registered orders', // 'No tienes órdenes registradas'
    toastLoadError: 'Error loading orders', // 'Error al cargar las órdenes'
    toastConfigError: 'Server configuration error. Please contact the administrator.', // 'Error de configuración en el servidor. Por favor contacta al administrador.'
    toastSessionExpired: 'Session expired. Please log in again.', // 'Sesión expirada. Por favor, inicia sesión nuevamente.'
    toastServerError: 'Internal server error. Please try again in a few moments.', // 'Error interno del servidor. Intenta nuevamente en unos momentos.'
};

function Orders() {
    // Context hooks
    const { userInfo } = useAuthContext(); // Get user information
    const { success, error, warning, info, promise } = useToastContext();
    
    // State
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedOrder, setExpandedOrder] = useState(null);
    
    // Fetch orders on component mount - using authenticated user's email
    useEffect(() => {
        if (userInfo && userInfo.email) {
            fetchUserOrders();
        } else if (!userInfo || !userInfo.email) {
            setLoading(false);
        }
    }, [userInfo?.email]); // Only depends on email to avoid unnecessary renders

    // Function to fetch orders - using authenticated endpoint
    const fetchUserOrders = async (showToast = true) => {
        setLoading(true);
        
        try {
            // Verify that the token is present
            const token = localStorage.getItem('authToken');
            if (!token) {
                if (showToast) error(TEXT.toastInvalidSession);
                setLoading(false);
                return;
            }
            
            // Use the endpoint for authenticated users
            const response = await api.orders.getUserOrders();
            
            if (response.success) {
                setOrders(response.orders || []);
                if (showToast && response.orders && response.orders.length > 0) {
                    success(TEXT.toastOrdersCount(response.orders.length));
                } else if (showToast) {
                    info(TEXT.toastNoOrders);
                }
            } else {
                if (showToast) error(TEXT.toastLoadError);
                setOrders([]);
            }
        } catch (err) {
            console.error('Error fetching orders:', err);
            
            if (showToast) {
                // Handle different types of errors
                if (err.message && err.message.includes('Cannot resolve keyword')) {
                    error(TEXT.toastConfigError);
                    console.error('Backend database query error:', err.message);
                } else if (err.message && err.message.includes('401')) {
                    error(TEXT.toastSessionExpired);
                } else if (err.message && err.message.includes('500')) {
                    error(TEXT.toastServerError);
                } else {
                    error(TEXT.toastLoadError);
                }
            }
            
            setOrders([]);
        } finally {
            setLoading(false);
        }
    };

    // Function to refresh orders
    const handleRefresh = () => {
        fetchUserOrders(false); // Don't show toast on manual refresh
    };

    // Get progress percentage based on status
    const getProgressPercentage = (order) => {
        // Try different possible fields for status
        const status = order?.status || order?.state || order?.order_status || order?.current_status;
        
        // Normalize status for more flexible comparison
        const normalizedStatus = status?.toLowerCase().trim();
        
        switch (normalizedStatus) {
            // English states (real API values)
            case 'pending':
                return 25;
            case 'estimated':
                return 50;
            case 'confirmed':
                return 60;
            case 'in_progress':  // ← This is the real value that comes from the API
                return 75;
            case 'completed':
                return 100;
            case 'canceled':
                return 0;
            
            // Spanish states (for compatibility)
            case 'pendiente':
            case 'first_estimate':
            case 'primera estimación':
            case 'primera_estimacion':
                return 25;
            case 'cotizado':
            case 'final_price_sent':
            case 'cotización final':
            case 'cotizacion_final':
            case 'estimado':
                return 50;
            case 'confirmado':
            case 'en_proceso':
            case 'en proceso':
            case 'enproceso':
                return 75;
            case 'completado':
            case 'terminado':
                return 100;
            case 'cancelado':
            case 'cancelled':
                return 0;
            default:
                console.warn('Unknown status:', status, 'defaulting to 25%');
                return 25;
        }
    };

    // Get status display text
    const getStatusText = (order) => {
        // Try different possible fields for status
        const status = order?.status || order?.state || order?.order_status || order?.current_status;
        
        // Normalize status for more flexible comparison
        const normalizedStatus = status?.toLowerCase().trim();
        
        switch (normalizedStatus) {
            // English states (real API values)
            case 'pending':
                return TEXT.firstEstimate;
            case 'estimated':
                return TEXT.estimated;
            case 'confirmed':
                return TEXT.confirmed;
            case 'in_progress':  // ← This is the real value that comes from the API
                return TEXT.inProgress;
            case 'completed':
                return TEXT.completed;
            case 'canceled':
                return TEXT.canceled;
                
            // Spanish states (for compatibility)
            case 'pendiente':
            case 'first_estimate':
            case 'primera estimación':
            case 'primera_estimacion':
                return TEXT.firstEstimate;
            case 'cotizado':
            case 'final_price_sent':
            case 'cotización final':
            case 'cotizacion_final':
            case 'estimado':
                return TEXT.estimated;
            case 'confirmado':
            case 'en_proceso':
            case 'en proceso':
            case 'enproceso':
                return TEXT.inProgress;
            case 'completado':
            case 'terminado':
                return TEXT.completed;
            case 'cancelado':
            case 'cancelled':
                return TEXT.canceled;
            default:
                return TEXT.firstEstimate;
        }
    };

    // Get status color
    const getStatusColor = (order) => {
        // Try different possible fields for status
        const status = order?.status || order?.state || order?.order_status || order?.current_status;
        
        // Normalize status for more flexible comparison
        const normalizedStatus = status?.toLowerCase().trim();
        
        switch (normalizedStatus) {
            // English states (real API values)
            case 'pending':
                return '#F59E0B'; // Yellow
            case 'estimated':
                return '#3B82F6'; // Blue
            case 'confirmed':
                return '#8B5CF6'; // Purple
            case 'in_progress':  // ← This is the real value that comes from the API
                return '#78B7D0'; // Cyan
            case 'completed':
                return '#10B981'; // Green
            case 'canceled':
                return '#EF4444'; // Red
                
            // Spanish states (for compatibility)
            case 'pendiente':
            case 'first_estimate':
            case 'primera estimación':
            case 'primera_estimacion':
                return '#F59E0B'; // Yellow
            case 'cotizado':
            case 'final_price_sent':
            case 'cotización final':
            case 'cotizacion_final':
            case 'estimado':
                return '#3B82F6'; // Blue
            case 'confirmado':
            case 'en_proceso':
            case 'en proceso':
            case 'enproceso':
                return '#78B7D0'; // Cyan
            case 'completado':
            case 'terminado':
                return '#10B981'; // Green
            case 'cancelado':
            case 'cancelled':
                return '#EF4444'; // Red
            default:
                return '#F59E0B';
        }
    };

    // Toggle order expansion
    const toggleOrderExpansion = (orderId) => {
        setExpandedOrder(expandedOrder === orderId ? null : orderId);
    };

    // Format date
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Format currency
    const formatCurrency = (amount) => {
        if (!amount) return TEXT.toBeDetermined;
        return `$${parseFloat(amount).toLocaleString('es-ES', { minimumFractionDigits: 2 })} MXN`;
    };

    return (
        <div className="orders-container">
            {/* Header Section */}
            <div className="orders-header">
                <h1>{TEXT.pageTitle}</h1>
                <p className="orders-subtitle">
                    {TEXT.pageSubtitle}
                </p>
                {/* Refresh button */}
                <button 
                    onClick={handleRefresh} 
                    className="refresh-button"
                    disabled={loading}
                    title={TEXT.update}
                >
                    <MdRefresh className={loading ? "spinning" : ""} />
                    {loading ? TEXT.updating : TEXT.update}
                </button>
            </div>

            {/* Orders Content */}
            <div className="orders-content">
                {loading ? (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>{TEXT.loading}</p>
                    </div>
                ) : orders.length === 0 ? (
                    <div className="empty-orders">
                        <h3>{TEXT.noOrdersTitle}</h3>
                        <p>{TEXT.noOrdersSubtitle}</p>
                        <a href="/services" className="modal-button-submit">
                            {TEXT.viewServices}
                        </a>
                    </div>
                ) : (
                    <div className="orders-list">
                        {orders.map((order) => (
                            <div key={order.id} className="order-card">
                                {/* Order Header */}
                                <div className="order-header">
                                    <div className="order-main-info">
                                        <h3 className="order-number">{TEXT.orderNumber}{order.order_number}</h3>
                                        <div className="order-meta">
                                            <span className="order-date">
                                                <MdCalendarToday />
                                                {formatDate(order.created_at)}
                                            </span>
                                            <span className="order-items-count">
                                                {order.items?.length || 0} {(order.items?.length || 0) === 1 ? TEXT.item : TEXT.items}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="order-actions">
                                        <span className="order-total">
                                            {formatCurrency(order.final_price || order.estimated_price)}
                                        </span>
                                        <button 
                                            className="toggle-details-btn"
                                            onClick={() => toggleOrderExpansion(order.id)}
                                        >
                                            <MdVisibility />
                                            {expandedOrder === order.id ? TEXT.hideDetails : TEXT.showDetails}
                                        </button>
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                <div className="order-progress">
                                    <div className="progress-bar-container">
                                        <div 
                                            className="progress-bar-fill"
                                            style={{ 
                                                width: `${getProgressPercentage(order)}%`,
                                                backgroundColor: getStatusColor(order)
                                            }}
                                        />
                                    </div>
                                    <div className="progress-status">
                                        <span 
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(order) + '20', color: getStatusColor(order) }}
                                        >
                                            {getStatusText(order)}
                                        </span>
                                        <span className="progress-percentage">
                                            {getProgressPercentage(order)}% {TEXT.completed}
                                        </span>
                                    </div>
                                </div>

                                {/* Expanded Details */}
                                {expandedOrder === order.id && (
                                    <div className="order-details">
                                        {/* Progress Steps */}
                                        <div className="progress-steps">
                                            <div className={`step ${getProgressPercentage(order) >= 25 ? 'active' : ''}`}>
                                                <div className="step-indicator">1</div>
                                                <span>{TEXT.firstEstimate}</span>
                                            </div>
                                            <div className={`step ${getProgressPercentage(order) >= 50 ? 'active' : ''}`}>
                                                <div className="step-indicator">2</div>
                                                <span>Final Quote</span> {/* Cotización Final */}
                                            </div>
                                            <div className={`step ${getProgressPercentage(order) >= 75 ? 'active' : ''}`}>
                                                <div className="step-indicator">3</div>
                                                <span>{TEXT.inProgress}</span>
                                            </div>
                                            <div className={`step ${getProgressPercentage(order) >= 100 ? 'active' : ''}`}>
                                                <div className="step-indicator">4</div>
                                                <span>{TEXT.completed}</span>
                                            </div>
                                        </div>

                                        {/* Customer Info */}
                                        <div className="detail-section">
                                            <h4>{TEXT.customerInfo}</h4>
                                            <div className="detail-grid">
                                                <div className="detail-item">
                                                    <span className="detail-label">{TEXT.name}</span>
                                                    <span className="detail-value">{order.customer_name}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="detail-label">{TEXT.email}</span>
                                                    <span className="detail-value">{order.customer_email}</span>
                                                </div>
                                                {order.customer_phone && (
                                                    <div className="detail-item">
                                                        <span className="detail-label">{TEXT.phone}</span>
                                                        <span className="detail-value">
                                                            <MdPhone /> {order.customer_phone}
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Order Items */}
                                        <div className="detail-section">
                                            <h4>{TEXT.orderItems}</h4>
                                            <div className="order-items-list">
                                                {order.items?.map((item, index) => (
                                                    <div key={item.id || index} className="order-item">
                                                        <div className="item-header">
                                                            <span className="item-number">{TEXT.itemNumber}{index + 1}</span>
                                                            <span className="item-service">{item.service_name || TEXT.service}</span>
                                                        </div>
                                                        <div className="item-details">
                                                            <p className="item-description">{item.description}</p>
                                                            <div className="item-specs">
                                                                <span>{TEXT.quantity} {item.quantity}</span>
                                                                {item.length_dimensions && item.width_dimensions && (
                                                                    <span>
                                                                        {TEXT.dimensions} {item.length_dimensions} x {item.width_dimensions}
                                                                        {item.height_dimensions && ` x ${item.height_dimensions}`} cm
                                                                    </span>
                                                                )}
                                                                {item.needs_custom_design && (
                                                                    <span className="custom-design-badge">
                                                                        {TEXT.customDesign}
                                                                    </span>
                                                                )}
                                                                {item.design_file && (
                                                                    <span className="has-file-badge">
                                                                        <MdAttachment /> {TEXT.attachedFile}
                                                                    </span>
                                                                )}
                                                            </div>
                                                            {item.unit_price && (
                                                                <div className="item-pricing">
                                                                    <span>{TEXT.unitPrice} {formatCurrency(item.unit_price)}</span>
                                                                    <span>{TEXT.subtotal} {formatCurrency(item.subtotal)}</span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Pricing Section */}
                                        {(order.estimated_price || order.final_price) && (
                                            <div className="detail-section">
                                                <h4>{TEXT.pricingSummary}</h4>
                                                <div className="pricing-summary">
                                                    {order.estimated_price && (
                                                        <div className="price-row">
                                                            <span>{TEXT.estimatedPrice}</span>
                                                            <span>{formatCurrency(order.estimated_price)}</span>
                                                        </div>
                                                    )}
                                                    {order.final_price && (
                                                        <div className="price-row final-price">
                                                            <span>{TEXT.finalPrice}</span>
                                                            <span>{formatCurrency(order.final_price)}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {/* Additional Notes */}
                                        {order.additional_notes && (
                                            <div className="detail-section">
                                                <h4>{TEXT.additionalNotes}</h4>
                                                <p className="notes-text">{order.additional_notes}</p>
                                            </div>
                                        )}

                                        {/* Order Actions */}
                                        <div className="order-actions-expanded">
                                            <button className="action-btn print-btn">
                                                <MdPrint /> {TEXT.printOrder}
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Orders;