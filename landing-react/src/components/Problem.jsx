import { motion } from 'framer-motion'

const problems = [
  { icon: '🦠', title: 'Maladies invisibles à l\'œil nu',    desc: 'Les pathologies fongiques progressent 2-3 semaines avant d\'être visibles. À ce stade, 60% des plants sont déjà infectés.' },
  { icon: '⏰', title: 'Réaction toujours trop tardive',      desc: 'Sans monitoring continu, on réagit après les dégâts. Une infestation de mildiou peut détruire une culture entière en 48h.' },
  { icon: '💸', title: 'Traitements mal ciblés = pertes',     desc: 'Traiter sans diagnostic précis coûte cher. Les mauvais fongicides appliqués sur une maladie bactérienne n\'ont aucun effet.' },
]

export default function Problem() {
  return (
    <section id="problem" className="py-24 px-[5%]">
      <div className="max-w-5xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-blue-400 mb-4">🔍 Le problème</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight mb-4">
            Tes plantes meurent sans<br />que tu comprennes pourquoi.
          </h2>
          <p className="text-slate-400 text-base max-w-[480px] leading-7">
            Les maladies végétales se propagent silencieusement. Sans détection précoce, il est déjà trop tard.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-14">
          {problems.map((p, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .6, delay: i * .15 }}
              whileHover={{ y: -6, borderColor: 'rgba(239,68,68,.4)', boxShadow: '0 0 40px rgba(239,68,68,.1)' }}
              className="glass border border-white/[.07] rounded-2xl p-8 transition-colors duration-300 cursor-default">
              <div className="text-3xl mb-4">{p.icon}</div>
              <h3 className="text-[1rem] font-extrabold mb-3">{p.title}</h3>
              <p className="text-[.82rem] text-slate-400 leading-[1.7]">{p.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
