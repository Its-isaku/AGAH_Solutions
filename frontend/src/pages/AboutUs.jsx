//?  <|------------------------Imports------------------------|>

//* Imports  
import '../style/AboutUs.css';
import '../style/SpotlightAboutUs.css';
import FullLogo from '../img/AGAH_FullLogo.png';

//* Components
import SpotlightAboutUs from './../components/common/Spotlights/SpotlightAboutUs';


//* API 
import api from '../services/api';

//* States
import { useEffect, useState } from 'react';


//?  <|-----------------------Component-----------------------|> 
function AboutUs() {

    //? <|---------------------Variables---------------------|> 
    const [aboutUsData, setAboutUsData] = useState(null);                              //* About Us data
    const [error, setError] = useState(null);                                          //* Error state

    //?  <|---------------------Functions---------------------|>

    //* Loads About Us Data
    const loadAboutusData = async () => {
        try {
            if (error) setError(null);

            const data = await api.aboutUs.getAboutInfo();

            if (data) {
                setAboutUsData(data);
            } else {
                setError("Failed to Load About Us Data");
                console.log("Failed to Load About Us Data");
            }
        } catch (err) {
            setError(err?.message || "Failed to Load About Us Data");
            console.log("Failed to Load About Us Data");
        }
    }

    //?  <|-----------------------Hooks-----------------------|>
    useEffect(() => {
        loadAboutusData();
    }, []);


    //?  <|-------------What is gonna be rendered-------------|>
    return (
        <>
        {/*//* lanyard Section  */}
        <div className="AboutUs_FullLogo">
            <img src={FullLogo} alt="AGAH Solutions Full Logo" />   
        </div>

        <div className="AboutUs_container">
            {/*//* Main Info Section  */}
            <div className="AboutUs_info">
                <div className="aboutUs-card">
                    <h2>Our Story</h2>
                    {aboutUsData?.aboutUs || "Loading..."} 
                </div>
            </div>

            {/*//* Mission & Vision Section  */}
            <div className="AboutUs_missionVision">
                <div className="aboutUs-card">
                    <h2>Mission</h2>
                    <p>{aboutUsData?.mission || "Loading..."}</p>
                </div>

                <div className="aboutUs-card">
                    <h2>Vision</h2>
                    <p>{aboutUsData?.vision || "Loading..."}</p>
                </div>
            </div>

        </div>
        </>
    )
}

export default AboutUs
