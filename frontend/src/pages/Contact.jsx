//?  Imports

//* React hooks 
import React, { useState, useEffect } from 'react';

//* Services
import api from '../services/api';

//* Styles
import '../style/Contact.css';

//* Icons
import { MdEmail, MdPhone, MdLocationOn, MdAccessTime, MdCheck, MdClose, MdSupport } from 'react-icons/md';

//?  Component
function Contact() {
    //? Variables 
    
    //* Form data state - stores all contact form information
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
    });
    
    //* Contact information state - stores company contact details
    const [contactInfo, setContactInfo] = useState({
        email: 'info@agahsolutions.com',
        phone: '+1 (555) 123-4567',
        address: '123 Tech Street, Innovation City, TC 12345',
        name: 'AGAH Solutions'
    });
    
    //* Form submission states
    const [isSubmitting, setIsSubmitting] = useState(false);        //* Loading state during form submission
    const [submitStatus, setSubmitStatus] = useState(null);         //* Success/error status after submission
    const [errors, setErrors] = useState({});                       //* Form validation errors

    //? Functions
    
    //* Fetches contact information from API
    const fetchContactInfo = async () => {
        try {
            const contactData = await api.contact.getContactInfo();
            setContactInfo(contactData);
        } catch (error) {
            console.log('Using default contact info:', error);
        }
    };

    //* Handles form input changes and clears specific errors
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        //* Clear specific error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    //* Validates contact form data and returns validation status
    const validateForm = () => {
        const newErrors = {};
        
        //* Name validation
        if (!formData.name.trim()) {
            newErrors.name = 'Name is required';
            // newErrors.name = 'El nombre es requerido';
        }
        
        //* Email validation
        if (!formData.email.trim()) {
            newErrors.email = 'Email is required';
            // newErrors.email = 'El email es requerido';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = 'Invalid email format';
            // newErrors.email = 'Formato de email inválido';
        }
        
        //* Subject validation
        if (!formData.subject.trim()) {
            newErrors.subject = 'Subject is required';
            // newErrors.subject = 'El asunto es requerido';
        }
        
        //* Message validation
        if (!formData.message.trim()) {
            newErrors.message = 'Message is required';
            // newErrors.message = 'El mensaje es requerido';
        } else if (formData.message.trim().length < 10) {
            newErrors.message = 'Message must be at least 10 characters';
            // newErrors.message = 'El mensaje debe tener al menos 10 caracteres';
            // newErrors.message = 'Message must be at least 10 characters';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    //* Handles form submission with validation and API call
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        //* Validate form before submission
        if (!validateForm()) {
            return;
        }
        
        //* Update submission states
        setIsSubmitting(true);
        setSubmitStatus(null);
        
        try {
            //* Use ContactAPI with included validation
            const result = await api.contact.sendValidatedContactForm(formData);
            
            if (result.success) {
                //* Success: reset form and show success message
                setSubmitStatus('success');
                setFormData({
                    name: '',
                    email: '',
                    phone: '',
                    subject: '',
                    message: ''
                });
            } else {
                //* Error: show error message
                setSubmitStatus('error');
                console.error('Contact form error:', result.error);
            }
        } catch (error) {
            //* Network/API error handling
            setSubmitStatus('error');
            console.error('Contact form submission error:', error);
        } finally {
            //* Reset loading state
            setIsSubmitting(false);
        }
    };

    //* Load contact info on component mount
    useEffect(() => {
        fetchContactInfo();
    }, []);

    //? What is gonna be rendered
    return (
        <>
            {/*? Content */}
            <div className="contact-container">
                
                {/*//* Header Section */}
                <div className="contact-header">
                    <h1 className="contact-title">Contact Us</h1>
                    {/* <h1 className="contact-title">Contáctanos</h1> */}
                    <p className="contact-subtitle">
                        Do you have an innovative idea? We're here to help you turn it into reality.
                        {/* ¿Tienes una idea innovadora? Estamos aquí para ayudarte a convertirla en realidad. */}
                    </p>
                </div>

                <div className="contact-content">
                    
                    {/*//* Contact Information Section */}
                    <div className="contact-info-section">
                        <div className="contact-info-card">
                            <h2 className="section-title">Contact Information</h2>
                            {/* <h2 className="section-title">Información de Contacto</h2> */}
                            
                            <div className="contact-details">
                                {/*//* Email Contact Item */}
                                <div className="contact-item">
                                    <div className="contact-icon email-icon"><MdEmail /></div>
                                    <div className="contact-text">
                                        <h3>Email</h3>
                                        <p>{contactInfo.email}</p>
                                    </div>
                                </div>
                                
                                {/*//* Phone Contact Item */}
                                <div className="contact-item">
                                    <div className="contact-icon phone-icon"><MdPhone /></div>
                                    <div className="contact-text">
                                        <h3>Phone</h3>
                                        {/* <h3>Teléfono</h3> */}
                                        <p>{contactInfo.phone}</p>
                                    </div>
                                </div>
                                
                                {/*//* Address Contact Item */}
                                <div className="contact-item">
                                    <div className="contact-icon address-icon"><MdLocationOn /></div>
                                    <div className="contact-text">
                                        <h3>Address</h3>
                                        {/* <h3>Dirección</h3> */}
                                        <p>{contactInfo.address}</p>
                                    </div>
                                </div>
                                
                                {/*//* Business Hours Contact Item */}
                                <div className="contact-item">
                                    <div className="contact-icon hours-icon"><MdAccessTime /></div>
                                    <div className="contact-text">
                                        <h3>Hours</h3>
                                        {/* <h3>Horario</h3> */}
                                        <p>Monday - Friday: 9:00 AM - 6:00 PM</p>
                                        {/* <p>Lunes - Viernes: 9:00 AM - 6:00 PM</p> */}
                                        <p>Saturdays: 10:00 AM - 2:00 PM</p>
                                        {/* <p>Sábados: 10:00 AM - 2:00 PM</p> */}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/*//* Quick Response Information Card */}
                        <div className="quick-response-card">
                            <h3>Quick Response</h3>
                            {/* <h3>Respuesta Rápida</h3> */}
                            <p>
                                We respond to all messages within the first 24 hours.
                                For urgent projects, contact us directly by phone.
                                {/* Respondemos todos los mensajes dentro de las primeras 24 horas.
                                Para proyectos urgentes, contáctanos directamente por teléfono. */}
                            </p>
                        </div>
                    </div>

                    {/*//* Contact Form Section */}
                    <div className="contact-form-section">
                        <div className="contact-form-card">
                            <h2 className="section-title">Send us a Message</h2> 
                            {/* <h2 className="section-title">Envíanos un Mensaje</h2> */}

                            {/*//* Status Messages */}
                            {submitStatus === 'success' && (
                                <div className="status-message success">
                                    <span className="status-icon"><MdCheck /></span>
                                    <p>Message sent successfully! We'll contact you soon.</p>
                                    {/* <p>¡Mensaje enviado exitosamente! Te contactaremos pronto.</p> */}
                                </div>
                            )}

                            {submitStatus === 'error' && (
                                <div className="status-message error">
                                    <span className="status-icon"><MdClose /></span>
                                    <p>Error sending message. Please try again.</p>
                                    {/* <p>Error al enviar el mensaje. Por favor, inténtalo de nuevo.</p> */}
                                </div>
                            )}

                            {/*//* Contact Form */}
                            <form className="contact-form" onSubmit={handleSubmit}>
                                {/*//* First Row: Name and Email */}
                                <div className="form-row">
                                    <div className="form-group">
                                        <label htmlFor="name">Name *</label>
                                        {/* <label htmlFor="name">Nombre *</label> */}
                                        <input
                                            type="text"
                                            id="name"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleInputChange}
                                            className={errors.name ? 'error' : ''}
                                            placeholder="Your full name"
                                            // placeholder="Tu nombre completo"
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
                                            placeholder="your@email.com"
                                            // placeholder="tu@email.com"
                                        />
                                        {errors.email && <span className="error-text">{errors.email}</span>}
                                    </div>
                                </div>

                                {/*//* Second Row: Phone and Subject */}
                                <div className="form-row">
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
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label htmlFor="subject">Subject *</label>
                                        {/* <label htmlFor="subject">Asunto *</label> */}
                                        <input
                                            type="text"
                                            id="subject"
                                            name="subject"
                                            value={formData.subject}
                                            onChange={handleInputChange}
                                            className={errors.subject ? 'error' : ''}
                                            placeholder="Subject of your inquiry"
                                            // placeholder="Tema de tu consulta"
                                        />
                                        {errors.subject && <span className="error-text">{errors.subject}</span>}
                                    </div>
                                </div>

                                {/*//* Message Text Area */}
                                <div className="form-group full-width">
                                    <label htmlFor="message">Message *</label>
                                    {/* <label htmlFor="message">Mensaje *</label> */}
                                    <textarea
                                        id="message"
                                        name="message"
                                        rows="6"
                                        value={formData.message}
                                        onChange={handleInputChange}
                                        className={errors.message ? 'error' : ''}
                                        placeholder="Tell us about your project or inquiry..."
                                        // placeholder="Cuéntanos sobre tu proyecto o consulta..."
                                    ></textarea>
                                    {errors.message && <span className="error-text">{errors.message}</span>}
                                </div>

                                {/*//* Submit Button */}
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className={`submit-btn ${isSubmitting ? 'loading' : ''}`}
                                >
                                    {isSubmitting ? (
                                        <span className="loading-spinner"></span>
                                    ) : (
                                        <>
                                            Send Message
                                            {/* Enviar Mensaje */}
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                {/*//* Additional Information Section */}
                <div className="additional-info">
                    {/*//* Free Consultation Card */}
                    <div className="info-card">
                        <div className="info-icon"><MdCheck /></div>
                        <h3>Free Consultation</h3>
                        {/* <h3>Consulta Gratuita</h3> */}
                        <p>The first consultation is completely free. Analyze your project without commitment.</p>
                        {/* <p>La primera consulta es completamente gratuita. Analiza tu proyecto sin compromiso.</p> */}
                    </div>

                    {/*//* 24h Response Card */}
                    <div className="info-card">
                        <div className="info-icon"><MdAccessTime /></div>
                        <h3>24h Response</h3>
                        {/* <h3>Respuesta 24h</h3> */}
                        <p>We contact you in less than 24 hours to discuss your project in detail.</p>
                        {/* <p>Te contactamos en menos de 24 horas para discutir tu proyecto en detalle.</p> */}
                    </div>

                    {/*//* Continuous Support Card */}
                    <div className="info-card">
                        <div className="info-icon"><MdSupport /></div>
                        <h3>Continuous Support</h3>
                        {/* <h3>Soporte Continuo</h3> */}
                        <p>Stay informed throughout your project's development process.</p>
                        {/* <p>Mantente informado durante todo el proceso de desarrollo de tu proyecto.</p> */}
                    </div>
                </div>
            </div>
        </>
    );
}

export default Contact;
