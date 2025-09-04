// frontend/src/context/AuthContext.jsx

import React, { createContext, useContext, useState, useEffect } from 'react';

// Create AuthContext
const AuthContext = createContext();

// AuthProvider component
export function AuthProvider({ children }) {
    const [userInfo, setUserInfo] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    // Check if user is logged in on app start
    useEffect(() => {
        checkAuthStatus();
        
        // Listen for auth changes from other components
        const handleAuthChange = () => {
            checkAuthStatus();
        };
        
        window.addEventListener('auth-change', handleAuthChange);
        
        return () => {
            window.removeEventListener('auth-change', handleAuthChange);
        };
    }, []);

    // Function to check authentication status
    const checkAuthStatus = () => {
        try {
            const token = localStorage.getItem('authToken');
            const userData = localStorage.getItem('userData');
            
            if (token && userData) {
                try {
                    const user = JSON.parse(userData);
                    setUserInfo(user);
                    setIsAuthenticated(true);
                } catch (parseError) {
                    console.error('Error parsing user data:', parseError);
                    // Clear corrupted data
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('userData');
                    setUserInfo(null);
                    setIsAuthenticated(false);
                }
            } else {
                setUserInfo(null);
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            setUserInfo(null);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    // Function to login user
    const login = (userData, token) => {
        try {
            localStorage.setItem('authToken', token);
            localStorage.setItem('userData', JSON.stringify(userData));
            setUserInfo(userData);
            setIsAuthenticated(true);
            
            // Dispatch auth change event
            window.dispatchEvent(new Event('auth-change'));
        } catch (error) {
            console.error('Error during login:', error);
        }
    };

    // Function to logout user
    const logout = () => {
        try {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            setUserInfo(null);
            setIsAuthenticated(false);
            
            // Dispatch auth change event
            window.dispatchEvent(new Event('auth-change'));
        } catch (error) {
            console.error('Error during logout:', error);
        }
    };

    // Function to update user info
    const updateUserInfo = (newUserInfo) => {
        try {
            const updatedUser = { ...userInfo, ...newUserInfo };
            localStorage.setItem('userData', JSON.stringify(updatedUser));
            setUserInfo(updatedUser);
        } catch (error) {
            console.error('Error updating user info:', error);
        }
    };

    // Function to get auth token
    const getAuthToken = () => {
        return localStorage.getItem('authToken');
    };

    // Function to check if user has specific role
    const hasRole = (role) => {
        if (!userInfo) return false;
        return userInfo.user_type === role || userInfo.role === role;
    };

    // Function to check if user is admin
    const isAdmin = () => {
        return hasRole('admin') || hasRole('staff');
    };

    // Function to get user display name
    const getUserDisplayName = () => {
        if (!userInfo) return 'Usuario';
        
        if (userInfo.first_name && userInfo.last_name) {
            return `${userInfo.first_name} ${userInfo.last_name}`;
        }
        
        if (userInfo.first_name) {
            return userInfo.first_name;
        }
        
        if (userInfo.username) {
            return userInfo.username;
        }
        
        return userInfo.email || 'Usuario';
    };

    // Context value
    const value = {
        // State
        userInfo,
        isAuthenticated,
        loading,
        
        // Functions
        login,
        logout,
        updateUserInfo,
        checkAuthStatus,
        
        // Utilities
        getAuthToken,
        hasRole,
        isAdmin,
        getUserDisplayName
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom hook to use AuthContext
export function useAuthContext() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuthContext must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;