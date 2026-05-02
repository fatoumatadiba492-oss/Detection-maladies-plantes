import { motion } from 'framer-motion'

const feats = [
  { icon:'🔬', title:'38 maladies détectées',     desc:'Modèle ViT entraîné sur 87 000 images PlantVillage. Tavelure, mildiou, oïdium, rouille, virus…',  tag:'IA PlantVillage',    color:'#00e676' },
  { icon:'🌍', title:'Toute plante reconnue',      desc:'CLIP zero-shot (OpenAI) analyse les symptômes visuels sur rose, basilic, aloe vera, orchidée…',   tag:'CLIP Universel',     color:'#60a5fa' },
  { icon:'📡', title:'Capteurs IoT en live',       desc:'Température, humidité air & sol, luminosité — données mises à jour toutes les 2,5 secondes.',     tag:'ESP32 IoT',          color:'#a855f7' },
  { icon:'💊', title:'Traitements précis',          desc:'Description scientifique, traitement recommandé et conseils agronomiques pour chaque maladie.',   tag:'Expert botanique',   color:'#f59e0b' },
  { icon:'📄', title:'Export PDF professionnel',   desc:'Rapport complet : historique, statistiques, capteurs, diagnostics — en un seul clic.',              tag:'Rapport automatique', color:'#ec4899' },
  { icon:'🎯', title:'Top-5 prédictions',           desc:'Visualisez les 5 maladies les plus probables avec score de confiance — décision éclairée.',        tag:'Transparence IA',    color:'#06b6d4' },
]

export default function Features() {
  return (
    <section id="features" className="py-24 px-[5%] bg-[#050b12]/50">
      <div className="max-w-5xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }} className="mb-14">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-blue-400 mb-4">⚡ Fonctionnalités</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight">
            Tout ce qu'il faut pour<br />surveiller tes plantes.
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {feats.map((f, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .6, delay: (i % 3) * .12 }}
              whileHover={{ y: -8, borderColor: `${f.color}35`,
                boxShadow: `0 20px 60px rgba(0,0,0,.4), 0 0 40px ${f.color}18` }}
              className="glass border border-white/[.07] rounded-2xl p-8 transition-all duration-350 cursor-default relative overflow-hidden group">
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                style={{background:`radial-gradient(circle at 50% 0%, ${f.color}10, transparent 60%)`}} />
              <div className="w-[52px] h-[52px] rounded-[14px] flex items-center justify-center text-2xl mb-5 relative"
                style={{background:`${f.color}18`, border:`1.5px solid ${f.color}30`,
                  boxShadow:`0 0 20px ${f.color}20`}}>
                {f.icon}
              </div>
              <h3 className="text-[1rem] font-extrabold mb-2.5">{f.title}</h3>
              <p className="text-[.8rem] text-slate-400 leading-[1.65] mb-4">{f.desc}</p>
              <span className="inline-flex px-2.5 py-1 rounded-full text-[.65rem] font-bold"
                style={{background:`${f.color}18`, color:f.color, border:`1px solid ${f.color}28`}}>
                {f.tag}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
