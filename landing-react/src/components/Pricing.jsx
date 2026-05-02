import { motion } from 'framer-motion'

const plans = [
  {
    label: 'Démarrage', name: 'Gratuit', price: '0€', period: '/mois',
    desc: 'Pour tester PlantAI et découvrir les fonctionnalités de base.',
    features: [
      { text: '5 analyses IA / jour',   ok: true  },
      { text: 'Détection 38 maladies',  ok: true  },
      { text: '1 caméra ESP32',         ok: true  },
      { text: 'Historique 7 jours',     ok: true  },
      { text: 'Export PDF',             ok: false },
      { text: 'Alertes critiques',      ok: false },
      { text: 'Support prioritaire',    ok: false },
    ],
    featured: false, btnLabel: 'Commencer gratis', btnStyle: 'outline',
  },
  {
    label: 'Plus populaire', name: 'Pro', price: '9€', period: '/mois',
    desc: 'Pour les passionnés et agriculteurs qui veulent le maximum.',
    features: [
      { text: 'Analyses illimitées',        ok: true  },
      { text: 'IA universelle (CLIP)',       ok: true  },
      { text: '5 caméras ESP32',            ok: true  },
      { text: 'Historique illimité',        ok: true  },
      { text: 'Export PDF professionnel',   ok: true  },
      { text: 'Alertes critiques temps réel', ok: true },
      { text: 'Support prioritaire',        ok: false },
    ],
    featured: true, btnLabel: 'Démarrer Pro →', btnStyle: 'main',
  },
  {
    label: 'Entreprise', name: 'Enterprise', price: '29€', period: '/mois',
    desc: 'Pour les exploitations agricoles et équipes techniques.',
    features: [
      { text: 'Tout le plan Pro',           ok: true },
      { text: 'Caméras illimitées',         ok: true },
      { text: 'API REST complète',          ok: true },
      { text: 'Dashboard multi-sites',      ok: true },
      { text: 'Modèle custom entraînable',  ok: true },
      { text: 'Rapport hebdomadaire auto',  ok: true },
      { text: 'Support prioritaire 24/7',   ok: true },
    ],
    featured: false, btnLabel: 'Contacter l\'équipe', btnStyle: 'outline',
  },
]

export default function Pricing() {
  return (
    <section id="pricing" className="py-24 px-[5%]">
      <div className="max-w-5xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-[#00e676]/10 border border-[#00e676]/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-[#00e676] mb-4">💳 Tarifs</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight mb-3">
            Simple, transparent,<br />sans surprise.
          </h2>
          <p className="text-slate-400 max-w-[440px] mx-auto text-base leading-7">
            Commencez gratuitement. Évoluez quand vous en avez besoin.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-14 items-start">
          {plans.map((p, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .6, delay: i * .15 }}
              whileHover={{ y: -6 }}
              className={`glass rounded-2xl p-8 relative overflow-hidden transition-all duration-300 text-left
                ${p.featured
                  ? 'border border-[#00e676]/40 shadow-[0_0_60px_rgba(0,230,118,.15),inset_0_0_40px_rgba(0,230,118,.03)]'
                  : 'border border-white/[.07]'}`}>

              {p.featured && (
                <div className="absolute top-5 right-[-32px] bg-gradient-to-r from-[#1db954] to-[#00c853]
                  text-white text-[.6rem] font-extrabold px-10 py-1 rotate-45 tracking-widest">
                  TOP
                </div>
              )}

              <div className="text-[.72rem] font-bold text-slate-500 uppercase tracking-widest mb-2">{p.label}</div>
              <div className="text-[1.35rem] font-black mb-1">{p.name}</div>
              <div className="text-[2.8rem] font-black leading-none my-4">
                {p.price}<span className="text-base text-slate-400 font-normal">{p.period}</span>
              </div>
              <p className="text-[.8rem] text-slate-400 mb-6 leading-[1.6]">{p.desc}</p>

              <ul className="flex flex-col gap-2.5 mb-8">
                {p.features.map((f, j) => (
                  <li key={j} className={`flex items-center gap-2.5 text-[.8rem] ${f.ok ? 'text-slate-300' : 'text-slate-600'}`}>
                    <span className={`font-extrabold ${f.ok ? 'text-[#00e676]' : 'text-slate-600'}`}>
                      {f.ok ? '✓' : '✗'}
                    </span>
                    {f.text}
                  </li>
                ))}
              </ul>

              <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: .97 }}
                className={`w-full py-3 rounded-xl text-[.88rem] font-bold transition-all duration-200 border-none cursor-pointer
                  ${p.btnStyle === 'main'
                    ? 'bg-gradient-to-r from-[#1db954] to-[#00c853] text-white shadow-[0_0_30px_rgba(29,185,84,.4)] hover:shadow-[0_0_50px_rgba(29,185,84,.6)]'
                    : 'bg-white/[.05] border border-white/[.08] text-slate-300 hover:border-[#00e676]/40 hover:text-[#00e676]'}`}>
                {p.btnLabel}
              </motion.button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
