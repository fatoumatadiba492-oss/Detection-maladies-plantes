import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const faqs = [
  { q: "L'IA peut-elle détecter des maladies sur n'importe quelle plante ?", a: "Oui ! Notre pipeline en 2 étapes couvre 14 espèces avec le modèle ViT PlantVillage. Pour toutes les autres plantes, notre moteur CLIP zero-shot analyse les symptômes visuels (oïdium, rouille, taches, chlorose…) et donne un diagnostic même sur des espèces jamais vues." },
  { q: "Quel matériel ESP32 est compatible ?",                               a: "Le module AI Thinker ESP32-CAM est recommandé (~5-8€). Flashez-le avec notre firmware Arduino fourni dans le projet. Arduino IDE 2 + 5 minutes suffisent pour la configuration complète." },
  { q: "Combien de temps prend une analyse ?",                               a: "La capture ESP32 + analyse IA complète prend moins de 3 secondes sur réseau local. Le modèle HuggingFace est mis en cache dès le premier démarrage, les analyses suivantes sont quasi-instantanées." },
  { q: "Les données restent-elles sur mon réseau local ?",                   a: "Oui. PlantAI tourne entièrement en local. Le backend Flask, la caméra ESP32 et votre navigateur communiquent uniquement sur votre réseau WiFi. Aucune image n'est envoyée vers un serveur externe." },
  { q: "Peut-on entraîner le modèle sur nos propres données ?",             a: "Absolument. Le script train_model.py fourni entraîne EfficientNet-B4 sur votre propre dataset ImageFolder. Une fois entraîné, PlantAI l'utilise automatiquement comme modèle principal." },
  { q: "Y a-t-il une application mobile ?",                                  a: "L'application est entièrement responsive et fonctionne parfaitement sur mobile. Une app native iOS/Android est prévue dans la roadmap v4." },
]

export default function FAQ() {
  const [open, setOpen] = useState(null)
  return (
    <section id="faq" className="py-24 px-[5%] bg-[#050b12]/50">
      <div className="max-w-5xl mx-auto text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: .6 }}>
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/25
            rounded-full px-4 py-1.5 text-[.72rem] font-bold text-blue-400 mb-4">❓ FAQ</div>
          <h2 className="text-[clamp(1.8rem,3.5vw,2.8rem)] font-black leading-tight mb-4">Questions fréquentes.</h2>
        </motion.div>

        <div className="flex flex-col gap-3 mt-12 max-w-[760px] mx-auto text-left">
          {faqs.map((f, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ duration: .5, delay: i * .07 }}
              className={`glass border rounded-2xl overflow-hidden transition-colors duration-300
                ${open === i ? 'border-[#00e676]/30' : 'border-white/[.07]'}`}>
              <button onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between gap-4 px-6 py-5 text-left
                  text-[.88rem] font-semibold bg-transparent border-none cursor-pointer
                  text-slate-200 hover:text-[#00e676] transition-colors duration-200">
                {f.q}
                <motion.span animate={{ rotate: open === i ? 180 : 0 }} transition={{ duration: .3 }}
                  className="w-6 h-6 rounded-full bg-[#00e676]/10 border border-[#00e676]/20 flex-shrink-0
                    flex items-center justify-center text-[.7rem] text-[#00e676]">
                  ▼
                </motion.span>
              </button>
              <AnimatePresence initial={false}>
                {open === i && (
                  <motion.div
                    key="content"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: .35, ease: 'easeInOut' }}
                    className="overflow-hidden">
                    <p className="px-6 pb-5 text-[.82rem] text-slate-400 leading-7">{f.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
