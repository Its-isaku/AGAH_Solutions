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
        <div className="Navbar">
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                {/*//* Company Logo */}
                <div className="Navbar_Logo">
                    <img src="../img/AGAH_logo.png" alt="Company Logo" />
                    <h1>AGAH Solutions</h1>
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
                    <button>Login</button> {/*//* will make this dinamic later */}
                    <h1>Cart</h1>
                    <h1>Orders</h1>
                </div>
            </SpotlightCard>    
        </div>
        </>
    )
}

export default Navbar
