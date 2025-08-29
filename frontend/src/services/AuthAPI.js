//? Import axios
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
                    // Token expired or invalid
                    this.logout();
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    //* Login user with email and password
    async login(credentials) {
        try {
            const response = await this.api.post('/login/', {
                email: credentials.email || credentials.username,
                password: credentials.password
            });
            
            // Backend now returns {success, data}
            if (response.data.success) {
                const { token, user } = response.data.data;
                
                // Store token and user data
                this.setToken(token);
                this.setUser(user);
                
                return {
                    success: true,
                    data: response.data.data,
                    message: response.data.message || 'Login successful'
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Login failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Error al iniciar sesión'
            };
        }
    }

    //* Register new user
    async signup(userData) {
        try {
            const response = await this.api.post('/register/', userData);
            
            // Backend now returns {success, data}
            if (response.data.success) {
                const { token, user } = response.data.data;
                
                // Auto-login after successful registration
                if (token) {
                    this.setToken(token);
                    this.setUser(user);
                }
                
                return {
                    success: true,
                    data: response.data.data,
                    message: response.data.message || 'Account created successfully'
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Registration failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Error en el registro'
            };
        }
    }

    //* Logout user
    async logout() {
        try {
            // Try to logout from backend
            const token = this.getToken();
            if (token) {
                await this.api.post('/logout/');
            }
        } catch (error) {
            // Even if backend logout fails, clear local data
            console.error('Logout error:', error);
        } finally {
            // Always clear local storage
            this.clearAuth();
            
            return {
                success: true,
                message: 'Sesión cerrada exitosamente'
            };
        }
    }

    //* Get user profile
    async getProfile() {
        try {
            const response = await this.api.get('/profile/');
            
            if (response.data.success) {
                return {
                    success: true,
                    data: response.data.data
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to load profile'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Error loading profile'
            };
        }
    }

    //* Update user profile
    async updateProfile(profileData) {
        try {
            const response = await this.api.put('/profile/', profileData);
            
            if (response.data.success) {
                // Update stored user data
                const updatedUser = response.data.data;
                this.setUser(updatedUser);
                
                return {
                    success: true,
                    data: updatedUser,
                    message: response.data.message || 'Profile updated successfully'
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to update profile'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Error updating profile'
            };
        }
    }

    //* Change password
    async changePassword(passwordData) {
        try {
            const response = await this.api.post('/change-password/', passwordData);
            
            if (response.data.success) {
                // Update token if returned
                if (response.data.data?.token) {
                    this.setToken(response.data.data.token);
                }
                
                return {
                    success: true,
                    message: response.data.message || 'Password changed successfully'
                };
            } else {
                return {
                    success: false,
                    error: response.data.error || 'Failed to change password'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || error.message || 'Error changing password'
            };
        }
    }

    //* Request password reset - TEMPORARILY DISABLED
    async requestPasswordReset(email) {
        // TODO: Implement password reset views in backend first
        return {
            success: false,
            error: 'Password reset functionality not yet implemented'
        };
    }

    //* Reset password with token - TEMPORARILY DISABLED
    async resetPassword(token, newPassword) {
        // TODO: Implement password reset views in backend first
        return {
            success: false,
            error: 'Password reset functionality not yet implemented'
        };
    }

    //* Verify if user is authenticated
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
        // Also update default header for this instance
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

    //* Clear all auth data
    clearAuth() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        delete this.api.defaults.headers.Authorization;
    }

    //* Verify if token is still valid
    async verifyToken() {
        try {
            const response = await this.api.get('/status/');
            
            if (response.data.success) {
                return {
                    success: true,
                    valid: response.data.valid,
                    data: response.data.data
                };
            } else {
                return {
                    success: false,
                    valid: false
                };
            }
        } catch (error) {
            return {
                success: false,
                valid: false,
                error: error.response?.data?.error || error.message
            };
        }
    }

    //* Check if user is admin or staff
    isAdmin() {
        const user = this.getUser();
        return user && (user.is_staff || user.user_type === 'admin' || user.user_type === 'staff');
    }

    //* Check if user is customer
    isCustomer() {
        const user = this.getUser();
        return user && user.user_type === 'customer';
    }
}

//* Create and export singleton instance
const authAPI = new AuthAPI();
export default authAPI;