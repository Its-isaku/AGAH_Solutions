//?frontend/src/components/homepage/HeroSection.jsx

//?  <|----------------------Imports----------------------|>

//* css 
import '../../style/HeroSection.css'

//* Components 
import SplitText from "../../components/common/SplitText";
import CardSwap, { Card } from '../../components/common/CardSwap'
import Carousel from '../../components/common/Carousel'

//* Images
import plasmaCuttingImg from '../../img/plasma_cutting.jpg'
import lasserEngravingImg from '../../img/laser_engravingpng.png'
import FillPrinting from '../../img/3D_printing.jpg'

//!  <|------------------Component------------------|> 
function HeroSection({heroData}) {

    //? <|------------------Variables------------------|> 
    const welcomeText = heroData?.welcomeText || "Welcome to";
        // const welcomeText = "Bienvenidos a";
    const companyName = heroData?.companyName || "AGAH Solutions";
    const tagline = heroData?.description || "Cutting-Edge Solutions, Crafted to Perfection";
    // const tagline = heroData?.description || "Soluciones Elaboradas a la Perfección";

    //? Services data (for carousel - Dynamic)
    const getServicesData = () => {
        //* if we have data from the API we use them, if not we use the defaults
        if (heroData?.featuredServices && heroData?.featuredServices.length > 0) {
            return heroData.featuredServices.map(service => ({
                id: service.id,
                title: service.name,
                image: getServiceImage(service)
            }));
        }

        return [
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
                image: FillPrinting
            }
        ];
    };

    //? Get Service image
    const getServiceImage = (service) => {
        //* try API images first
        if (service.image_url) {
            return service.image_url;
        } 

        //* Fallback to local images based on service types
        const localImageMap = {
            'plasma_cutting': plasmaCuttingImg,
            'laser_engraving': lasserEngravingImg,
            '3d_printing': FillPrinting,
        }

        return localImageMap[service.service_type] || plasmaCuttingImg; 
    }

    //? Get services for carousel and cards
    const serviceData = getServicesData();

    //? Carousel items
    const carouselItems = serviceData.map(service => ({
        id: service.id,
        title: service.title,
        image: service.image
    }));

    //? <|------------------Functions------------------|>
    

    //? <|------------------Hooks------------------|>


    //? <|------------------Render------------------|>
    return (
        <>
        {/*//? Hero Section */}
        <div className='hero-section'>
            <div className='hero-welcome-text'>
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
                    <span className="hero-company-name">
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
                <p className="hero-tagline">{tagline}</p>
            </div>
            
            {/*//* Card Display - Desktop only */}
            <div className="hero-cards-container">
                {/* Temporalmente comentado para probar MagicBento */}
                <CardSwap
                    width={800}
                    height={400}
                    cardDistance={60}
                    verticalDistance={70}
                    delay={3000}
                    pauseOnHover={false}
                >
                    {serviceData.map((service, index) => (
                        <Card key={service.id}>
                            <div className="hero-card-title">
                                <h3>{service.title}</h3>
                            </div>
                            <div className="hero-card-photo">
                                <img 
                                    src={service.image} 
                                    alt={service.title}
                                    onError={(e) => {
                                        console.warn(`Failed to load image for ${service.title}:`, e.target.src);
                                    }}
                                />
                            </div>
                        </Card>
                    ))}
                </CardSwap>
            </div>

            {/*//* Card Display - Mobile & Tablet only */}
            <div className='hero-carousel-container' style={{ height: '800px', position: 'relative' }}>
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
        </>
    )
}

export default HeroSection