//?  Imports

//* css 
import '../style/HomePage.css'

//* Components
import HeroSection from '../components/HomePage/HeroSection';
import ServicePreview from '../components/HomePage/ServicePreview';
import AboutUsPreview from '../components/HomePage/AboutUsPreview';

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
            <ServicePreview />

            {/*//?  About Us Preview */}
            <AboutUsPreview />
        </>
    )
}

export default HomePage
