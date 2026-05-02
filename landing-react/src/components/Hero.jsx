import { motion } from 'framer-motion'

const fadeUp = (delay = 0) => ({
  initial:    { opacity: 0, y: 40 },
  animate:    { opacity: 1, y: 0  },
  transition: { duration: .75, ease: [.22,1,.36,1], delay },
})

const dataCards = [
  { pos: 'top-[-20px] right-[-30px]',  label: 'Température',  value: '24.3°C', color: '#f59e0b', trend: '↑ Optimal', delay: '.5s'  },
  { pos: 'right-[-88px] top-[45%]',    label: 'Humidité sol', value: '68%',    color: '#00e676', trend: '↑ Bon',     delay: '1s'   },
  { pos: 'bottom-[-20px] left-[-24px]',label: 'Diagnostic IA',value: '✅ Saine',color: '#00e676', trend: 'Conf. 97%', delay: '1.5s' },
  { pos: 'left-[-88px] top-[30%]',     label: 'Luminosité',   value: '74%',    color: '#eab308', trend: '↓ Légère', delay: '.8s'  },
]

function FloatCard({ pos, label, value, color, trend, delay }) {
  return (
    <div className={`absolute ${pos} glass border border-[#00e676]/20 rounded-xl px-3.5 py-2.5 text-xs whitespace-nowrap
      shadow-[0_8px_32px_rgba(0,0,0,.45)]`}
      style={{ animation: `float 3.5s ease-in-out ${delay} infinite` }}>
      <div className="text-slate-500 uppercase tracking-widest text-[.58rem] mb-1">{label}</div>
      <div className="font-extrabold text-[.92rem]" style={{ color }}>{value}</div>
      <div className="text-[.58rem] mt-0.5 text-emerald-400">{trend}</div>
    </div>
  )
}

export default function Hero() {
  return (
    <section id="hero" className="min-h-screen flex items-center justify-center px-[5%] pt-[120px] pb-20 relative">
      <div className="max-w-6xl w-full mx-auto grid grid-cols-1 md:grid-cols-2 gap-16 items-center">

        {/* Left */}
        <div>
          <motion.div {...fadeUp(0)}
            className="inline-flex items-center gap-2 bg-[#00e676]/10 border border-[#00e676]/30
              rounded-full px-4 py-1.5 text-[.72rem] font-bold text-[#00e676] mb-6">
            <span className="w-1.5 h-1.5 bg-[#00e676] rounded-full pulse-anim" />
            Nouveau — IA universelle v3.0
          </motion.div>

          <motion.h1 {...fadeUp(.1)}
            className="text-[clamp(2.4rem,5vw,4rem)] font-black leading-[1.08] mb-5">
            Surveille tes plantes<br />
            <span className="text-gradient">en temps réel.</span>
          </motion.h1>

          <motion.p {...fadeUp(.2)} className="text-[1.05rem] text-slate-400 leading-7 mb-9 max-w-[500px]">
            PlantAI combine ESP32-CAM, intelligence artificielle et capteurs IoT pour diagnostiquer
            instantanément n'importe quelle maladie végétale — sur <strong className="text-slate-200">n'importe quelle plante</strong>.
          </motion.p>

          <motion.div {...fadeUp(.3)} className="flex flex-wrap gap-3.5 mb-8">
            <motion.a href="index.html"
              whileHover={{ scale: 1.04, y: -3 }} whileTap={{ scale: .97 }}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl text-[.92rem] font-bold
                bg-gradient-to-r from-[#1db954] to-[#00c853] text-white no-underline
                shadow-[0_0_30px_rgba(29,185,84,.4)] hover:shadow-[0_0_50px_rgba(29,185,84,.6)] transition-shadow duration-300">
              🚀 Démarrer gratuitement
            </motion.a>
            <motion.a href="#solution"
              whileHover={{ scale: 1.04, y: -3 }} whileTap={{ scale: .97 }}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl text-[.92rem] font-bold
                bg-white/[.05] border border-white/[.08] text-slate-200 no-underline
                hover:border-[#00e676]/40 hover:text-[#00e676] transition-all duration-200">
              ▶ Voir la démo
            </motion.a>
          </motion.div>

          <motion.div {...fadeUp(.4)} className="flex items-center gap-3 text-[.77rem] text-slate-500">
            <div className="flex">
              {['MK','SA','JD','AL'].map((i, idx) => (
                <div key={idx} className="w-7 h-7 rounded-full border-2 border-[#050b12] -ml-2 first:ml-0
                  bg-gradient-to-br from-[#1db954] to-[#3b82f6] flex items-center justify-center
                  text-[.55rem] font-bold text-white"
                  style={idx===1?{background:'linear-gradient(135deg,#3b82f6,#1d4ed8)'}:
                        idx===2?{background:'linear-gradient(135deg,#f59e0b,#d97706)'}:
                        idx===3?{background:'linear-gradient(135deg,#ec4899,#be185d)'}:{}}>{i}</div>
              ))}
            </div>
            <span className="text-[#f59e0b] tracking-widest">★★★★★</span>
            <span>+2 400 plantes surveillées</span>
          </motion.div>
        </div>

        {/* Right — 3D Device */}
        <motion.div {...fadeUp(.2)}
          className="flex items-center justify-center order-first md:order-last">
          <div className="relative w-[320px] h-[320px] md:w-[360px] md:h-[360px]">
            {/* Orbit rings */}
            <div className="absolute inset-0 rounded-full border border-[#00e676]/15 orbit-1" />
            <div className="absolute inset-[-32px] rounded-full border border-[#3b82f6]/10 orbit-2" />
            <div className="absolute inset-[-64px] rounded-full border border-[#a855f7]/07 orbit-3" />

            {/* Orbit dots */}
            {[
              'top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#00e676] shadow-[0_0_12px_#00e676] orbit-1',
              'top-[-30px] left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-400 shadow-[0_0_12px_#60a5fa] orbit-2',
            ].map((c,i) => <div key={i} className={`absolute w-2 h-2 rounded-full ${c}`} />)}

            {/* Core device */}
            <div className="absolute inset-10 rounded-3xl glass border border-[#00e676]/25
              flex flex-col items-center justify-center gap-2
              shadow-[0_0_60px_rgba(0,230,118,.15),inset_0_0_40px_rgba(0,230,118,.05)] float">
              <div className="text-[2.4rem]">📷</div>
              <div className="text-[.65rem] font-extrabold text-[#00e676] tracking-[3px] uppercase">ESP32-CAM</div>
              <div className="flex items-center gap-1.5 text-[.6rem] text-slate-500">
                <span className="w-1.5 h-1.5 bg-[#00e676] rounded-full pulse-anim" />
                Opérationnelle
              </div>
            </div>

            {/* Floating data cards */}
            {dataCards.map((c, i) => <FloatCard key={i} {...c} />)}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
