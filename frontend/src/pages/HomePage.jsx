//?  Imports
import '../style/HomePage.css'
import SplitText from "../components/common/SplitText";
import CardSwap, { Card } from '../components/common/CardSwap'
import Carousel from '../components/common/Carousel'
import plasmaCuttingImg from '../img/plasma_cutting.jpg'
import lasserEngravingImg from '../img/laser_engravingpng.png'
import PrintingImg from '../img/3D_printing.jpg'


//?  Component 
function HomePage() {

    //? Variables 
    const welcomeText = "Welcome to";
    const companyName = "AGAH Solutions";
    const carouselItems = [
        {
            id: 1,
            title: "Plasma Cutting",
            image: plasmaCuttingImg
        },
        {
            id: 2,
            title: "Laser Engraving",
            image: lasserEngravingImg
        },
        {
            id: 3,
            title: "3D Printing",
            image: PrintingImg
        }
    ];


    //? Functions


    //? Hooks


    //? What is gonna be rendered
    return (
        <>
        {/*//? Intro Section */}
        <div className='intro_section'>
            <div className='welcome_text'>
                {/*//*  Welcome Text */}
                <h2>
                    <SplitText
                        text={welcomeText}
                        className="text-2xl font-semibold text-center"
                        delay={100}
                        duration={0.6}
                        ease="power3.out"
                        splitType="words"
                        from={{ opacity: 0, y: 40 }}
                        to={{ opacity: 1, y: 0 }}
                        threshold={0.1}
                        rootMargin="-100px"
                        textAlign="center"
                    />
                </h2>
                <h1>
                    <span className="company_name">
                        <SplitText
                            text={companyName}
                            className="text-2xl font-semibold text-center"
                            delay={50}
                            duration={0.6}
                            ease="power3.out"
                            splitType="chars"
                            from={{ opacity: 0, y: 40 }}
                            to={{ opacity: 1, y: 0 }}
                            threshold={0.1}
                            rootMargin="-100px"
                            textAlign="center"
                        />
                    </span>
                </h1>
                <p>Cutting-Edge Solutions, Crafted to Perfection</p>
            </div>
            
            {/*//* Card Display - Desktop only */}
            <div className="card_display_container">
                <CardSwap
                    width={800}
                    height={400}
                    cardDistance={60}
                    verticalDistance={70}
                    delay={3000}
                    pauseOnHover={false}
                >
                    <Card>
                        <div className="card_title">
                            <h3>Plasma Cutting</h3>
                        </div>

                        <div className="card_photo">
                            <img src={plasmaCuttingImg} alt="Plasma Cutting" />
                        </div>
                    </Card>
                    
                    <Card>
                        <div className="card_title">
                            <h3>Laser Engraving</h3>
                        </div>
                        <div className="card_photo">
                            <div className="placeholder_image">
                                <img src={lasserEngravingImg} alt="Laser Engraving" />
                            </div>
                        </div>
                    </Card>
                    
                    <Card>
                        <div className="card_title">
                            <h3>3D Printing</h3>
                        </div>
                        <div className="card_photo">
                            <div className="placeholder_image">
                                <img src={PrintingImg} alt="3D Printing" />
                            </div>
                        </div>
                    </Card>
                </CardSwap>
            </div>

            {/*//* Card Display - Mobile & Tablet only */}
            <div className='carrusel_display_container' style={{ height: '800px', position: 'relative' }}>
                <Carousel
                    items={carouselItems}
                    baseWidth={400}
                    autoplay={true}
                    autoplayDelay={3000}
                    pauseOnHover={true}
                    loop={true}
                    round={false}
                />
            </div>
        </div>

        {/*//?  Info Section */}
        <div className='info_section'>
            <div className="info_divider">

            </div>
            
        </div>

        {/*//? AGAH Carnet */}
        <div className='agah_carnet_section'>
            

        </div>

        {/*//?  Featured Services Section */}
        <div className='featured_services_section'>


        </div>

        {/*//?  Contact Section */}
        <div className='short_contact_section'>


        </div>
        </>
    )
}

export default HomePage
