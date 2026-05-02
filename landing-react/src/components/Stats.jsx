import { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'

function Counter({ target, suffix = '' }) {
  const [val, setVal] = useState(0)
  const ref = useRef()
  const inView = useInView(ref, { once: true })
  useEffect(() => {
    if (!inView) return
    let start = null
    const dur = 1800
    const step = (now) => {
      if (!start) start = now
      const p = Math.min((now - start) / dur, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      setVal(Math.round(target * ease))
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [inView, target])
  return <span ref={ref}>{val.toLocaleString('fr')}{suffix}</span>
}

const stats = [
  { target: 38,   suffix: '',  label: 'Maladies détectées' },
  { target: 97,   suffix: '%', label: 'Précision IA' },
  { target: 2400, suffix: '+', label: 'Plantes surveillées' },
  { target: 3,    suffix: 's', label: 'Temps d\'analyse' },
]

export default function Stats() {
  return (
    <div className="relative z-10 border-y border-white/[.05] bg-[#050b12]/60 backdrop-blur-md py-10">
      <div className="max-w-5xl mx-auto px-[5%] grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((s, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }} transition={{ duration: .6, delay: i * .1 }}
            className="text-center">
            <div className="text-[2rem] font-black text-gradient">
              <Counter target={s.target} suffix={s.suffix} />
            </div>
            <div className="text-[.75rem] text-slate-500 mt-1">{s.label}</div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
