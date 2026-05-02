import { useEffect, useRef } from 'react'

export default function BgCanvas() {
  const ref = useRef()
  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    let W, H, animId, t = 0
    const orbs = [
      { x: .15, y: .2,  r: .4,  c: 'rgba(0,200,83,',   spd: .0003 },
      { x: .85, y: .15, r: .35, c: 'rgba(59,130,246,',  spd: .0004 },
      { x: .5,  y: .7,  r: .45, c: 'rgba(168,85,247,',  spd: .00025 },
      { x: .9,  y: .8,  r: .3,  c: 'rgba(0,200,83,',    spd: .0005 },
    ]
    const particles = Array.from({ length: 60 }, () => ({
      x: Math.random() * 2000, y: Math.random() * 1200,
      vx: (Math.random() - .5) * .3, vy: (Math.random() - .5) * .3,
      r: Math.random() * 1.5 + .5, a: Math.random() * .35 + .1,
      hue: 110 + Math.random() * 60,
    }))

    function resize() {
      W = canvas.width  = window.innerWidth
      H = canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    function draw() {
      animId = requestAnimationFrame(draw)
      t += .004
      ctx.clearRect(0, 0, W, H)

      const bg = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, W * .85)
      bg.addColorStop(0, 'rgba(7,14,24,1)')
      bg.addColorStop(1, 'rgba(5,11,18,1)')
      ctx.fillStyle = bg
      ctx.fillRect(0, 0, W, H)

      orbs.forEach((o, i) => {
        const cx = (o.x + Math.sin(t * o.spd * 1000 + i) * .08) * W
        const cy = (o.y + Math.cos(t * o.spd * 1200 + i) * .06) * H
        const r  = o.r * Math.min(W, H) * .9
        const g  = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
        g.addColorStop(0, o.c + '0.06)')
        g.addColorStop(1, o.c + '0)')
        ctx.fillStyle = g
        ctx.fillRect(0, 0, W, H)
      })

      ctx.save()
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `hsla(${p.hue},80%,60%,${p.a})`
        ctx.shadowColor = `hsla(${p.hue},80%,60%,.5)`
        ctx.shadowBlur  = 6
        ctx.fill()
      })
      ctx.restore()

      ctx.save()
      ctx.strokeStyle = 'rgba(0,230,118,0.025)'
      ctx.lineWidth = 1
      for (let x = 0; x < W; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke() }
      for (let y = 0; y < H; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke() }
      ctx.restore()
    }
    draw()
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize) }
  }, [])

  return <canvas ref={ref} className="fixed inset-0 z-0 pointer-events-none" />
}
