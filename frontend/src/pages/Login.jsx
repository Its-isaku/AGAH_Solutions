//?  Imports
import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function Login() {

    //? Variables 
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

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

    const validateForm = () => {
        if (!formData.email.trim()) {
            setError('Email is required');
            // setError('El email es requerido');
            return false;
        }
        if (!formData.password) {
            setError('Password is required');
            // setError('La contraseña es requerida');
            return false;
        }
        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            // setError('La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        e.stopPropagation(); // Prevenir cualquier propagación del evento
        
        if (!validateForm()) return;
        
        setLoading(true);
        setError('');
        setSuccess('');
        
        try {
            const response = await authAPI.login(formData);
            
            if (response.success) {
                setSuccess('Login successful!');
                // setSuccess('¡Inicio de sesión exitoso!');
                
                //* Force navbar update
                window.dispatchEvent(new Event('auth-change'));
                
                //* Check if there's a saved route to redirect to
                const redirectPath = sessionStorage.getItem('redirectAfterLogin');
                
                setTimeout(() => {
                    if (redirectPath) {
                        //* Clear saved route
                        sessionStorage.removeItem('redirectAfterLogin');
                        navigate(redirectPath);
                    } else if (location.state?.from) {
                        //* If came from a specific route
                        navigate(location.state.from);
                    } else {
                        //* If no saved route, go to home
                        navigate('/');
                    }
                }, 1000);
                
            } else {
                //* Show specific server error and clear inputs
                setError(response.error || 'Incorrect credentials');
                // setError(response.error || 'Credenciales incorrectas');
                //* Clear inputs to allow user to try again
                setFormData({
                    email: '',
                    password: ''
                });
                //* Don't navigate or reload on error
                return;
            }
        } catch (error) {
            console.error('Login error:', error);
            setError('Connection error. Please try again.');
            // setError('Error de conexión. Por favor, inténtalo de nuevo.');
            //* Clear inputs on connection error too
            setFormData({
                email: '',
                password: ''
            });
            //* Don't navigate or reload on error
            return;
        } finally {
            setLoading(false);
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    //* Check if user is already authenticated (solo al montar el componente)
    useEffect(() => {
        const checkAuth = async () => {
            //* Only verify on initial load, not during login process
            if (!loading && !error && !success) {
                const isAuth = await authAPI.isAuthenticated();
                if (isAuth) {
                    navigate('/');
                }
            }
        };
        checkAuth();
    }, [navigate]); //* Removed loading, error, success from dependencies

    //? What is gonna be rendered
    return (
        <>
        {/*//? Content */}
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    <h1>Log In</h1>
                    {/* <h1>Iniciar Sesión</h1> */}
                    
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

                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="email">Email *</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                placeholder="your@email.com"
                                // placeholder="tu@email.com"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password *</label>
                            {/* <label htmlFor="password">Contraseña *</label> */}
                            <div className="password-input-wrapper">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={togglePasswordVisibility}
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                    // aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                >
                                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            className="submit-btn"
                            disabled={loading}
                        >
                            {loading ? 'Logging in...' : 'Log In'}
                            {/* {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'} */}
                        </button>
                    </form>

                    <div className="auth-links">
                        <Link to="/reset-password" className="forgot-link">
                            Forgot your password?
                            {/* ¿Olvidaste tu contraseña? */}
                        </Link>
                        
                        <div className="separator">
                            <span>Don't have an account?</span>
                            {/* <span>¿No tienes cuenta?</span> */}
                        </div>
                        
                        <Link to="/signup" className="signup-link">
                            Create New Account
                            {/* Crear Cuenta Nueva */}
                        </Link>
                    </div>
                </div>
            </div>
        </div>
        </>
    );
}

export default Login;