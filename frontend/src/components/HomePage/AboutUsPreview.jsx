//?  Imports

//* Components
import GradientText from '../common/GradientText';
import SpotlightCard from '../common/Spotlights/SpotlightCard';
import { Link } from 'react-router-dom';


//?  Component 
function AboutUsPreview() {

    //? Variables                         //* Error state
    // const previewText = "AGAH Solutions nació del sueño de tres ingenieros mecatrónicos de la UABC, Aarón Almeraz, José García y Ángel Ahumada,  con la misión de ofrecer servicios de fabricación confiables, profesionales y con trato humano, en contraste con la falta de compromiso que veían en muchos proveedores. Con pasión y equipos modestos comenzaron a brindar soluciones en corte CNC por plasma, grabado láser, impresión 3D y producción de artículos técnicos y decorativos. Hoy buscan elevar el estándar local e industrial con tecnología, creatividad y responsabilidad, sembrando excelencia con integridad y fe para construir confianza en cada proyecto."
    const previewText = "AGAH Solutions was born from the dream of three mechatronics engineers from UABC, Aarón Almeraz, José García, and Ángel Ahumada, with the mission of offering reliable, professional, and human-centered manufacturing services, in contrast to the lack of commitment they observed in many providers. With passion and modest equipment, they began providing solutions in CNC plasma cutting, laser engraving, 3D printing, and the production of technical and decorative items. Today, they strive to raise the local and industrial standard through technology, creativity, and responsibility, sowing excellence with integrity and faith to build trust in every project."

    // const previewMission = "AGAH Solutions se sostiene sobre valores que nacen de nuestra fe y guían cada decisión y proyecto. Buscamos honrar a Dios en todo lo que hacemos, ofreciendo un trabajo hecho con excelencia, gratitud y compromiso. Practicamos la integridad al ser transparentes con nuestros precios, plazos y capacidades, cumpliendo lo que prometemos. Servimos con propósito, atendiendo a cada cliente con respeto y disposición, convencidos de que cada proyecto es una oportunidad para reflejar el carácter de Cristo. Administramos con responsabilidad nuestro tiempo, recursos y herramientas, practicando la mayordomía con visión de largo plazo y generosidad. Fomentamos la unidad y el amor fraternal en nuestras relaciones, colaborando con respeto, paciencia y espíritu de servicio. Finalmente, mantenemos nuestra fe y confianza en Dios, reconociendo que nuestra labor depende de Su bendición, y que cada paso lo damos con oración, confianza y esperanza."
    const previewMission = "AGAH Solutions is built on values rooted in our faith, guiding every decision and project we undertake. We strive to honor God in everything we do, delivering work with excellence, gratitude, and commitment. We practice integrity by being transparent with our prices, timelines, and technical capabilities, always fulfilling what we promise. We serve with purpose, treating each client with respect and dedication, convinced that every project is an opportunity to reflect the character of Christ. We manage our time, resources, and tools responsibly, practicing stewardship with a long-term vision and generosity. We foster unity and brotherly love in our relationships, collaborating with respect, patience, and a spirit of service. Finally, we place our faith and trust in God, recognizing that our work depends on His blessing, and that every step we take is guided by prayer, confidence, and hope."

    //? Functions

    //? Hooks

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
                        {/* Acerca de AGAH Solutions */}
                        About us Preview
                    </GradientText>
                </h2>
            </div>
            
            <div className='about_preview'>
                <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(0, 229, 255, 0.2)">
                    <div className="about_preview_Info">
                        <div className="text">
                            {/* <h2>Quienes somos</h2> */}
                            <h2>About us</h2>
                            <p>{previewText}</p>
                        </div>

                        <div className="text">
                            {/* <h2>Nuestra Misión</h2> */}
                            <h2>Our Mission</h2>
                            <p>{previewMission}</p>
                        </div>

                        <div className="previewBtn">
                            <Link to="/about" className="btn btn-primary">
                                Learn More
                            </Link>
                        </div>
                    </div>
                    
                    <div className="about_preview_img">

                    </div>
                </SpotlightCard>
            </div>
        </>
    )
}

export default AboutUsPreview;
