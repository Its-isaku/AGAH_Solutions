//?  Imports
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash, FaLock } from 'react-icons/fa';
import authAPI from '../services/AuthAPI';
import '../style/AuthStyle.css';

//?  Component 
function ResetPassword() {

    //? Variables 
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
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

    const validateForm = () => {
        //* Validate current password
        if (!formData.currentPassword) {
            setError('Current password is required');
            // setError('La contraseña actual es requerida');
            return false;
        }
        
        //* Validate new password
        if (!formData.newPassword) {
            setError('New password is required');
            // setError('La nueva contraseña es requerida');
            return false;
        }
        
        if (formData.newPassword.length < 8) {
            setError('New password must be at least 8 characters');
            // setError('La nueva contraseña debe tener al menos 8 caracteres');
            return false;
        }
        
        //* Validate that new password is different from current
        if (formData.currentPassword === formData.newPassword) {
            setError('New password must be different from current password');
            // setError('La nueva contraseña debe ser diferente a la actual');
            return false;
        }
        
        //* Validate password confirmation
        if (!formData.confirmNewPassword) {
            setError('You must confirm your new password');
            // setError('Debes confirmar tu nueva contraseña');
            return false;
        }
        
        if (formData.newPassword !== formData.confirmNewPassword) {
            setError('New passwords do not match');
            // setError('Las nuevas contraseñas no coinciden');
            return false;
        }
        
        //* Additional security validation (optional)
        const hasUpperCase = /[A-Z]/.test(formData.newPassword);
        const hasLowerCase = /[a-z]/.test(formData.newPassword);
        const hasNumbers = /\d/.test(formData.newPassword);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(formData.newPassword);
        
        if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
            setError('Password must contain uppercase, lowercase and numbers');
            // setError('La contraseña debe contener mayúsculas, minúsculas y números');
            return false;
        }
        
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        //* Verify authentication before proceeding
        if (!authAPI.isAuthenticated()) {
            setError('You must be authenticated to change your password. Please log in again.');
            // setError('Debes estar autenticado para cambiar tu contraseña. Por favor, inicia sesión nuevamente.');
            setTimeout(() => navigate('/login'), 2000);
            return;
        }
        
        setLoading(true);
        setError('');
        setSuccess('');
        
        try {
            //* Prepare data for backend
            const passwordData = {
                old_password: formData.currentPassword,
                new_password: formData.newPassword,
                confirm_password: formData.confirmNewPassword  //* Changed from confirm_new_password
            };
            
            const response = await authAPI.changePassword(passwordData);
            
            if (response.success) {
                setSuccess('Password updated successfully!');
                // setSuccess('¡Contraseña actualizada exitosamente!');
                
                //* Clear the form
                setFormData({
                    currentPassword: '',
                    newPassword: '',
                    confirmNewPassword: ''
                });
                
                //* Redirect after 2 seconds
                setTimeout(() => {
                    navigate('/');
                }, 2000);
            } else {
                setError(response.error || 'Error changing password');
                // setError(response.error || 'Error al cambiar la contraseña');
            }
        } catch (error) {
            console.error('Password change error:', error);
            setError('Connection error. Please try again.');
            // setError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const togglePasswordVisibility = (field) => {
        if (field === 'current') {
            setShowCurrentPassword(!showCurrentPassword);
        } else if (field === 'new') {
            setShowNewPassword(!showNewPassword);
        } else if (field === 'confirm') {
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
                    <div className="auth-header">
                        <FaLock className="auth-icon" />
                        <h1>Change Password</h1>
                        {/* <h1>Cambiar Contraseña</h1> */}
                        <p className="auth-subtitle">
                            For security, enter your current password to create a new one
                            {/* Por seguridad, ingresa tu contraseña actual para crear una nueva */}
                        </p>
                    </div>
                    
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
                        {/* Current Password */}
                        {/* {/* Contraseña Actual */}
                        <div className="form-group">
                            <label htmlFor="currentPassword">Current Password *</label>
                            {/* <label htmlFor="currentPassword">Contraseña Actual *</label> */}
                            <div className="password-input-wrapper">
                                <input
                                    type={showCurrentPassword ? "text" : "password"}
                                    id="currentPassword"
                                    name="currentPassword"
                                    value={formData.currentPassword}
                                    onChange={handleInputChange}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => togglePasswordVisibility('current')}
                                    aria-label={showCurrentPassword ? "Hide password" : "Show password"}
                                    // aria-label={showCurrentPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                >
                                    {showCurrentPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                        </div>

                        <div className="form-divider"></div>

                        {/* New Password */}
                        {/* {/* Nueva Contraseña */}
                        <div className="form-group">
                            <label htmlFor="newPassword">New Password *</label>
                            {/* <label htmlFor="newPassword">Nueva Contraseña *</label> */}
                            <div className="password-input-wrapper">
                                <input
                                    type={showNewPassword ? "text" : "password"}
                                    id="newPassword"
                                    name="newPassword"
                                    value={formData.newPassword}
                                    onChange={handleInputChange}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="new-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => togglePasswordVisibility('new')}
                                    aria-label={showNewPassword ? "Hide password" : "Show password"}
                                    // aria-label={showNewPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                >
                                    {showNewPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                            <small className="password-hint">
                                Minimum 8 characters, include uppercase, lowercase and numbers
                                {/* Mínimo 8 caracteres, incluye mayúsculas, minúsculas y números */}
                            </small>
                        </div>

                        {/* Confirm New Password */}
                        {/* {/* Confirmar Nueva Contraseña */}
                        <div className="form-group">
                            <label htmlFor="confirmNewPassword">Confirm New Password *</label>
                            {/* <label htmlFor="confirmNewPassword">Confirmar Nueva Contraseña *</label> */}
                            <div className="password-input-wrapper">
                                <input
                                    type={showConfirmPassword ? "text" : "password"}
                                    id="confirmNewPassword"
                                    name="confirmNewPassword"
                                    value={formData.confirmNewPassword}
                                    onChange={handleInputChange}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="new-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => togglePasswordVisibility('confirm')}
                                    aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                                    // aria-label={showConfirmPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                >
                                    {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                                </button>
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            className="submit-btn"
                            disabled={loading || success}
                        >
                            {loading ? 'Updating...' : 'Update Password'}
                            {/* {loading ? 'Actualizando...' : 'Actualizar Contraseña'} */}
                        </button>
                    </form>

                    <div className="auth-links">
                        <Link to="/" className="back-link">
                            ← Back to home
                            {/* ← Volver al inicio */}
                        </Link>
                    </div>
                </div>
            </div>
        </div>
        </>
    );
}

export default ResetPassword;