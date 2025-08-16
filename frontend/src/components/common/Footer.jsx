//?  Imports
import '../../style/Footer.css'
import SpotlightFooter from './Spotlights/SpotlightFooter';
import { FaSquareFacebook } from "react-icons/fa6";
import { Link } from 'react-router-dom';

//?  Component 
function Footer() {
    //? Variables 
    

    //? Functions


    //? What is gonna be rendered
    return (
        <>
        <SpotlightFooter className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                <div className="Footer_Content">
                    {/*//? Contact Information */}
                    <div className='Footer_contact'>
                        <div className="Footer_Title">
                            <h2>Contact Us</h2>
                        </div>
                        <p><span>Email: </span>Agahsolutions@gmail.com</p>
                        <p><span>Phone: </span>+52 665 127 0811</p>
                        <p><span>Address: </span>Pending...</p> 
                    </div>
                    
                    {/*//? Links */}
                    <div className='Footer_links'>
                        <div className="Footer_Title">
                            <h2>Quick Links</h2>
                        </div>
                        <ul>
                            <li><Link to="/">Home</Link></li>
                            <li><Link to="/about">About Us</Link></li>
                            <li><Link to="/services">Services</Link></li>
                            <li><Link to="/contact">Contact</Link></li>
                        </ul>
                    </div>
                    {/*//? Social Media */}
                    <div className='Footer_social'>
                        <div className="Footer_Title">
                            <h2>Follow Us</h2>
                        </div>
                        <ul>
                            <li><a href="https://www.facebook.com/share/1C39VW1ojV/?mibextid=wwXIfr"><span><FaSquareFacebook size={24} /></span> Facebook</a></li>
                        </ul>
                    </div>
                </div>
            </SpotlightFooter>
        </>
    )
}

export default Footer


