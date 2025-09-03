//?  Imports
import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { useToastContext } from '../context/ToastContext';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function Login() {

    //? Variables 
    const { success, error: showError, promise } = useToastContext();
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
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
    };

    const validateForm = () => {
        if (!formData.email.trim()) {
            showError('El email es requerido');
            return false;
        }
        if (!formData.password) {
            showError('La contraseña es requerida');
            return false;
        }
        if (formData.password.length < 6) {
            showError('La contraseña debe tener al menos 6 caracteres');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (!validateForm()) return;
        
        try {
            await promise(
                authAPI.login(formData),
                {
                    loading: 'Iniciando sesión...',
                    success: '¡Inicio de sesión exitoso! Bienvenido de vuelta',
                    error: 'Credenciales incorrectas. Por favor, verifica tu email y contraseña'
                }
            );
            
            //* Force navbar update
            window.dispatchEvent(new Event('auth-change'));
            
            //* Check redirect paths
            const redirectPath = sessionStorage.getItem('redirectAfterLogin');
            
            setTimeout(() => {
                if (redirectPath) {
                    sessionStorage.removeItem('redirectAfterLogin');
                    navigate(redirectPath);
                } else if (location.state?.from) {
                    navigate(location.state.from);
                } else {
                    navigate('/');
                }
            }, 1500);
            
        } catch (error) {
            console.error('Login error:', error);
            //* Clear inputs on error
            setFormData({
                email: '',
                password: ''
            });
        }
    };

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    //* Check if user is already authenticated (solo al montar el componente)
    useEffect(() => {
        const checkAuth = async () => {
            //* Only verify on initial load, not during login process
            if (!loading) {
                const isAuth = await authAPI.isAuthenticated();
                if (isAuth) {
                    navigate('/');
                }
            }
        };
        checkAuth();
    }, [navigate, loading]); //* Only depend on navigate and loading

    //? What is gonna be rendered
    return (
        <>
        {/*//? Content */}
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    <h1>Log In</h1>
                    {/* <h1>Iniciar Sesión</h1> */}

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
                        >
                            Log In
                            {/* Iniciar Sesión */}
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