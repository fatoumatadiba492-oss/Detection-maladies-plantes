import { motion } from 'framer-motion'

const cols = [
  { title: 'Produit', links: [{ l: 'Solution', h: '#solution' }, { l: 'Fonctionnalités', h: '#features' }, { l: 'Tarifs', h: '#pricing' }, { l: 'Ouvrir l\'app', h: 'index.html' }] },
  { title: 'Ressources', links: [{ l: 'Documentation', h: '#' }, { l: 'Guide ESP32', h: '#' }, { l: 'API Reference', h: '#' }, { l: 'FAQ', h: '#faq' }] },
  { title: 'Projet', links: [{ l: 'À propos', h: '#' }, { l: 'GitHub', h: '#' }, { l: 'Contact', h: '#' }, { l: 'Projet Tutoré 2026', h: '#' }] },
]

export default function Footer() {
  return (
    <footer className="border-t border-white/[.05] px-[5%] pt-16 pb-8">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-[9px] bg-gradient-to-br from-[#1db954] to-[#0d6e2e]
                flex items-center justify-center text-base shadow-[0_0_16px_rgba(29,185,84,.35)]">🌿</div>
              <span className="font-extrabold text-[.85rem] tracking-widest uppercase">PlantAI</span>
            </div>
            <p className="text-[.78rem] text-slate-500 leading-7 max-w-[220px]">
              Plateforme intelligente de monitoring et diagnostic des maladies végétales propulsée par IA et IoT.
            </p>
          </div>
          {cols.map((c, i) => (
            <div key={i}>
              <div className="text-[.72rem] font-extrabold text-slate-300 uppercase tracking-[2px] mb-4">{c.title}</div>
              <div className="flex flex-col gap-2.5">
                {c.links.map((l, j) => (
                  <motion.a key={j} href={l.h} whileHover={{ x: 4, color: '#00e676' }}
                    className="text-[.78rem] text-slate-500 no-underline transition-colors duration-200">
                    {l.l}
                  </motion.a>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-white/[.05] pt-6 flex flex-wrap justify-between items-center gap-4
          text-[.72rem] text-slate-600">
          <span>© 2026 PlantAI — Projet Tutoré · Tous droits réservés</span>
          <div className="flex gap-2">
            {['🐙','🐦','💼'].map((s, i) => (
              <motion.a key={i} href="#" whileHover={{ scale: 1.15, borderColor: '#00e676' }}
                className="w-8 h-8 rounded-lg bg-white/[.04] border border-white/[.07]
                  flex items-center justify-center text-[.82rem] no-underline transition-colors duration-200">
                {s}
              </motion.a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
