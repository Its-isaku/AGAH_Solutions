//?  Imports
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import { useToastContext } from '../context/ToastContext';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function SignUp() {

    //? Variables 
    const { success, error: showError, promise } = useToastContext();
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: ''
    });
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
    };

    const validateForm = () => {
        if (!formData.firstName.trim()) {
            showError('El nombre es requerido');
            return false;
        }
        if (!formData.lastName.trim()) {
            showError('El apellido es requerido');
            return false;
        }
        if (!formData.email.trim()) {
            showError('El email es requerido');
            return false;
        }
        if (!formData.email.includes('@')) {
            showError('Por favor ingresa un email válido');
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
        if (!formData.confirmPassword) {
            showError('Debes confirmar tu contraseña');
            return false;
        }
        if (formData.password !== formData.confirmPassword) {
            showError('Las contraseñas no coinciden');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        try {
            //* Prepare data for backend
            const signupData = {
                first_name: formData.firstName.trim(),
                last_name: formData.lastName.trim(), 
                email: formData.email.trim().toLowerCase(),
                password: formData.password,
                confirm_password: formData.confirmPassword,
                phone: formData.phone.trim() || null
            };

            await promise(
                authAPI.signup(signupData),
                {
                    loading: 'Creando tu cuenta...',
                    success: '¡Cuenta creada exitosamente! Bienvenido a AGAH Solutions',
                    error: 'Error al crear la cuenta. Verifica que el email no esté registrado'
                }
            );
            
            //* Redirect after successful registration
            setTimeout(() => {
                navigate('/');
            }, 2000);
            
        } catch (error) {
            console.error('Signup error:', error);
        }
    };

    const togglePasswordVisibility = (field) => {
        if (field === 'password') {
            setShowPassword(!showPassword);
        } else {
            setShowConfirmPassword(!showConfirmPassword);
        }
    };

    //? What is gonna be rendered
    return (
        <>
        {/*//? Content */}
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    <h1>Create Account</h1>
                    {/* <h1>Crear Cuenta</h1> */}

                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="firstName">First Name *</label>
                            {/* <label htmlFor="firstName">Nombre *</label> */}
                            <input
                                type="text"
                                id="firstName"
                                name="firstName"
                                value={formData.firstName}
                                onChange={handleInputChange}
                                placeholder="Your first name"
                                // placeholder="Tu nombre"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="lastName">Last Name *</label>
                            {/* <label htmlFor="lastName">Apellido *</label> */}
                            <input
                                type="text"
                                id="lastName"
                                name="lastName"
                                value={formData.lastName}
                                onChange={handleInputChange}
                                placeholder="Your last name"
                                // placeholder="Tu apellido"
                                required
                                disabled={loading}
                            />
                        </div>

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

                        <div className="form-group">
                            <label htmlFor="phone">Phone</label>
                            {/* <label htmlFor="phone">Teléfono</label> */}
                            <input
                                type="tel"
                                id="phone"
                                name="phone"
                                value={formData.phone}
                                onChange={handleInputChange}
                                placeholder="+1 (555) 123-4567"
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password *</label>
                            {/* <label htmlFor="password">Contraseña *</label> */}
                            <div className="password-container">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleInputChange}
                                    placeholder="Minimum 6 characters"
                                    // placeholder="Mínimo 6 caracteres"
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
                            <label htmlFor="confirmPassword">Confirm Password *</label>
                            {/* <label htmlFor="confirmPassword">Confirmar Contraseña *</label> */}
                            <div className="password-container">
                                <input
                                    type={showConfirmPassword ? 'text' : 'password'}
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleInputChange}
                                    placeholder="Confirm your password"
                                    // placeholder="Confirma tu contraseña"
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
                            {loading ? 'Creating account...' : 'Create Account'}
                            {/* {loading ? 'Creando cuenta...' : 'Crear Cuenta'} */}
                        </button>
                    </form>

                    <div className="auth-links">
                        <div className="separator">
                            <span>Already have an account?</span>
                            {/* <span>¿Ya tienes cuenta?</span> */}
                        </div>
                        <Link to="/login" className="login-link">
                            Log In
                            {/* Iniciar Sesión */}
                        </Link>
                    </div>
                </div>
            </div>
        </div>
        </>
    );
}

export default SignUp;