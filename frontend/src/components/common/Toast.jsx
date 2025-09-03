import React, { useState, useEffect, useRef } from 'react';
import { MdCheck, MdClose, MdInfo, MdWarning } from 'react-icons/md';
import '../../style/Toast.css';

// Hook para manejar las notificaciones
export const useToast = () => {
    const [toasts, setToasts] = useState([]);

    const addToast = (message, type = 'info', duration = 4000) => {
        const id = Date.now() + Math.random();
        const newToast = {
            id,
            message,
            type,
            duration,
            timestamp: Date.now()
        };

        setToasts(prev => {
            // Limitar a máximo 5 toasts visibles
            const updatedToasts = [...prev, newToast];
            return updatedToasts.slice(-5);
        });

        return id;
    };

    const removeToast = (id) => {
        // Marcar como removing para activar animación
        setToasts(prev => 
            prev.map(toast => 
                toast.id === id 
                    ? { ...toast, isRemoving: true }
                    : toast
            )
        );
        
        // Eliminar después de la animación (400ms como definimos en CSS)
        setTimeout(() => {
            setToasts(prev => prev.filter(toast => toast.id !== id));
        }, 400);
    };

    // Métodos de conveniencia
    const success = (message, duration) => addToast(message, 'success', duration);
    const error = (message, duration) => addToast(message, 'error', duration);
    const info = (message, duration) => addToast(message, 'info', duration);
    const warning = (message, duration) => addToast(message, 'warning', duration);

    // Para promesas con estados de carga
    const promise = (promiseOrFunc, messages = {}) => {
        const loadingId = addToast(
            messages.loading || 'Cargando...', 
            'loading', 
            0 // No auto-remove para loading
        );

        const promiseToResolve = typeof promiseOrFunc === 'function' 
            ? promiseOrFunc() 
            : promiseOrFunc;

        return promiseToResolve
            .then((result) => {
                removeToast(loadingId);
                addToast(messages.success || 'Operación completada exitosamente', 'success');
                return result;
            })
            .catch((error) => {
                removeToast(loadingId);
                addToast(messages.error || 'Ocurrió un error', 'error');
                throw error;
            });
    };

    return {
        toasts,
        success,
        error,
        info,
        warning,
        promise,
        removeToast
    };
};

// Componente individual de toast
const ToastItem = ({ toast, onRemove, style }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [progressStyle, setProgressStyle] = useState({});
    const [isPaused, setIsPaused] = useState(false);
    const [remainingTime, setRemainingTime] = useState(toast.duration);
    const timerRef = useRef(null);
    const startTimeRef = useRef(Date.now());

    useEffect(() => {
        // Animation in - delay para stagger effect
        const timer = setTimeout(() => setIsVisible(true), 50);
        return () => clearTimeout(timer);
    }, []);

    // Timer management with pause on hover
    useEffect(() => {
        if (toast.duration <= 0) return;

        const startTimer = () => {
            if (timerRef.current) clearTimeout(timerRef.current);
            
            timerRef.current = setTimeout(() => {
                if (!isPaused) {
                    onRemove(toast.id);
                }
            }, remainingTime);
        };

        if (!isPaused) {
            startTimeRef.current = Date.now();
            startTimer();
            
            // Progress bar animation
            setProgressStyle({
                transform: 'scaleX(1)',
                transitionDuration: `${remainingTime}ms`,
                animationPlayState: 'running'
            });
        } else {
            if (timerRef.current) clearTimeout(timerRef.current);
            
            // Pause progress bar
            setProgressStyle(prev => ({
                ...prev,
                animationPlayState: 'paused'
            }));
        }

        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [isPaused, remainingTime, toast.duration, toast.id, onRemove]);

    const handleMouseEnter = () => {
        if (toast.duration > 0) {
            setIsPaused(true);
            const elapsed = Date.now() - startTimeRef.current;
            setRemainingTime(Math.max(remainingTime - elapsed, 0));
        }
    };

    const handleMouseLeave = () => {
        if (toast.duration > 0) {
            setIsPaused(false);
        }
    };

    const handleRemove = () => {
        if (toast.isRemoving) return; // Prevenir múltiples clicks
        onRemove(toast.id);
    };

    const getIcon = () => {
        switch (toast.type) {
            case 'success':
                return <MdCheck />;
            case 'error':
                return <MdClose />;
            case 'warning':
                return <MdWarning />;
            case 'loading':
                return <div className="loading-spinner-toast"></div>;
            default:
                return <MdInfo />;
        }
    };

    return (
        <div 
            className={`toast-item toast-${toast.type} ${isVisible ? 'toast-visible' : ''} ${toast.isRemoving ? 'toast-removing' : ''}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{
                ...style,
                '--progress-transform': progressStyle.transform || 'scaleX(0)',
                '--progress-duration': progressStyle.transitionDuration || '0ms'
            }}
        >
            <div className="toast-icon">
                {getIcon()}
            </div>
            <div className="toast-content">
                <p className="toast-message">{toast.message}</p>
            </div>
            <button 
                className="toast-close"
                onClick={handleRemove}
                aria-label="Cerrar notificación"
            >
                <MdClose />
            </button>
            {/* Barra de progreso para auto-dismiss */}
            {toast.duration > 0 && !toast.isRemoving && (
                <div 
                    className="toast-progress-bar"
                    style={progressStyle}
                />
            )}
        </div>
    );
};

// Contenedor principal de toasts
const ToastContainer = ({ toasts, onRemove }) => {
    if (toasts.length === 0) return null;

    return (
        <div className="toast-container">
            {toasts.map((toast, index) => (
                <ToastItem
                    key={toast.id}
                    toast={toast}
                    onRemove={onRemove}
                    style={{
                        zIndex: 1000 - index // Los más nuevos aparecen encima
                    }}
                />
            ))}
        </div>
    );
};

export default ToastContainer;
