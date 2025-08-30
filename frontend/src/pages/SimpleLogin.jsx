import React, { useState } from 'react';
import authAPI from '../services/AuthAPI';

function SimpleLogin() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Form submitted - preventing default and propagation');
        
        setLoading(true);
        setError('');
        
        try {
            console.log('Making login request...');
            const response = await authAPI.login({ email, password });
            console.log('Login response:', response);
            
            if (response.success) {
                console.log('Login successful!');
                alert('Login exitoso!');
            } else {
                console.log('Login failed:', response.error);
                setError(response.error || 'Error de login');
                setEmail('');
                setPassword('');
            }
        } catch (error) {
            console.error('Login catch error:', error);
            setError('Error de conexión');
            setEmail('');
            setPassword('');
        } finally {
            setLoading(false);
        }
        
        console.log('handleSubmit completed');
        return false; // Extra precaución
    };

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: '50px auto' }}>
            <h2>Simple Login Test</h2>
            
            {error && (
                <div style={{ 
                    background: 'red', 
                    color: 'white', 
                    padding: '10px', 
                    marginBottom: '10px',
                    borderRadius: '5px'
                }}>
                    {error}
                </div>
            )}
            
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '10px' }}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        style={{ width: '100%', padding: '10px' }}
                        required
                    />
                </div>
                
                <div style={{ marginBottom: '10px' }}>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={{ width: '100%', padding: '10px' }}
                        required
                    />
                </div>
                
                <button 
                    type="submit" 
                    disabled={loading}
                    style={{ 
                        width: '100%', 
                        padding: '10px',
                        background: loading ? 'gray' : 'blue',
                        color: 'white',
                        border: 'none',
                        cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                >
                    {loading ? 'Cargando...' : 'Login'}
                </button>
            </form>
            
            <p style={{ marginTop: '20px', fontSize: '12px', color: 'gray' }}>
                Abre la consola del navegador para ver los logs
            </p>
        </div>
    );
}

export default SimpleLogin;
