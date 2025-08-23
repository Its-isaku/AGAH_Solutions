import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../style/Contact.css';
import { MdEmail, MdPhone, MdLocationOn, MdAccessTime, MdCheck, MdClose, MdSupport } from 'react-icons/md';

function Contact() {
    //? Variables 
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
    });
    
    const [contactInfo, setContactInfo] = useState({
        email: 'info@agahsolutions.com',
        phone: '+1 (555) 123-4567',
        address: '123 Tech Street, Innovation City, TC 12345',
        name: 'AGAH Solutions'
    });
    
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitStatus, setSubmitStatus] = useState(null); 
    const [errors, setErrors] = useState({});

    //? Functions
    const fetchContactInfo = async () => {
        try {
            const contactData = await api.contact.getContactInfo();
            setContactInfo(contactData);
        } catch (error) {
            console.log('Using default contact info:', error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear specific error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.name.trim()) {
            // newErrors.name = 'El nombre es requerido';
            newErrors.name = 'Name is required';
        }
        
        if (!formData.email.trim()) {
            // newErrors.email = 'El email es requerido';
            newErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            // newErrors.email = 'Formato de email inválido';
            newErrors.email = 'Invalid email format';
        }
        
        if (!formData.subject.trim()) {
            // newErrors.subject = 'El asunto es requerido';
            newErrors.subject = 'Subject is required';
        }
        
        if (!formData.message.trim()) {
            // newErrors.message = 'El mensaje es requerido';
            newErrors.message = 'Message is required';
        } else if (formData.message.trim().length < 10) {
            // newErrors.message = 'El mensaje debe tener al menos 10 caracteres';
            newErrors.message = 'Message must be at least 10 characters';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
        };

        const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setIsSubmitting(true);
        setSubmitStatus(null);
        
        try {
            // Usar TU ContactAPI con validación incluida
            const result = await api.contact.sendValidatedContactForm(formData);
            
            if (result.success) {
            setSubmitStatus('success');
            setFormData({
                name: '',
                email: '',
                phone: '',
                subject: '',
                message: ''
            });
            } else {
            setSubmitStatus('error');
            console.error('Contact form error:', result.error);
            }
        } catch (error) {
            setSubmitStatus('error');
            console.error('Contact form submission error:', error);
        } finally {
            setIsSubmitting(false);
        }
        };

        // Load contact info on component mount
        useEffect(() => {
        fetchContactInfo();
        }, []);

        //? What is gonna be rendered
        return (
        <>
        {/*? Content */}
        <div className="contact-container">
            
            {/* Header Section */}
            <div className="contact-header">
            {/* <h1 className="contact-title">Contáctanos</h1> */}
            <h1 className="contact-title">Contact Us</h1>
            <p className="contact-subtitle">
                {/* ¿Tienes una idea innovadora? Estamos aquí para ayudarte a convertirla en realidad. */}
                Do you have an innovative idea? We're here to help you make it a reality.
            </p>
        </div>

            <div className="contact-content">
            
            {/* Contact Information */}
            <div className="contact-info-section">
                <div className="contact-info-card">
                {/* <h2 className="section-title">Información de Contacto</h2> */}
                <h2 className="section-title">Contact Information</h2>
                
                <div className="contact-details">
                    <div className="contact-item">
                    <div className="contact-icon email-icon"><MdEmail /></div>
                    <div className="contact-text">
                        <h3>Email</h3>
                        <p>{contactInfo.email}</p>
                    </div>
                    </div>
                    
                    <div className="contact-item">
                    <div className="contact-icon phone-icon"><MdPhone /></div>
                    <div className="contact-text">
                        {/* <h3>Teléfono</h3> */}
                        <h3>Phone</h3>
                        <p>{contactInfo.phone}</p>
                    </div>
                    </div>
                    
                    <div className="contact-item">
                    <div className="contact-icon address-icon"><MdLocationOn /></div>
                    <div className="contact-text">
                        {/* <h3>Dirección</h3> */}
                        <h3>Address</h3>
                        <p>{contactInfo.address}</p>
                    </div>
                    </div>
                    
                    <div className="contact-item">
                    <div className="contact-icon hours-icon"><MdAccessTime /></div>
                    <div className="contact-text">
                        {/* <h3>Horario</h3> */}
                        <h3>Hours</h3>
                        {/* <p>Lunes - Viernes: 9:00 AM - 6:00 PM</p> */}
                        <p>Monday - Friday: 9:00 AM - 6:00 PM</p>
                        {/* <p>Sábados: 10:00 AM - 2:00 PM</p> */}
                        <p>Saturdays: 10:00 AM - 2:00 PM</p>
                    </div>
                    </div>
                </div>
                </div>

                {/* Quick Response Info */}
                <div className="quick-response-card">
                {/* <h3>Respuesta Rápida</h3> */}
                <h3>Quick Response</h3>
                <p>
                    {/* Respondemos todos los mensajes dentro de las primeras 24 horas. */}
                    We respond to all messages within the first 24 hours.
                    {/* Para proyectos urgentes, contáctanos directamente por teléfono. */}
                    For urgent projects, contact us directly by phone.
                </p>
                </div>
            </div>

            {/* Contact Form */}
            <div className="contact-form-section">
                <div className="contact-form-card">
                {/* <h2 className="section-title">Envíanos un Mensaje</h2> */}
                <h2 className="section-title">Send Us a Message</h2>

                {/* Status Messages */}
                {submitStatus === 'success' && (
                    <div className="status-message success">
                    <span className="status-icon"><MdCheck /></span>
                    {/* <p>¡Mensaje enviado exitosamente! Te contactaremos pronto.</p> */}
                    <p>Message sent successfully! We'll contact you soon.</p>
                    </div>
                )}

                {submitStatus === 'error' && (
                    <div className="status-message error">
                    <span className="status-icon"><MdClose /></span>
                    {/* <p>Error al enviar el mensaje. Por favor, inténtalo de nuevo.</p> */}
                    <p>Error sending message. Please try again.</p>
                    </div>
                )}

                <div className="contact-form">
                    <div className="form-row">
                    <div className="form-group">
                        {/* <label htmlFor="name">Nombre *</label> */}
                        <label htmlFor="name">Name *</label>
                        <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className={errors.name ? 'error' : ''}
                        // placeholder="Tu nombre completo"
                        placeholder="Your full name"
                        />
                        {errors.name && <span className="error-text">{errors.name}</span>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email *</label>
                        <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className={errors.email ? 'error' : ''}
                        // placeholder="tu@email.com"
                        placeholder="your@email.com"
                        />
                        {errors.email && <span className="error-text">{errors.email}</span>}
                    </div>
                    </div>

                    <div className="form-row">
                    <div className="form-group">
                        {/* <label htmlFor="phone">Teléfono</label> */}
                        <label htmlFor="phone">Phone</label>
                        <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        placeholder="+1 (555) 123-4567"
                        />
                    </div>

                    <div className="form-group">
                        {/* <label htmlFor="subject">Asunto *</label> */}
                        <label htmlFor="subject">Subject *</label>
                        <input
                        type="text"
                        id="subject"
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        className={errors.subject ? 'error' : ''}
                        // placeholder="Tema de tu consulta"
                        placeholder="Topic of your inquiry"
                        />
                        {errors.subject && <span className="error-text">{errors.subject}</span>}
                    </div>
                    </div>

                    <div className="form-group full-width">
                    {/* <label htmlFor="message">Mensaje *</label> */}
                    <label htmlFor="message">Message *</label>
                    <textarea
                        id="message"
                        name="message"
                        rows="6"
                        value={formData.message}
                        onChange={handleInputChange}
                        className={errors.message ? 'error' : ''}
                        // placeholder="Cuéntanos sobre tu proyecto o consulta..."
                        placeholder="Tell us about your project or inquiry..."
                    ></textarea>
                    {errors.message && <span className="error-text">{errors.message}</span>}
                    </div>

                    <button
                    type="submit"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className={`submit-btn ${isSubmitting ? 'loading' : ''}`}
                    >
                    {isSubmitting ? (
                        <span className="loading-spinner"></span>
                    ) : (
                        <>
                        Send Message
                        </>
                    )}
                    </button>
                </div>
                </div>
            </div>
            </div>

            {/* Additional Info Section */}
            <div className="additional-info">
            <div className="info-card">
                <div className="info-icon"><MdCheck /></div>
                {/* <h3>Consulta Gratuita</h3> */}
                <h3>Free Consultation</h3>
                {/* <p>La primera consulta es completamente gratuita. Analiza tu proyecto sin compromiso.</p> */}
                <p>The first consultation is completely free. Analyze your project without commitment.</p>
            </div>

            <div className="info-card">
                <div className="info-icon"><MdAccessTime /></div>
                {/* <h3>Respuesta 24h</h3> */}
                <h3>24h Response</h3>
                {/* <p>Te contactamos en menos de 24 horas para discutir tu proyecto en detalle.</p> */}
                <p>We contact you within 24 hours to discuss your project in detail.</p>
            </div>

            <div className="info-card">
                <div className="info-icon"><MdSupport /></div>
                {/* <h3>Soporte Continuo</h3> */}
                <h3>Continuous Support</h3>
                {/* <p>Mantente informado durante todo el proceso de desarrollo de tu proyecto.</p> */}
                <p>Stay informed throughout your project development process.</p>
            </div>
            </div>
        </div>
        </>
        )
}

export default Contact