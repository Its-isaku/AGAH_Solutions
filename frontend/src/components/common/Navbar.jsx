//?  Imports
import { useRef } from "react";
import '../../style/Navbar.css'
import SpotlightCard from './SpotlightCard';

//?  Component 
function Navbar() {
    //? Variables 
    

    //? Functions


    //? What is gonna be rendered
    return (
        <>
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                <div className="Navbar_Content">
                    {/*//* Company Logo */}
                    <div className="Navbar_Logo">
                        <img src="../img/AGAH_logo.png" alt="Company Logo" />
                        <a href="#home">AGAH Solutions</a>
                    </div>
                    
                    {/*//* Navigation Links */}
                    <nav className="Navbar_Links">
                        <ul>
                            <li><a href="#home">Home</a></li>
                            <li><a href="#about">About Us</a></li>
                            <li><a href="#services">Services</a></li>
                            <li><a href="#contact">Contact</a></li>
                        </ul>
                    </nav>

                    {/*//* Account */}
                    <div className="Navbar_Account">
                        <a href="#login">Login</a> {/*//* will make this dinamic later */}
                        <a href="#home">CART</a>
                        <a href="#home">ORDERS</a>
                    </div>
                </div>
            </SpotlightCard>    
        </>
    )
}

export default Navbar
