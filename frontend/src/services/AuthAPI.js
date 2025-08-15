//? import axios 
import axios from 'axios';

//? <|--------------------Auth API class---------------------|>
class AuthAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000/api/auth';
        this.api = axios.create({
            baseURL: this.baseURL,
            headers: {
                'Content-Type': 'application/json',
            }
        });

        //* Setup interceptors for automatic token handling
        this.setupInterceptors();
    }

    //* Method to setup request/response interceptors
    setupInterceptors() {
        //* Request interceptor: Add token to every request automatically
        this.api.interceptors.request.use(
            (config) => {
                const token = this.getToken();
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        //* Response interceptor: Handle token expiration
        this.api.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    this.logout();
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    //* Login user with email/username and password
    async login(credentials) {
        try {
            const response = await this.api.post('/login/', credentials);
            
            //* Store token and user data
            if (response.data.token) {
                this.setToken(response.data.token);
                this.setUser(response.data.user);
            }
            
            return {
                success: true,
                data: response.data,
                message: 'Inicio de sesión exitoso'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al iniciar sesión',
                details: error.response?.data
            };
        }
    }

    //* Register new user
    async signup(userData) {
        try {
            const response = await this.api.post('/signup/', userData);
            
            //* Auto-login after successful registration
            if (response.data.token) {
                this.setToken(response.data.token);
                this.setUser(response.data.user);
            }
            
            return {
                success: true,
                data: response.data,
                message: 'Cuenta creada exitosamente'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error en el registro',
                details: error.response?.data
            };
        }
    }

    //* Logout user (clear local storage and redirect)
    logout() {
        try {
            //* Remove token and user data from storage
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            
            //* Clear axios default headers
            delete this.api.defaults.headers.Authorization;
            
            return {
                success: true,
                message: 'Sesión cerrada exitosamente'
            };
        } catch (error) {
            return {
                success: false,
                error: 'Error al cerrar sesión'
            };
        }
    }

    //* Request password reset email
    async resetPassword(email) {
        try {
            const response = await this.api.post('/password-reset/', { email });
            
            return {
                success: true,
                data: response.data,
                message: 'Correo de restablecimiento de contraseña enviado'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al restablecer contraseña',
                details: error.response?.data
            };
        }
    }

    //* Confirm password reset with token
    async confirmPasswordReset(token, newPassword) {
        try {
            const response = await this.api.post('/password-reset-confirm/', {
                token,
                new_password: newPassword
            });
            
            return {
                success: true,
                data: response.data,
                message: 'Contraseña restablecida exitosamente'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al confirmar restablecimiento de contraseña',
                details: error.response?.data
            };
        }
    }

    //* Get current user profile
    async getProfile() {
        try {
            const response = await this.api.get('/profile/');
            
            //* Update stored user data
            this.setUser(response.data);
            
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al obtener el perfil',
                details: error.response?.data
            };
        }
    }

    //* Update user profile
    async updateProfile(profileData) {
        try {
            const response = await this.api.put('/profile/', profileData);
            
            //* Update stored user data
            this.setUser(response.data);
            
            return {
                success: true,
                data: response.data,
                message: 'Perfil actualizado exitosamente'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al actualizar el perfil',
                details: error.response?.data
            };
        }
    }

    //* Change user password (when logged in)
    async changePassword(currentPassword, newPassword) {
        try {
            const response = await this.api.post('/change-password/', {
                current_password: currentPassword,
                new_password: newPassword
            });
            
            return {
                success: true,
                data: response.data,
                message: 'Contraseña cambiada exitosamente'
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || 'Error al cambiar la contraseña',
                details: error.response?.data
            };
        }
    }

    //* Check if user is authenticated
    isAuthenticated() {
        const token = this.getToken();
        const user = this.getUser();
        return !!(token && user);
    }

    //* Get stored authentication token
    getToken() {
        return localStorage.getItem('authToken');
    }

    //* Store authentication token
    setToken(token) {
        localStorage.setItem('authToken', token);
        this.api.defaults.headers.Authorization = `Bearer ${token}`;
    }

    //* Get stored user data
    getUser() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }

    //* Store user data
    setUser(userData) {
        localStorage.setItem('userData', JSON.stringify(userData));
    }

    //* Verify if token is still valid
    async verifyToken() {
        try {
            const response = await this.api.post('/verify-token/');
            return {
                success: true,
                valid: response.data.valid
            };
        } catch (error) {
            return {
                success: false,
                valid: false
            };
        }
    }

    //* Refresh authentication token
    async refreshToken() {
        try {
            const response = await this.api.post('/refresh-token/');
            
            if (response.data.token) {
                this.setToken(response.data.token);
            }
            
            return {
                success: true,
                data: response.data
            };
        } catch (error) {
            this.logout();
            return {
                success: false,
                error: 'Error al renovar el token'
            };
        }
    }
}

export default AuthAPI;
