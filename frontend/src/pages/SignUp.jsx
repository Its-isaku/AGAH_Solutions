//?  Imports
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function SignUp() {

    //? Variables 
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: ''
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
        
        //* Clear error when user starts typing
        if (error) {
            setError('');
        }
    };

    const validateForm = () => {
        if (!formData.firstName.trim()) {
            setError('First name is required');
            // setError('El nombre es requerido');
            return false;
        }
        if (!formData.lastName.trim()) {
            setError('Last name is required');
            // setError('El apellido es requerido');
            return false;
        }
        if (!formData.email.trim()) {
            setError('Email is required');
            // setError('El email es requerido');
            return false;
        }
        if (!formData.email.includes('@')) {
            setError('Please enter a valid email');
            // setError('Por favor ingresa un email válido');
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
        if (!formData.confirmPassword) {
            setError('You must confirm your password');
            // setError('Debes confirmar tu contraseña');
            return false;
        }
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            // setError('Las contraseñas no coinciden');
            return false;
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        setLoading(true);
        setError('');
        setSuccess('');
        
        try {
            //* Prepare data for backend
            const signupData = {
                first_name: formData.firstName.trim(),
                last_name: formData.lastName.trim(), 
                email: formData.email.trim().toLowerCase(),
                password: formData.password,
                confirm_password: formData.confirmPassword, //* Add this field for backend validation
                phone: formData.phone.trim() || null
            };

            console.log('Sending signup data:', signupData); // Debug log
            const response = await authAPI.signup(signupData);
            
            if (response.success) {
                setSuccess('Account created successfully! Logging in...');
                // setSuccess('¡Cuenta creada exitosamente! Iniciando sesión...');
                //* Redirect to dashboard or home after successful registration
                setTimeout(() => {
                    navigate('/');
                }, 2000);
            } else {
                setError(response.error || 'Error creating account');
                // setError(response.error || 'Error al crear la cuenta');
            }
        } catch (error) {
            setError('Connection error. Please try again.');
            // setError('Error de conexión. Por favor, inténtalo de nuevo.');
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

    //? What is gonna be rendered
    return (
        <>
        {/*//? Content */}
        <div className="auth-page-container">
            <div className="auth-content">
                <div className="auth-card-container">
                    <h1>Create Account</h1>
                    {/* <h1>Crear Cuenta</h1> */}
                    
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