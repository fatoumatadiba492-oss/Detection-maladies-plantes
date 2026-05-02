import { motion } from 'framer-motion'

const steps = [
  { icon: '🔌', num: '01', title: 'Connecte ton ESP32-CAM', desc: 'Flash le firmware PlantAI sur ta caméra. Elle démarre et affiche son IP — tu l\'entres dans l\'app en 10 secondes.' },
  { icon: '📷', num: '02', title: 'Pointe et capture',       desc: 'Dirige la caméra vers la feuille de ta plante. Un clic sur "Capturer & Analyser" — photo et analyse instantanées.' },
  { icon: '🧠', num: '03', title: 'Reçois le diagnostic IA', desc: 'En moins de 3 secondes, l\'IA identifie la maladie, son niveau de gravité et le traitement exact à appliquer.' },
]

export default function HowItWorks() {
  return (
    <section id="how" className="py-24 px-[5%]">
      <div className="max-w-5xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-[#00e676]/10 border border-[#00e676]/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-[#00e676] mb-4">📋 Comment ça marche</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight mb-4">Prêt en 3 étapes.</h2>
          <p className="text-slate-400 text-base max-w-[520px] mx-auto leading-7">
            De la configuration à l'analyse, tout est pensé pour être simple et instantané.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mt-16 relative">
          {/* Connecting line (desktop) */}
          <div className="hidden md:block absolute top-[36px] left-[calc(16.66%+20px)] right-[calc(16.66%+20px)] h-px
            bg-gradient-to-r from-transparent via-[#1db954] to-transparent" />

          {steps.map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .7, delay: i * .18 }}>
              <motion.div whileHover={{ scale: 1.08, boxShadow: '0 0 40px rgba(0,230,118,.3)' }}
                className="w-[72px] h-[72px] rounded-full mx-auto mb-5 flex items-center justify-center text-2xl
                  bg-[#00e676]/15 border-2 border-[#00e676]/30 shadow-[0_0_30px_rgba(0,230,118,.15)]
                  cursor-default transition-all duration-300 relative z-10">
                {s.icon}
              </motion.div>
              <div className="text-[.65rem] text-[#00e676] font-extrabold tracking-[3px] mb-2">{s.num}</div>
              <h3 className="text-[1rem] font-extrabold mb-2.5">{s.title}</h3>
              <p className="text-[.8rem] text-slate-400 leading-[1.65]">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
