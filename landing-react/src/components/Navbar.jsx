import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const links = [
  { href: '#solution', label: 'Solution' },
  { href: '#features', label: 'Fonctionnalités' },
  { href: '#pricing',  label: 'Tarifs' },
  { href: '#faq',      label: 'FAQ' },
]

export default function Navbar() {
  const [scrolled,  setScrolled]  = useState(false)
  const [menuOpen,  setMenuOpen]  = useState(false)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: .6, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 h-[70px] flex items-center gap-8 px-[5%]
        border-b border-white/[0.06] transition-all duration-300
        ${scrolled ? 'bg-[#050b12]/95 backdrop-blur-2xl' : 'bg-[#050b12]/70 backdrop-blur-xl'}`}
    >
      {/* Logo */}
      <a href="#" className="flex items-center gap-2.5 no-underline group">
        <div className="w-9 h-9 rounded-[10px] bg-gradient-to-br from-[#1db954] to-[#0d6e2e]
          flex items-center justify-center text-lg shadow-[0_0_20px_rgba(29,185,84,.4)]
          group-hover:shadow-[0_0_35px_rgba(29,185,84,.6)] transition-all duration-300">
          🌿
        </div>
        <span className="font-extrabold text-[.9rem] tracking-widest text-slate-100 uppercase">PlantAI</span>
      </a>

      {/* Desktop links */}
      <div className="hidden md:flex gap-1 ml-auto">
        {links.map(l => (
          <motion.a key={l.href} href={l.href} whileHover={{ scale: 1.05 }}
            className="px-4 py-1.5 rounded-lg text-[.82rem] font-medium text-slate-400
              hover:text-[#00e676] hover:bg-[#00e676]/[.07] transition-all duration-200 no-underline">
            {l.label}
          </motion.a>
        ))}
      </div>

      <motion.a href="index.html" whileHover={{ scale: 1.04, y: -2 }} whileTap={{ scale: .97 }}
        className="hidden md:flex items-center gap-1.5 ml-4 px-5 py-2 rounded-[10px] text-[.82rem] font-bold
          bg-gradient-to-r from-[#1db954] to-[#00c853] text-white no-underline
          shadow-[0_0_24px_rgba(29,185,84,.4)] hover:shadow-[0_0_40px_rgba(29,185,84,.6)] transition-shadow duration-300">
        Ouvrir l'app →
      </motion.a>

      {/* Hamburger */}
      <button className="md:hidden ml-auto flex flex-col gap-[5px] p-1 bg-transparent border-none cursor-pointer"
        onClick={() => setMenuOpen(p => !p)}>
        {[0,1,2].map(i => (
          <motion.span key={i} className="block w-[22px] h-[2px] bg-slate-400 rounded-full"
            animate={menuOpen
              ? i === 0 ? { rotate: 45,  y: 7 }
              : i === 1 ? { opacity: 0 }
              : { rotate: -45, y: -7 }
              : { rotate: 0, y: 0, opacity: 1 }}
            transition={{ duration: .25 }} />
        ))}
      </button>

      {/* Mobile menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: .25 }}
            className="absolute top-[70px] left-0 right-0 glass border-b border-white/[.06]
              flex flex-col p-4 gap-2 md:hidden">
            {links.map(l => (
              <a key={l.href} href={l.href} onClick={() => setMenuOpen(false)}
                className="px-4 py-3 rounded-xl text-[.88rem] font-medium text-slate-300
                  hover:text-[#00e676] hover:bg-white/[.04] transition-all no-underline">
                {l.label}
              </a>
            ))}
            <a href="index.html"
              className="mt-2 text-center px-4 py-3 rounded-xl text-[.88rem] font-bold
                bg-gradient-to-r from-[#1db954] to-[#00c853] text-white no-underline">
              Ouvrir l'app →
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}
