import { motion } from 'framer-motion'
import { stagger, fadeIn } from '../lib/animations'
import KeyMessage from './KeyMessage'

/**
 * SlideLayout — enforces the canonical Title → KeyMessage → Content order.
 *
 * Props:
 *   title       (string, required) — slide heading
 *   subtitle    (string)           — lighter text after the title
 *   keyMessage  (ReactNode)        — bullet content inside KeyMessage; omit to skip
 *   keyLabel    (string)           — override KeyMessage label (default "Key Message")
 *   children    (ReactNode)        — main content area, fills remaining space
 *   className   (string)           — extra classes on root
 */
export default function SlideLayout({
  title,
  subtitle,
  keyMessage,
  keyLabel,
  children,
  className = '',
}) {
  return (
    <motion.div
      className={`flex flex-col h-full gap-3 ${className}`}
      variants={stagger}
      initial="hidden"
      animate="show"
    >
      {/* ── Title (always first) ── */}
      <motion.div variants={fadeIn}>
        <h2 className="text-[28px] font-bold text-neutral-800 tracking-tight">
          {title}
          {subtitle && (
            <span className="text-sm font-normal text-neutral-400 ml-3">
              {subtitle}
            </span>
          )}
        </h2>
      </motion.div>

      {/* ── KeyMessage (always second when present) ── */}
      {keyMessage && (
        <motion.div variants={fadeIn}>
          <KeyMessage {...(keyLabel ? { label: keyLabel } : {})}>
            {keyMessage}
          </KeyMessage>
        </motion.div>
      )}

      {/* ── Content (always last, fills remaining space) ── */}
      <motion.div variants={fadeIn} className="flex-1 min-h-0">
        {children}
      </motion.div>
    </motion.div>
  )
}
