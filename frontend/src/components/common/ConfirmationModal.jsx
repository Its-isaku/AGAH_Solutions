import React from 'react';
import { MdDeleteOutline } from 'react-icons/md';
import '../../style/Services.css'; // Usar los estilos de Services

const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirmar", cancelText = "Cancelar" }) => {
    if (!isOpen) return null;

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className="modal-overlay" onClick={handleBackdropClick}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{title}</h2>
                    <button className="modal-close" onClick={onClose}>
                        &times;
                    </button>
                </div>
                
                <div className="modal-body">
                    <div className="confirmation-icon">
                        <MdDeleteOutline />
                    </div>
                    <p className="confirmation-message">{message}</p>
                </div>
                
                <div className="modal-footer">
                    <button 
                        className="modal-button-cancel" 
                        onClick={onClose}
                    >
                        {cancelText}
                    </button>
                    <button 
                        className="modal-button-submit" 
                        onClick={onConfirm}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;
