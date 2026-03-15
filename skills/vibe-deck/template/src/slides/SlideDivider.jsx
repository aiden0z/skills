import { motion } from 'framer-motion'
import { colors } from '../theme'
import { stagger, fadeIn } from '../lib/animations'

export default function SlideDivider({ number, title, subtitle }) {
  return (
    <motion.div
      className="flex items-center h-full px-24"
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      {/* 左侧编号 */}
      {number && (
        <motion.div className="shrink-0 mr-12" variants={fadeIn}>
          <span
            className="text-[96px] font-extrabold leading-none"
            style={{ color: colors.primary }}
          >
            {number}
          </span>
        </motion.div>
      )}

      {/* 右侧内容 */}
      <motion.div variants={fadeIn}>
        <div className="w-12 h-[3px] rounded-full mb-5" style={{ background: `linear-gradient(to right, ${colors.primary}, ${colors.primaryLight})` }} />
        <h2 className="text-[40px] font-bold tracking-tight leading-tight" style={{ color: colors.text }}>
          {title}
        </h2>
        {subtitle && (
          <p className="text-[17px] mt-3 leading-relaxed" style={{ color: colors.textSecondary }}>
            {subtitle}
          </p>
        )}
      </motion.div>
    </motion.div>
  )
}
