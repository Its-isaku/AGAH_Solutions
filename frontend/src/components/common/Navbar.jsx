//?  Imports
import { useState } from 'react'
import '../../style/Navbar.css'
import SpotlightNavbar from './Spotlights/SpotlightNavbar';
import LOGO from '../../img/AGAH_LOGO.png' 

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
                            <li><a href="#home" onClick={closeMenu}>Home</a></li>
                            <li><a href="#about" onClick={closeMenu}>About Us</a></li> 
                            <li><a href="#services" onClick={closeMenu}>Services</a></li>
                            <li><a href="#contact" onClick={closeMenu}>Contact</a></li>
                        </ul>
                    </nav>

                    {/*//* Account */}
                    <div className={`Navbar_Account ${isMenuOpen ? 'active' : ''}`}>
                        <a href="#login" onClick={closeMenu}>Login</a> {/*//* will make this dinamic later */}
                        <a href="#home" onClick={closeMenu}>CART</a>
                        <a href="#home" onClick={closeMenu}>ORDERS</a>
                    </div>
                </div>
            </SpotlightNavbar>    
        </>
    )
}

export default Navbar
