//?  Imports

//* css 
import '../style/HomePage.css'

//* Components
import HeroSection from '../components/HomePage/HeroSection';
import MagicBento from '../components/HomePage/MagicBento';
import GradientText from '../components/common/GradientText';

//* API
import api from '../services/api'; 

//* States 
import { useEffect, useState } from 'react';


//?  Component 
function HomePage() {

    //? Variables 
    const [homepageData, setHomepageData] = useState(null)                //* Homepage data
    const [loading, setLoading] = useState(true)                         //* Loading state - set to true for initial loading
    const [error, setError] = useState(null)                              //* Error state


    //? Functions

    //* Loads Homepage Data
    const loadHomepageData = async () => {
        try {
            
            //* update states 
            setLoading(true);
            setError(null);

            console.log('Loading homepage data...');
            const result = await api.homepage.getHomepageData()

            if(result.success) {
                setHomepageData(result.data)
            } else {
                setError(result.error || '');
            }
        } catch (err) {
            setError('Server Connection Error');
            console.log('Connection Error:', err);
        } finally {
            setLoading(false);
        }
    }

    //? Prepares Hero Section Data
    const prepareHeroData = () => {
        if (!homepageData) return {};

        return {
            welcomeText: homepageData.welcomeText || "Welcome to",
            companyName: homepageData.companyName || "AGAH Solutions",
            tagline: "Cutting-Edge Solutions, Crafted to Perfection",
            featuredServices: homepageData.featuredServices || []
        }
    }

    //? Hooks
    useEffect(() => {
        loadHomepageData();
    }, []);


    //? Loading state
    if (loading) {
        return (
            <div className="homepage-loading">
                <div className="loading-content">
                    <div className="loading-spinner"></div>
                    <p>Cargando AGAH Solutions...</p>
                </div>
            </div>
        )
    }

    //? What is gonna be rendered
    return (
        <>
            {/*//? Hero Section */}
            <HeroSection heroData={prepareHeroData()} />

            {/*//?  Service Preview */}

            <div className="info_title">    
                <h2>
                    <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="custom-class"
                    >
                        Services Preview
                    </GradientText>
                </h2>
            </div>

            <div className='info_section'>
                <MagicBento 
                    textAutoHide={true}
                    enableStars={false}
                    enableSpotlight={true}
                    enableBorderGlow={true}
                    enableTilt={true}
                    enableMagnetism={true}
                    clickEffect={false}
                    spotlightRadius={300}
                    particleCount={12}
                    glowColor="132, 0, 255"
                />
            </div>


            {/*//? Lanyard */}
            <div className="lanyard_title">
                <h2>
                    <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="custom-class"
                    >
                        Services Preview
                    </GradientText>
                </h2>
            </div>

            <div className='Lanyard'>
                

            </div>

            {/*//?  About Us Preview */}
            <div className="about_preview_title">
                <h2>
                    <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="custom-class"
                    >
                        About Us Preview
                    </GradientText>
                </h2>
            </div>
            
            <div className='about_preview'>
            
            </div>
        </>
    )
}

export default HomePage
