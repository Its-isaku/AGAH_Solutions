//?  Imports
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaEnvelope, FaArrowLeft } from 'react-icons/fa';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function ForgotPassword() {
    //? Variables 
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    //? Functions
    const handleInputChange = (e) => {
        setEmail(e.target.value);
        if (error) setError('');
    };

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!email) {
            setError('El email es requerido');
            return;
        }
        
        if (!validateEmail(email)) {
            setError('Por favor ingresa un email válido');
            return;
        }
        
        setLoading(true);
        setError('');
        
        try {
            const response = await authAPI.requestPasswordReset(email);
            
            if (response.success) {
                setSuccess(true);
            } else {
                setError(response.error || 'Error al enviar el email de recuperación');
            }
        } catch (error) {
            console.error('Password reset request error:', error);
            setError('Connection error. Please try again.');
            //? setError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    //? What is gonna be rendered
    return (
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    {!success ? (
                        <>
                            <div className="auth-header">
                                <FaEnvelope className="auth-icon" />
                                <h1>Reset Password</h1>
                                {/* <h1>Recuperar Contraseña</h1> */}
                                <p className="auth-subtitle">
                                    Enter your email and we'll send you a link to reset your password
                                    {/* Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña */}
                                </p>
                            </div>
                            
                            {error && (
                                <div className="alert-error">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="auth-form">
                                <div className="form-group">
                                    <label htmlFor="email">Email *</label>
                                    <input
                                        type="email"
                                        id="email"
                                        name="email"
                                        value={email}
                                        onChange={handleInputChange}
                                        placeholder="your@email.com"
                                        /* placeholder="tu@email.com" */
                                        required
                                        autoComplete="email"
                                    />
                                </div>

                                <button 
                                    type="submit" 
                                    className="submit-btn"
                                    disabled={loading}
                                >
                                    {loading ? 'Sending...' : 'Send Recovery Email'}
                                    {/* {loading ? 'Enviando...' : 'Enviar Email de Recuperación'} */}
                                </button>
                            </form>
                        </>
                    ) : (
                        <div className="auth-header">
                            <FaEnvelope className="auth-icon success-icon" />
                            <h1>Email Sent</h1>
                            {/* <h1>Email Enviado</h1> */}
                            <p className="auth-subtitle">
                                We've sent a recovery link to <strong>{email}</strong>
                                {/* Hemos enviado un enlace de recuperación a <strong>{email}</strong> */}
                            </p>
                            <p className="auth-subtitle">
                                Check your inbox and spam folder. The link will expire in 1 hour.
                                {/* Revisa tu bandeja de entrada y spam. El enlace expirará en 1 hora. */}
                            </p>
                        </div>
                    )}

                    <div className="auth-links">
                        <Link to="/login" className="back-link">
                            <FaArrowLeft /> Back to login
                            {/* <FaArrowLeft /> Volver al login */}
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;
