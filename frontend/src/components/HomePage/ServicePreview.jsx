//?  Imports

//* Components
import MagicBento from '../common/MagicBento';
import GradientText from '../common/GradientText';


//?  Component 
function ServicePreview() {

    //? Variables 

    //? Functions

    //? Hooks

    //? What is gonna be rendered
    return (
        <>
            {/*//?  Service Preview */}
            <div className="info_title">    
                <h2>
                    <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={3}
                    showBorder={false}
                    className="custom-class"
                    >
                        {/* Lo que ofrecemos */}
                        Service Preview
                    </GradientText>
                </h2>
            </div>

            <div className='info_section'>
                <MagicBento 
                    textAutoHide={true}
                    enableStars={false}
                    enableSpotlight={true}
                    enableBorderGlow={true}
                    enableTilt={false}
                    enableMagnetism={false}
                    clickEffect={false}
                    spotlightRadius={200}
                    particleCount={12}
                    glowColor="132, 0, 255"
                />
            </div>
        </>
    )
}

export default ServicePreview;
