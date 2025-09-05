import React, { useState, useEffect, useRef } from 'react';
import { MdCheck, MdClose, MdInfo, MdWarning } from 'react-icons/md';
import '../../style/Toast.css';

// Hook para animaciones FLIP (First, Last, Invert, Play)
const useFlipAnimation = (dependency) => {
    const ref = useRef();
    const prevPositions = useRef(new Map());

    useEffect(() => {
        if (!ref.current) return;

        const container = ref.current;
        const items = Array.from(container.children);
        
        // First: Capturar posiciones actuales
        const currentPositions = new Map();
        items.forEach((item, index) => {
            const rect = item.getBoundingClientRect();
            const key = item.dataset.toastId || index;
            currentPositions.set(key, { y: rect.top, height: rect.height });
        });

        // Last & Invert: Comparar con posiciones previas y aplicar transform
        items.forEach((item, index) => {
            const key = item.dataset.toastId || index;
            const current = currentPositions.get(key);
            const previous = prevPositions.current.get(key);
            
            if (previous && current && previous.y !== current.y) {
                const deltaY = previous.y - current.y;
                
                // Invert: Remover cualquier transición CSS temporal
                item.style.transition = 'none';
                item.style.transform = `translateY(${deltaY}px)`;
                
                // Forzar reflow
                item.offsetHeight;
                
                // Play: Animar de vuelta a posición natural
                requestAnimationFrame(() => {
                    item.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
                    item.style.transform = 'translateY(0px)';
                    
                    // Limpiar después de la animación
                    setTimeout(() => {
                        item.style.transition = '';
                        item.style.transform = '';
                    }, 600);
                });
            }
        });

        // Actualizar posiciones para la próxima vez
        prevPositions.current = currentPositions;
    }, [dependency]);

    return ref;
};

const TOAST_TEXT = {
    loading: 'Loading...',
    successDefault: 'Operation completed successfully',
    errorDefault: 'An error occurred',
    closeToast: 'Close notification',
};

// Hook to manage notifications
export const useToast = () => {
    const [toasts, setToasts] = useState([]);

    const addToast = (message, type = 'info', duration = 4000) => {
        const id = Date.now() + Math.random() * 10000; // ID más único
        const newToast = {
            id,
            message,
            type,
            duration,
            timestamp: Date.now(),
            createdAt: performance.now() // Tiempo de alta precisión
        };

        console.log(`Agregando toast ${id} con duración ${duration}ms`);

        setToasts(prev => {
            // Limit to maximum 5 visible toasts
            const updatedToasts = [...prev, newToast];
            console.log(`Total de toasts: ${updatedToasts.length}`);
            return updatedToasts.slice(-5);
        });

        return id;
    };

    const removeToast = (id) => {
        console.log(`Iniciando eliminación de toast ${id}`);
        
        // Primero marcar como eliminando para activar animación de salida
        setToasts(prev => 
            prev.map(toast => 
                toast.id === id 
                    ? { ...toast, isRemoving: true }
                    : toast
            )
        );

        // Después de la animación, eliminarlo del array
        setTimeout(() => {
            console.log(`Removiendo toast ${id} del DOM`);
            setToasts(prev => {
                const filtered = prev.filter(toast => toast.id !== id);
                console.log(`Toasts restantes: ${filtered.length}`);
                return filtered;
            });
        }, 300); // Tiempo de la animación de salida
    };

    // Convenience methods
    const success = (message, duration) => addToast(message, 'success', duration);
    const error = (message, duration) => addToast(message, 'error', duration);
    const info = (message, duration) => addToast(message, 'info', duration);
    const warning = (message, duration) => addToast(message, 'warning', duration);

    // For promises with loading states
    const promise = (promiseOrFunc, messages = {}) => {
        const loadingId = addToast(
            messages.loading || TOAST_TEXT.loading, 
            'loading', 
            0 // No auto-remove for loading
        );

        const promiseToResolve = typeof promiseOrFunc === 'function' 
            ? promiseOrFunc() 
            : promiseOrFunc;

        return promiseToResolve
            .then((result) => {
                removeToast(loadingId);
                addToast(messages.success || TOAST_TEXT.successDefault, 'success');
                return result;
            })
            .catch((error) => {
                removeToast(loadingId);
                addToast(messages.error || TOAST_TEXT.errorDefault, 'error');
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

// Individual toast component
const ToastItem = ({ toast, onRemove, style, index }) => {
    const [isVisible, setIsVisible] = useState(false);
    const timerRef = useRef(null);
    const elementRef = useRef(null);

    useEffect(() => {
        // Animación de entrada con pequeño delay para efecto escalonado
        const enterDelay = Math.min(index * 100, 400);
        const timer = setTimeout(() => {
            setIsVisible(true);
        }, enterDelay);
        
        return () => clearTimeout(timer);
    }, [index]);

    // Timer completamente independiente que inicia inmediatamente
    useEffect(() => {
        if (toast.duration <= 0) return;

        console.log(`Toast ${toast.id}: Timer iniciado por ${toast.duration}ms`);
        
        // Timer independiente que inicia inmediatamente cuando se monta el componente
        timerRef.current = setTimeout(() => {
            console.log(`Toast ${toast.id}: Timer terminado, eliminando...`);
            onRemove(toast.id);
        }, toast.duration);

        return () => {
            console.log(`Toast ${toast.id}: Timer limpiado`);
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, []); // Sin dependencias para que solo se ejecute una vez

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

    const handleRemove = () => {
        if (toast.isRemoving) return; // Prevenir clicks múltiples
        
        // Añadir clase para animación de salida inmediata
        if (elementRef.current) {
            elementRef.current.classList.add('toast-removing');
        }
        
        // Pequeño delay para que la animación se inicie
        requestAnimationFrame(() => {
            onRemove(toast.id);
        });
    };

    return (
        <div 
            ref={elementRef}
            data-toast-id={toast.id}
            className={`toast-item toast-${toast.type} ${isVisible ? 'toast-visible' : ''} ${toast.isRemoving ? 'toast-removing' : ''}`}
            style={{
                ...style,
                // Variables CSS para efectos de apilamiento
                '--stack-index': index,
                '--stack-offset': `${index * 4}px`,
                '--stack-scale': `${1 - (index * 0.02)}`
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
                aria-label={TOAST_TEXT.closeToast}
            >
                <MdClose />
            </button>
            {/* Simple progress bar - solo visual */}
            {toast.duration > 0 && !toast.isRemoving && (
                <div 
                    className="toast-progress-bar"
                    style={{
                        transform: 'scaleX(0)',
                        transitionDuration: `${toast.duration}ms`,
                        transitionTimingFunction: 'linear',
                        animation: `toast-progress ${toast.duration}ms linear forwards`
                    }}
                />
            )}
        </div>
    );
};

// Main toast container
const ToastContainer = ({ toasts, onRemove }) => {
    const flipRef = useFlipAnimation(toasts.length); // Trigger animation when toast count changes
    
    if (toasts.length === 0) return null;

    return (
        <div ref={flipRef} className="toast-container">
            {toasts.map((toast, index) => (
                <ToastItem
                    key={toast.id}
                    toast={toast}
                    onRemove={onRemove}
                    index={index}
                    style={{
                        zIndex: 1000 - index, // Los más nuevos aparecen arriba
                    }}
                />
            ))}
        </div>
    );
};

export default ToastContainer;
