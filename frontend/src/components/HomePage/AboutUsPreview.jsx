//?  Imports

//* Components
import GradientText from '../common/GradientText';
import SpotlightCard from '../common/Spotlights/SpotlightCard';

//* API 
import api from '../../services/api'; 

//* states
import { useEffect, useState } from 'react';


//?  Component 
function AboutUsPreview() {

    //? Variables 
    const [aboutUsPreviewData, setAboutUsPreviewData] = useState(null);
    const [error, setError] = useState(null)                              //* Error state

    //? Functions
    
    //* Load AboutUs preview data
    const loadAboutUsPreviewData = async () => {
        try {
            const result = await api.aboutUs.AboutUsPreview();

            if(result.success) {
                setAboutUsPreviewData(result.data)
            } else  {
                setError(result.error || '');  
            }
        } catch (err) {
            setError('Server Connection Error');
            console.log('Connection Error:', err);
        }
    }

    //? Hooks
    useEffect(() => {
        loadAboutUsPreviewData();
    }, []);

    //? What is gonna be rendered
    return (
        <>
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
                <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                    <div className="about_preview_Info">
                        <h2>About us</h2>
                        <p>{aboutUsPreviewData?.description || ''}</p>
                    </div>
                    
                    <div className="about_preview_img">

                    </div>
                </SpotlightCard>
            </div>
        </>
    )
}

export default AboutUsPreview;
