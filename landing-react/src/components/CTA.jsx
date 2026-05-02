import { useState } from 'react'
import { motion } from 'framer-motion'

export default function CTA() {
  const [email, setEmail] = useState('')
  const [done,  setDone]  = useState(false)
  const [error, setError] = useState(false)

  const submit = () => {
    if (!email || !email.includes('@')) { setError(true); setTimeout(() => setError(false), 2500); return }
    setDone(true); setEmail('')
  }

  return (
    <section className="py-24 px-[5%] relative overflow-hidden">
      {/* Radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_50%,rgba(0,230,118,.07),transparent_70%)] pointer-events-none" />

      <div className="max-w-5xl mx-auto text-center relative">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-[#00e676]/10 border border-[#00e676]/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-[#00e676] mb-6">🚀 Commencer maintenant</div>

          <h2 className="text-[clamp(2rem,4vw,3.2rem)] font-black leading-tight mb-4">
            Tes plantes méritent<br />
            <span className="text-gradient">une intelligence artificielle.</span>
          </h2>
          <p className="text-slate-400 text-base max-w-[440px] mx-auto mb-10 leading-7">
            Rejoins les 2 400 utilisateurs qui surveillent leurs plantes en temps réel.
          </p>

          <motion.div className={`flex gap-2 max-w-[480px] mx-auto rounded-2xl p-1.5 pl-5 mb-3 transition-all duration-300
            glass border ${error ? 'border-red-500/60' : 'border-white/[.07] focus-within:border-[#00e676]/50'}`}>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && submit()}
              placeholder={error ? 'Email invalide !' : 'ton@email.com'}
              className="flex-1 bg-transparent border-none outline-none text-[.88rem] text-slate-200
                placeholder:text-slate-500 font-normal" />
            <motion.button onClick={submit} whileHover={{ scale: 1.04 }} whileTap={{ scale: .97 }}
              className={`px-6 py-3 rounded-xl text-[.85rem] font-bold border-none cursor-pointer transition-all duration-300
                ${done
                  ? 'bg-gradient-to-r from-[#16a34a] to-[#15803d] text-white'
                  : 'bg-gradient-to-r from-[#1db954] to-[#00c853] text-white shadow-[0_0_20px_rgba(29,185,84,.3)] hover:shadow-[0_0_35px_rgba(29,185,84,.5)]'}`}>
              {done ? '✅ Inscrit !' : 'Démarrer gratis →'}
            </motion.button>
          </motion.div>
          <p className="text-[.72rem] text-slate-600">Gratuit pour toujours · Aucune carte bancaire · Installation en 5 min</p>
        </motion.div>
      </div>
    </section>
  )
}
