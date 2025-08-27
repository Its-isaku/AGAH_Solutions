//?  Imports
import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function ResetPassword() {

    //? Variables 
    const [searchParams] = useSearchParams();
    const [mode, setMode] = useState('request'); //* 'request' or 'confirm'
    const [token, setToken] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const navigate = useNavigate();


    //? Functions
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        //* Clear errors when user starts typing
        if (error) setError('');
    };

    const validateRequestForm = () => {
        if (!formData.email.trim()) {
            setError('El email es requerido');
            return false;
        }
        if (!formData.email.includes('@')) {
            setError('Por favor ingresa un email válido');
            return false;
        }
        return true;
    };

    const validateConfirmForm = () => {
        if (!formData.newPassword) {
            setError('La nueva contraseña es requerida');
            return false;
        }
        if (formData.newPassword.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        if (formData.newPassword !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return false;
        }
        return true;
    };

    const handleRequestSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateRequestForm()) return;
        
        setLoading(true);
        setError('');
        setSuccess('');
        
        try {
            const response = await authAPI.requestPasswordReset(formData.email);
            
            if (response.success) {
                setSuccess('Te hemos enviado un email con las instrucciones para restablecer tu contraseña. Por favor, revisa tu bandeja de entrada.');
                //* Clear form
                setFormData({ email: '', newPassword: '', confirmPassword: '' });
            } else {
                setError(response.error || 'Error al solicitar el restablecimiento');
            }
        } catch (error) {
            setError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateConfirmForm()) return;
        
        setLoading(true);
        setError('');
        setSuccess('');
        
        try {
            const response = await authAPI.resetPassword(token, formData.newPassword);
            
            if (response.success) {
                setSuccess('¡Contraseña restablecida exitosamente! Redirigiendo al inicio de sesión...');
                setTimeout(() => {
                    navigate('/login');
                }, 3000);
            } else {
                setError(response.error || 'Error al restablecer la contraseña. El enlace puede haber expirado.');
            }
        } catch (error) {
            setError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const togglePasswordVisibility = (field) => {
        if (field === 'password') {
            setShowPassword(!showPassword);
        } else {
            setShowConfirmPassword(!showConfirmPassword);
        }
    };

    //* Check URL parameters on component mount
    useEffect(() => {
        const tokenParam = searchParams.get('token');
        if (tokenParam) {
            setToken(tokenParam);
            setMode('confirm');
        }
    }, [searchParams]);

    //* Check if user is already authenticated (commented out to allow access)
    // useEffect(() => {
    //     if (authAPI.isAuthenticated()) {
    //         navigate('/');
    //     }
    // }, [navigate]);

    //? What is gonna be rendered
    return (
        <>
        {/*//? Content */}
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    <h1>
                        {mode === 'request' ? 'Restablecer Contraseña' : 'Nueva Contraseña'}
                    </h1>
                    
                    {error && (
                        <div className="alert-error">
                            {error}
                        </div>
                    )}
                    
                    {success && (
                        <div className="alert-success">
                            {success}
                        </div>
                    )}

                    {mode === 'request' ? (
                        <form onSubmit={handleRequestSubmit} className="auth-form">
                            <div className="form-group">
                                <label htmlFor="email">Email *</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    placeholder="tu@email.com"
                                    required
                                    disabled={loading}
                                />
                            </div>

                            <button 
                                type="submit" 
                                className="submit-btn"
                                disabled={loading}
                            >
                                {loading ? 'Enviando...' : 'Enviar Instrucciones'}
                            </button>
                        </form>
                    ) : (
                        <form onSubmit={handleConfirmSubmit} className="auth-form">
                            <div className="form-group">
                                <label htmlFor="newPassword">Nueva Contraseña *</label>
                                <div className="password-container">
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        id="newPassword"
                                        name="newPassword"
                                        value={formData.newPassword}
                                        onChange={handleInputChange}
                                        placeholder="Mínimo 6 caracteres"
                                        required
                                        disabled={loading}
                                    />
                                    <button
                                        type="button"
                                        className="password-toggle-btn"
                                        onClick={() => togglePasswordVisibility('password')}
                                        disabled={loading}
                                    >
                                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                                    </button>
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirmar Contraseña *</label>
                                <div className="password-container">
                                    <input
                                        type={showConfirmPassword ? 'text' : 'password'}
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleInputChange}
                                        placeholder="Confirma tu nueva contraseña"
                                        required
                                        disabled={loading}
                                    />
                                    <button
                                        type="button"
                                        className="password-toggle-btn"
                                        onClick={() => togglePasswordVisibility('confirm')}
                                        disabled={loading}
                                    >
                                        {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                                    </button>
                                </div>
                            </div>

                            <button 
                                type="submit" 
                                className="submit-btn"
                                disabled={loading}
                            >
                                {loading ? 'Actualizando...' : 'Actualizar Contraseña'}
                            </button>
                        </form>
                    )}

                    <div className="auth-links">
                        <Link to="/login" className="back-link">
                            ← Volver al inicio de sesión
                        </Link>
                        {mode === 'request' && (
                            <>
                                <div className="separator">
                                    <span>¿No tienes cuenta?</span>
                                </div>
                                <Link to="/signup" className="signup-link">
                                    Crear Cuenta Nueva
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
        </>
    );
}

export default ResetPassword;