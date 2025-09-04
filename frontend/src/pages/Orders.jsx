// frontend/src/pages/Orders.jsx

import React, { useState, useEffect } from 'react';
import { useAuthContext } from '../context/AuthContext';
import { useToastContext } from '../context/ToastContext';
import api from '../services/api';
import '../style/Orders.css';

// Icons
import { 
    MdSearch, 
    MdEmail, 
    MdPhone, 
    MdCalendarToday, 
    MdAttachment,
    MdVisibility,
    MdPrint,
    MdRefresh 
} from 'react-icons/md';

function Orders() {
    // Context hooks
    const { success, error, warning, info, promise } = useToastContext();
    
    // State
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchEmail, setSearchEmail] = useState('');
    const [expandedOrder, setExpandedOrder] = useState(null);
    
    // Fetch orders on component mount - without userInfo
    useEffect(() => {
        // Por ahora dejamos vacío el email inicial
        // El usuario tendrá que escribir su email para buscar
    }, []);

    // Function to fetch orders by email
    const fetchUserOrders = async (email) => {
        if (!email || !email.includes('@')) {
            warning('Por favor ingresa un email válido');
            return;
        }

        setLoading(true);
        
        try {
            await promise(
                api.orders.getOrdersByCustomer(email),
                {
                    loading: 'Buscando tus órdenes...',
                    success: (data) => {
                        setOrders(data.orders || []);
                        return `Encontradas ${data.orders?.length || 0} órdenes`;
                    },
                    error: 'Error al cargar las órdenes'
                }
            );
        } catch (err) {
            console.error('Error fetching orders:', err);
            setOrders([]);
        } finally {
            setLoading(false);
        }
    };

    // Handle search
    const handleSearch = (e) => {
        e.preventDefault();
        fetchUserOrders(searchEmail);
    };

    // Get progress percentage based on status
    const getProgressPercentage = (status) => {
        switch (status) {
            case 'pendiente':
            case 'first_estimate':
                return 25;
            case 'cotizado':
            case 'final_price_sent':
                return 50;
            case 'confirmado':
            case 'en_proceso':
                return 75;
            case 'completado':
                return 100;
            case 'cancelado':
                return 0;
            default:
                return 25;
        }
    };

    // Get status display text
    const getStatusText = (status) => {
        switch (status) {
            case 'pendiente':
            case 'first_estimate':
                return 'Primera Estimación';
            case 'cotizado':
            case 'final_price_sent':
                return 'Precio Final Aceptado';
            case 'confirmado':
            case 'en_proceso':
                return 'En Proceso';
            case 'completado':
                return 'Terminado';
            case 'cancelado':
                return 'Cancelado';
            default:
                return 'Primera Estimación';
        }
    };

    // Get status color
    const getStatusColor = (status) => {
        switch (status) {
            case 'pendiente':
            case 'first_estimate':
                return '#F59E0B'; // Yellow
            case 'cotizado':
            case 'final_price_sent':
                return '#3B82F6'; // Blue
            case 'confirmado':
            case 'en_proceso':
                return '#78B7D0'; // Cyan
            case 'completado':
                return '#10B981'; // Green
            case 'cancelado':
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
        if (!amount) return 'Por cotizar';
        return `$${parseFloat(amount).toLocaleString('es-ES', { minimumFractionDigits: 2 })} MXN`;
    };

    return (
        <div className="orders-container">
            {/* Header Section */}
            <div className="orders-header">
                <h1>Mis Órdenes</h1>
                <p className="orders-subtitle">
                    Consulta el estado y detalles de todas tus órdenes
                </p>
            </div>

            {/* Search Section */}
            <div className="orders-search-section">
                <form onSubmit={handleSearch} className="search-form">
                    <div className="search-input-group">
                        <MdEmail className="search-icon" />
                        <input
                            type="email"
                            value={searchEmail}
                            onChange={(e) => setSearchEmail(e.target.value)}
                            placeholder="Ingresa tu email para buscar órdenes"
                            className="search-input"
                            required
                        />
                        <button type="submit" className="search-button" disabled={loading}>
                            {loading ? <MdRefresh className="spinning" /> : <MdSearch />}
                            Buscar
                        </button>
                    </div>
                </form>
            </div>

            {/* Orders Content */}
            <div className="orders-content">
                {loading && orders.length === 0 ? (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>Cargando órdenes...</p>
                    </div>
                ) : orders.length === 0 ? (
                    <div className="empty-orders">
                        <h3>No se encontraron órdenes</h3>
                        <p>No tienes órdenes asociadas a este email, o el email no existe en nuestro sistema.</p>
                        <a href="/services" className="continue-shopping-btn">
                            Hacer una Orden
                        </a>
                    </div>
                ) : (
                    <div className="orders-list">
                        {orders.map((order) => (
                            <div key={order.id} className="order-card">
                                {/* Order Header */}
                                <div className="order-header">
                                    <div className="order-main-info">
                                        <h3 className="order-number">#{order.order_number}</h3>
                                        <div className="order-meta">
                                            <span className="order-date">
                                                <MdCalendarToday />
                                                {formatDate(order.created_at)}
                                            </span>
                                            <span className="order-items-count">
                                                {order.items?.length || 0} {(order.items?.length || 0) === 1 ? 'artículo' : 'artículos'}
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
                                            {expandedOrder === order.id ? 'Ocultar' : 'Ver'} Detalles
                                        </button>
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                <div className="progress-section">
                                    <div className="progress-header">
                                        <span className="progress-label">Estado: {getStatusText(order.status)}</span>
                                        <span className="progress-percentage">
                                            {getProgressPercentage(order.status)}%
                                        </span>
                                    </div>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill"
                                            style={{ 
                                                width: `${getProgressPercentage(order.status)}%`,
                                                backgroundColor: getStatusColor(order.status)
                                            }}
                                        ></div>
                                    </div>
                                    <div className="progress-steps">
                                        <div className={`step ${getProgressPercentage(order.status) >= 25 ? 'completed' : ''}`}>
                                            <span>Primera Estimación</span>
                                        </div>
                                        <div className={`step ${getProgressPercentage(order.status) >= 50 ? 'completed' : ''}`}>
                                            <span>Precio Final Aceptado</span>
                                        </div>
                                        <div className={`step ${getProgressPercentage(order.status) >= 75 ? 'completed' : ''}`}>
                                            <span>En Proceso</span>
                                        </div>
                                        <div className={`step ${getProgressPercentage(order.status) >= 100 ? 'completed' : ''}`}>
                                            <span>Terminado</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Expanded Details */}
                                {expandedOrder === order.id && (
                                    <div className="order-details">
                                        {/* Customer Info */}
                                        <div className="detail-section">
                                            <h4>Información del Cliente</h4>
                                            <div className="detail-grid">
                                                <div className="detail-item">
                                                    <span className="label">Nombre:</span>
                                                    <span className="value">{order.customer_name}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="label">Email:</span>
                                                    <span className="value">{order.customer_email}</span>
                                                </div>
                                                <div className="detail-item">
                                                    <span className="label">Teléfono:</span>
                                                    <span className="value">{order.customer_phone}</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Order Items */}
                                        <div className="detail-section">
                                            <h4>Artículos del Pedido</h4>
                                            <div className="order-items">
                                                {order.items?.map((item, index) => (
                                                    <div key={index} className="order-item">
                                                        <div className="item-header">
                                                            <h5>{item.service_name}</h5>
                                                            <span className="item-price">
                                                                {formatCurrency(item.estimated_unit_price * item.quantity)}
                                                            </span>
                                                        </div>
                                                        <div className="item-details">
                                                            <p><strong>Descripción:</strong> {item.description}</p>
                                                            <p><strong>Cantidad:</strong> {item.quantity}</p>
                                                            {(item.length_dimensions || item.width_dimensions || item.height_dimensions) && (
                                                                <p>
                                                                    <strong>Dimensiones:</strong> 
                                                                    {item.length_dimensions}cm × {item.width_dimensions}cm × {item.height_dimensions}cm
                                                                </p>
                                                            )}
                                                            {item.needs_custom_design && (
                                                                <span className="custom-design-badge">
                                                                    Diseño Personalizado
                                                                </span>
                                                            )}
                                                            {item.design_file && (
                                                                <div className="file-attachment">
                                                                    <MdAttachment />
                                                                    <span>Archivo de diseño adjunto</span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Additional Notes */}
                                        {order.additional_notes && (
                                            <div className="detail-section">
                                                <h4>Notas Adicionales</h4>
                                                <p className="notes-text">{order.additional_notes}</p>
                                            </div>
                                        )}

                                        {/* Pricing Info */}
                                        <div className="detail-section">
                                            <h4>Información de Precios</h4>
                                            <div className="pricing-info">
                                                <div className="price-row">
                                                    <span>Precio Estimado:</span>
                                                    <span>{formatCurrency(order.estimaded_price)}</span>
                                                </div>
                                                {order.final_price && (
                                                    <div className="price-row final-price">
                                                        <span>Precio Final:</span>
                                                        <span>{formatCurrency(order.final_price)}</span>
                                                    </div>
                                                )}
                                                {order.estimated_completion_date_days && (
                                                    <div className="price-row">
                                                        <span>Tiempo Estimado:</span>
                                                        <span>{order.estimated_completion_date_days} días</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Action Buttons */}
                                        <div className="order-actions-expanded">
                                            <button className="modal-button-cancel">
                                                <MdPrint />
                                                Imprimir Orden
                                            </button>
                                            <button className="modal-button-submit">
                                                <MdPhone />
                                                Contactar Soporte
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