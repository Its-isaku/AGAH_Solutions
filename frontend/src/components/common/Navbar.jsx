//?  Imports
import { useState } from 'react'
import '../../style/Navbar.css'
import SpotlightNavbar from './Spotlights/SpotlightNavbar';
import LOGO from '../../img/AGAH_LOGO.png' 
import { Link } from 'react-router-dom';

//?  Component 
function Navbar() {
    //? Variables 
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    //? Functions
    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const closeMenu = () => {
        setIsMenuOpen(false);
    };

    //? What is gonna be rendered
    return (
        <>
            <SpotlightNavbar className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                <div className="Navbar_Content">
                    {/*//* Company Logo */}
                    <div className="Navbar_Logo">
                        <img src={LOGO} alt="Company Logo" />
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

                    {/*//* Account */}
                    <div className={`Navbar_Account ${isMenuOpen ? 'active' : ''}`}>
                        <Link to="#login" onClick={closeMenu}>Login</Link> {/*//* will make this dinamic later */}
                        <Link to="#home" onClick={closeMenu}>CART</Link>
                        <Link to="#home" onClick={closeMenu}>ORDERS</Link>
                    </div>
                </div>
            </SpotlightNavbar>    
        </>
    )
}

export default Navbar
