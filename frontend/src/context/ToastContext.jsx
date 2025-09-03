import React, { createContext, useContext } from 'react';
import { useToast } from '../components/common/Toast';
import ToastContainer from '../components/common/Toast';

const ToastContext = createContext();

export const useToastContext = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToastContext must be used within a ToastProvider');
    }
    return context;
};

export const ToastProvider = ({ children }) => {
    const toastHook = useToast();

    return (
        <ToastContext.Provider value={toastHook}>
            {children}
            <ToastContainer 
                toasts={toastHook.toasts} 
                onRemove={toastHook.removeToast}
            />
        </ToastContext.Provider>
    );
};
