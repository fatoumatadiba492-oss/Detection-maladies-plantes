import BgCanvas     from './components/BgCanvas'
import Navbar       from './components/Navbar'
import Hero         from './components/Hero'
import Stats        from './components/Stats'
import Problem      from './components/Problem'
import Solution     from './components/Solution'
import Features     from './components/Features'
import HowItWorks   from './components/HowItWorks'
import Testimonials from './components/Testimonials'
import Pricing      from './components/Pricing'
import FAQ          from './components/FAQ'
import CTA          from './components/CTA'
import Footer       from './components/Footer'

export default function App() {
  return (
    <div className="relative min-h-screen bg-[#050b12] text-slate-100 overflow-x-hidden">
      <BgCanvas />
      <div className="relative z-10">
        <Navbar />
        <Hero />
        <Stats />
        <Problem />
        <Solution />
        <Features />
        <HowItWorks />
        <Testimonials />
        <Pricing />
        <FAQ />
        <CTA />
        <Footer />
      </div>
    </div>
  )
}
