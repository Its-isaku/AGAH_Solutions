import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import authApi from '../../services/AuthAPI';

function ProtectedRoute({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const authStatus = await authApi.isAuthenticated();
            setIsAuthenticated(authStatus);
        } catch (error) {
            console.error("Error checking authentication:", error);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    //? Mientras verifica la autenticación
    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                color: '#78B7D0'
            }}>
                <p>Checking authentication...</p>
                {/* <p>Verificando autenticación...</p> */}
            </div>
        );
    }

    //? If not authenticated, redirect to login
    if (!isAuthenticated) {
        //? Save the route they were trying to access
        const currentPath = window.location.pathname;
        sessionStorage.setItem('redirectAfterLogin', currentPath);
        return <Navigate to="/login" replace />;
    }

    //? If authenticated, show the component
    return children;
}

export default ProtectedRoute;