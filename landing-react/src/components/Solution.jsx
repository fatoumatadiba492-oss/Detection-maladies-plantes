import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

function DashboardMock() {
  const chartRef = useRef()
  useEffect(() => {
    const bars = chartRef.current?.querySelectorAll('.dash-bar')
    const interval = setInterval(() => {
      if (!bars) return
      const idx = Math.floor(Math.random() * bars.length)
      bars[idx].style.height = Math.round(Math.random() * 60 + 30) + '%'
    }, 700)
    return () => clearInterval(interval)
  }, [])
  const kpis = [
    { label: 'Température',  val: '24.3°C', color: '#f59e0b', sub: '↑ Optimal' },
    { label: 'Humidité sol', val: '68%',    color: '#3b82f6', sub: '↑ Normal'  },
    { label: 'Diagnostic IA',val: 'Saine ✅',color: '#1db954', sub: 'Conf. 97%' },
    { label: 'Luminosité',   val: '74%',    color: '#eab308', sub: '↓ Légère'  },
  ]
  const bars = [65,40,72,55,88,45,92,68,35,78,60,85]
  const bColors = ['#1db954','#3b82f6','#1db954','#3b82f6','#1db954','#f59e0b','#1db954','#3b82f6','#f59e0b','#1db954','#3b82f6','#1db954']
  return (
    <div className="rounded-2xl overflow-hidden glass border border-white/[.07] shadow-[0_24px_80px_rgba(0,0,0,.5),0_0_40px_rgba(0,230,118,.12)]">
      <div className="bg-[#050b12]/90 px-5 py-3.5 flex items-center gap-2 border-b border-white/[.06]">
        {['#ef4444','#f59e0b','#1db954'].map((c,i) => <div key={i} className="w-2.5 h-2.5 rounded-full" style={{background:c}}/>)}
        <span className="text-[.7rem] text-slate-500 ml-2">PlantAI — Dashboard</span>
      </div>
      <div className="p-5">
        <div className="grid grid-cols-2 gap-3 mb-4">
          {kpis.map((k,i) => (
            <div key={i} className="bg-[#050b12]/70 border border-white/[.06] rounded-xl p-3.5">
              <div className="text-[.58rem] text-slate-500 uppercase tracking-widest mb-1.5">{k.label}</div>
              <div className="font-extrabold text-[1.25rem]" style={{color:k.color}}>{k.val}</div>
              <div className="text-[.58rem] text-emerald-400 mt-1">{k.sub}</div>
            </div>
          ))}
        </div>
        <div ref={chartRef} className="flex items-end gap-1.5 bg-[#050b12]/50 rounded-xl p-3" style={{height:'80px'}}>
          {bars.map((h,i) => (
            <div key={i} className="dash-bar flex-1 rounded-t-sm transition-all duration-500"
              style={{height:`${h}%`,background:bColors[i],opacity:.7}} />
          ))}
        </div>
      </div>
    </div>
  )
}

const items = [
  { icon: '🧠', title: 'IA universelle — toute plante',   desc: 'Pipeline double ViT + CLIP zero-shot détecte les maladies sur n\'importe quelle espèce végétale.' },
  { icon: '📷', title: 'ESP32-CAM intégrée',              desc: 'Capturez en un clic. Le diagnostic arrive en moins de 3 secondes avec conseil personnalisé.' },
  { icon: '📊', title: 'Historique & statistiques',       desc: 'Suivi de la santé dans le temps. Export PDF complet pour vos rapports agronomiques.' },
  { icon: '🚨', title: 'Alertes critiques temps réel',    desc: 'En cas de maladie grave, alerte visuelle et sonore avec actions à prendre immédiatement.' },
]

export default function Solution() {
  return (
    <section id="solution" className="py-24 px-[5%]">
      <div className="max-w-5xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-[#00e676]/10 border border-[#00e676]/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-[#00e676] mb-4">✨ La solution</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight mb-4">
            Un dashboard intelligent<br />connecté à tes plantes.
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 mt-14 items-center">
          <motion.div initial={{ opacity: 0, scale: .92 }} whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }} transition={{ duration: .7, ease: [.22,1,.36,1] }}>
            <DashboardMock />
          </motion.div>

          <div className="flex flex-col gap-6">
            {items.map((it, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: 40 }} whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }} transition={{ duration: .6, delay: i * .12 }}
                className="flex gap-4">
                <div className="w-11 h-11 rounded-xl bg-[#00e676]/10 border border-[#00e676]/20
                  flex items-center justify-center text-xl flex-shrink-0 shadow-[0_0_20px_rgba(0,230,118,.12)]">
                  {it.icon}
                </div>
                <div>
                  <div className="font-bold text-[.95rem] mb-1.5">{it.title}</div>
                  <div className="text-[.8rem] text-slate-400 leading-[1.65]">{it.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
