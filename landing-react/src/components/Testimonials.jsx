import { motion } from 'framer-motion'

const testis = [
  { stars: 5, text: '"PlantAI a sauvé ma serre entière. Le mildiou de la tomate a été détecté 10 jours avant que je voie quoi que ce soit. Le traitement a fonctionné parfaitement."', name: 'Mamadou Koné', role: 'Agriculteur, Sénégal', init: 'MK', grad: 'from-[#1db954] to-[#0d6e2e]' },
  { stars: 5, text: '"J\'ai soumis une photo de mon aloe vera malade et l\'IA a immédiatement détecté une chlorose ferrique avec le traitement à appliquer. Impressionnant !"', name: 'Sophie Andersen', role: 'Passionnée de botanique', init: 'SA', grad: 'from-[#3b82f6] to-[#1d4ed8]' },
  { stars: 5, text: '"L\'intégration ESP32 est bluffante. Flux live + capture + diagnostic en 3 secondes — exactement ce qu\'il fallait pour notre projet de serre connectée."', name: 'Julien Dupont', role: 'Étudiant agro-informatique', init: 'JD', grad: 'from-[#f59e0b] to-[#d97706]' },
]

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-24 px-[5%] bg-[#050b12]/50">
      <div className="max-w-5xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-blue-400 mb-4">💬 Ils nous font confiance</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight">
            Ce que disent nos utilisateurs.
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-14 text-left">
          {testis.map((t, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .6, delay: i * .15 }}
              whileHover={{ y: -6, borderColor: 'rgba(0,230,118,.25)', boxShadow: '0 16px 40px rgba(0,0,0,.3)' }}
              className="glass border border-white/[.07] rounded-2xl p-7 transition-all duration-300">
              <div className="text-[#f59e0b] tracking-[3px] text-base mb-3">{'★'.repeat(t.stars)}</div>
              <p className="text-[.83rem] text-slate-400 leading-7 italic mb-5">{t.text}</p>
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.grad} flex items-center justify-center text-[.72rem] font-extrabold text-white flex-shrink-0`}>
                  {t.init}
                </div>
                <div>
                  <div className="text-[.82rem] font-bold">{t.name}</div>
                  <div className="text-[.7rem] text-slate-500">{t.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
