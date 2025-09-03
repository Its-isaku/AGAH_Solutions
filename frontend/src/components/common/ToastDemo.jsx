import React from 'react';
import { useToastContext } from '../context/ToastContext';

/**
 * Componente de demostración para probar todos los tipos de toasts
 * Úsalo temporalmente cuando necesites probar las notificaciones
 */
function ToastDemo() {
    const { success, error, warning, info, promise } = useToastContext();

    const demoStyles = {
        container: {
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            alignItems: 'center',
            background: 'rgba(0, 0, 0, 0.1)',
            borderRadius: '1rem',
            margin: '2rem'
        },
        buttonRow: {
            display: 'flex',
            gap: '0.75rem',
            flexWrap: 'wrap',
            justifyContent: 'center'
        },
        button: {
            padding: '0.75rem 1.5rem',
            borderRadius: '0.5rem',
            border: 'none',
            color: 'white',
            cursor: 'pointer',
            fontWeight: '500',
            transition: 'transform 0.2s ease',
            fontSize: '0.9rem'
        }
    };

    return (
        <div style={demoStyles.container}>
            <h3 style={{ color: '#F4E7E1', marginBottom: '1rem' }}>Demo de Toasts</h3>
            
            <div style={demoStyles.buttonRow}>
                <button 
                    onClick={() => success('¡Operación exitosa!')}
                    style={{ ...demoStyles.button, background: '#10B981' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Success Toast
                </button>
                
                <button 
                    onClick={() => error('Algo salió mal')}
                    style={{ ...demoStyles.button, background: '#EF4444' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Error Toast
                </button>
                
                <button 
                    onClick={() => warning('Revisa los datos')}
                    style={{ ...demoStyles.button, background: '#F59E0B' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Warning Toast
                </button>
                
                <button 
                    onClick={() => info('Información importante')}
                    style={{ ...demoStyles.button, background: '#3B82F6' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Info Toast
                </button>
            </div>

            <div style={demoStyles.buttonRow}>
                <button 
                    onClick={() => {
                        promise(
                            new Promise((resolve) => setTimeout(resolve, 2000)),
                            {
                                loading: 'Procesando...',
                                success: '¡Completado exitosamente!',
                                error: 'Error en el proceso'
                            }
                        );
                    }}
                    style={{ ...demoStyles.button, background: '#78B7D0' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Promise Toast (2s)
                </button>
                
                <button 
                    onClick={() => {
                        promise(
                            new Promise((_, reject) => setTimeout(() => reject(new Error('Fallo simulado')), 1500)),
                            {
                                loading: 'Intentando...',
                                success: '¡Éxito!',
                                error: 'Error simulado'
                            }
                        ).catch(() => {}); // Evitar error no manejado
                    }}
                    style={{ ...demoStyles.button, background: '#8B5CF6' }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                >
                    Promise Error (1.5s)
                </button>
            </div>
            
            <p style={{ color: '#78B7D0', fontSize: '0.9rem', textAlign: 'center', marginTop: '1rem' }}>
                Utiliza este componente temporalmente para probar los toasts.<br/>
                Elimínalo cuando ya no lo necesites.
            </p>
        </div>
    );
}

export default ToastDemo;
