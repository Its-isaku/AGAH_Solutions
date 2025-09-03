import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './style/index.css'
import HomePage from './pages/HomePage.jsx'
import AboutUs from './pages/AboutUs.jsx'
import Services from './pages/Services.jsx'
import Contact from './pages/Contact.jsx'
import Login from './pages/Login.jsx'
import SignUp from './pages/SignUp.jsx'
import ResetPassword from './pages/ResetPassword.jsx'
import Cart from './pages/Cart.jsx'
import Orders from './pages/Orders.jsx'
import Navbar from './components/common/Navbar.jsx'
import Footer from './components/common/Footer.jsx'
import ProtectedRoute from './components/common/ProtectedRoute.jsx'
import { CartProvider } from './context/CartContext.jsx'
import { ToastProvider } from './context/ToastContext.jsx'

createRoot(document.getElementById('root')).render(
<StrictMode>
  <ToastProvider>
    <CartProvider>
      <Router>
        <Navbar />
        <main>
          <Routes>
            {/*//? Public routes */}
            {/* //? Rutas públicas */}
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutUs />} />
            <Route path="/services" element={<Services />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            
            {/*//? Protected routes - require authentication */}
            {/* //? Rutas protegidas - requieren autenticación */}
            <Route 
              path="/reset-password" 
              element={
                <ProtectedRoute>
                  <ResetPassword />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/cart" 
              element={
                <ProtectedRoute>
                  <Cart />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/orders" 
              element={
                <ProtectedRoute>
                  <Orders />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
        <Footer />
      </Router>
    </CartProvider>
  </ToastProvider>
</StrictMode>
)