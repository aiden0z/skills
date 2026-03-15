import { motion } from 'framer-motion'
import { config, colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideThankYou({
  title = 'Thank You',
  subtitle = 'Questions & Discussion',
  contact,
}) {
  const p = config.presenter || {}
  const c = contact || {}
  const hasContact = c.email || c.phone || c.wechat || p.name

  return (
    <motion.div
      className="flex flex-col items-center justify-center h-full"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      <motion.div className="flex flex-col items-center text-center" variants={fadeIn}>
        <h1 className="text-[52px] font-extrabold tracking-tight" style={{ color: colors.text }}>
          {title}
        </h1>
        {subtitle && (
          <p className="text-[20px] font-light mt-3" style={{ color: colors.textSecondary }}>
            {subtitle}
          </p>
        )}
      </motion.div>

      {hasContact && (
        <motion.div className="mt-12 flex items-center gap-6 text-[13px]" style={{ color: colors.muted }} variants={fadeIn}>
          {(c.email || c.phone || c.wechat) ? (
            <>
              {c.email && <span>{c.email}</span>}
              {c.phone && <span>{c.phone}</span>}
              {c.wechat && <span>WeChat: {c.wechat}</span>}
            </>
          ) : (
            <>
              {p.name && <span className="font-semibold" style={{ color: colors.textSecondary }}>{p.name}</span>}
              {p.role && (
                <>
                  <div className="h-3 w-[1px]" style={{ backgroundColor: `${colors.muted}40` }} />
                  <span>{p.role}</span>
                </>
              )}
            </>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}
