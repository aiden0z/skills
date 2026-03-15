import { motion } from 'framer-motion'
import { colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideAgenda({ title = 'Agenda', items = [] }) {
  return (
    <motion.div
      className="flex flex-col h-full"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={fadeIn} className="mb-8">
        <h2 className="text-[28px] font-bold tracking-tight" style={{ color: colors.text }}>
          {title}
        </h2>
      </motion.div>

      <motion.div className="flex flex-col gap-2 flex-1 justify-center pl-16" variants={stagger}>
        {items.map((item, i) => {
          const num = item.number || String(i + 1).padStart(2, '0')
          const isActive = !!item.active
          return (
            <motion.div
              key={i}
              className="flex items-center gap-6 py-4"
              variants={fadeIn}
            >
              <span
                className="text-[24px] font-bold font-mono w-10 shrink-0"
                style={{ color: isActive ? colors.primary : `${colors.muted}40` }}
              >
                {num}
              </span>
              <span
                className="text-[20px] tracking-tight"
                style={{
                  color: isActive ? colors.text : colors.muted,
                  fontWeight: isActive ? 600 : 400,
                }}
              >
                {item.title}
              </span>
            </motion.div>
          )
        })}
      </motion.div>
    </motion.div>
  )
}
