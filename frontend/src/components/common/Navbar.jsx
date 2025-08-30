//?  Imports
import { useState, useEffect, useRef } from 'react'
import '../../style/Navbar.css'
import SpotlightNavbar from './Spotlights/SpotlightNavbar';
import LOGO from '../../img/AGAH_LOGO.png' 
import { Link, useNavigate, useLocation } from 'react-router-dom';
import authApi from "../../services/AuthAPI.js";
import { FaUser, FaChevronDown, FaShoppingCart, FaClipboardList, FaSignOutAlt, FaKey } from 'react-icons/fa';

//?  Component 
function Navbar() {
    //? Variables 
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    //? useEffect to verify authentication on load and when route changes
    useEffect(() => {
        //* Don't execute checkAuthStatus if we're on login page to avoid interference
        if (location.pathname === '/login' || location.pathname === '/signup') {
            return;
        }
        
        checkAuthStatus();
        
        //* Listen to custom authentication change event
        const handleAuthChange = () => {
            checkAuthStatus();
        };
        
        window.addEventListener('auth-change', handleAuthChange);
        
        return () => {
            window.removeEventListener('auth-change', handleAuthChange);
        };
    }, [location.pathname]); //* Re-verify when route changes

    //? useEffect to close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    //? Functions
    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const closeMenu = () => {
        setIsMenuOpen(false);
        setIsDropdownOpen(false);
    };

    const toggleDropdown = () => {
        if (!isDropdownOpen) {
            //* Calculate position BEFORE opening to avoid shaking
            const dropdown = dropdownRef.current;
            if (dropdown) {
                //* Create temporary element to measure
                const tempMenu = document.createElement('div');
                tempMenu.className = 'user-dropdown-menu';
                tempMenu.style.visibility = 'hidden';
                tempMenu.style.position = 'absolute';
                tempMenu.style.top = 'calc(100% + 10px)';
                tempMenu.style.right = '0';
                tempMenu.style.minWidth = '220px';
                dropdown.appendChild(tempMenu);
                
                const rect = tempMenu.getBoundingClientRect();
                const windowWidth = window.innerWidth;
                
                //* Apply class BEFORE showing dropdown
                if (rect.right > windowWidth - 20) {
                    dropdown.classList.add('dropdown-left');
                } else {
                    dropdown.classList.remove('dropdown-left');
                }
                
                //* Remove temporary element
                dropdown.removeChild(tempMenu);
            }
        }
        
        setIsDropdownOpen(!isDropdownOpen);
    };

    //* Check authentication status
    const checkAuthStatus = async () => {
        try {
            setLoading(true);
            const authStatus = await authApi.isAuthenticated();
            setIsAuthenticated(authStatus);
            
            if (authStatus) {
                //* If authenticated, get user data
                const userData = await authApi.getUser();
                setUser(userData);
            } else {
                setUser(null);
            }
        } catch (error) {
            console.error("Error checking authentication:", error);
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    //* Manejar logout
    const handleLogout = async () => {
        try {
            await authApi.logout();
            setIsAuthenticated(false);
            setUser(null);
            setIsDropdownOpen(false);
            closeMenu();
            
            //* Disparar evento de cambio de autenticación
            window.dispatchEvent(new Event('auth-change'));
            
            navigate('/');
        } catch (error) {
            console.error("Error during logout:", error);
        }
    };

    //* Manejar navegación protegida
    const handleProtectedNavigation = (path) => {
        if (!isAuthenticated) {
            //* Guardar la ruta a la que querían ir
            sessionStorage.setItem('redirectAfterLogin', path);
            navigate('/login', { state: { from: location.pathname } });
        } else {
            navigate(path);
        }
        closeMenu();
    };

    //? What is gonna be rendered
    return (
        <>
            <SpotlightNavbar 
                className="custom-spotlight-card" 
                spotlightColor="rgba(0, 229, 255, 0.2)"
                style={{ overflow: 'visible' }}
            >
                <div className="Navbar_Content">
                    {/*//* Company Logo */}
                    <div className="Navbar_Logo">
                        <Link to="/">
                            <img src={LOGO} alt="Company Logo" />
                        </Link>
                    </div>
                    
                    {/*//* Hamburger Menu Button */}
                    <button 
                        className={`Navbar_Hamburger ${isMenuOpen ? 'active' : ''}`}
                        onClick={toggleMenu}
                        aria-label="Toggle menu"
                    >
                        {/*//*Manual Hamburger Icon */}
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                    
                    {/*//* Navigation Links */}
                    <nav className={`Navbar_Links ${isMenuOpen ? 'active' : ''}`}>
                        <ul>
                            <li><Link to="/" onClick={closeMenu}>Home</Link></li>
                            <li><Link to="/about" onClick={closeMenu}>About Us</Link></li> 
                            <li><Link to="/services" onClick={closeMenu}>Services</Link></li>
                            <li><Link to="/contact" onClick={closeMenu}>Contact</Link></li>
                        </ul>
                    </nav>

                    {/*//* Account Section */}
                    <div className={`Navbar_Account ${isMenuOpen ? 'active' : ''}`}>
                        {loading ? (
                            <span className="loading-text">...</span>
                        ) : isAuthenticated && user ? (
                            <>
                                {/*//* Carrito y Órdenes - Solo visible cuando está logueado */}
                                <Link 
                                    to="/cart" 
                                    onClick={closeMenu}
                                    className="nav-icon-link"
                                    title="Carrito"
                                >
                                    <FaShoppingCart />
                                </Link>
                                <Link 
                                    to="/orders" 
                                    onClick={closeMenu}
                                    className="nav-icon-link"
                                    title="Órdenes"
                                >
                                    <FaClipboardList />
                                </Link>

                                {/*//* Dropdown de usuario */}
                                <div className="user-dropdown" ref={dropdownRef}>
                                    <button 
                                        className="user-dropdown-toggle"
                                        onClick={toggleDropdown}
                                    >
                                        <FaUser />
                                        <span>{user.first_name || user.email?.split('@')[0] || 'Usuario'}</span>
                                        <FaChevronDown className={`chevron ${isDropdownOpen ? 'rotate' : ''}`} />
                                    </button>

                                    {isDropdownOpen && (
                                        <div className="user-dropdown-menu">
                                            <div className="dropdown-header">
                                                <p className="user-email">{user.email}</p>
                                                <p className="user-name">
                                                    {user.first_name && user.last_name 
                                                        ? `${user.first_name} ${user.last_name}`
                                                        : 'Usuario'}
                                                </p>
                                            </div>
                                            <div className="dropdown-divider"></div>
                                            <Link 
                                                to="/reset-password" 
                                                className="dropdown-item"
                                                onClick={closeMenu}
                                            >
                                                <FaKey />
                                                <span>Change Password</span>
                                                {/* <span>Cambiar Contraseña</span> */}
                                            </Link>
                                            <button 
                                                className="dropdown-item logout"
                                                onClick={handleLogout}
                                            >
                                                <FaSignOutAlt />
                                                <span>Log Out</span>
                                                {/* <span>Cerrar Sesión</span> */}
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <Link to="/login" onClick={closeMenu} className="login-btn">
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </SpotlightNavbar>    
        </>
    )
}

export default Navbar