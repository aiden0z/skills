export const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05 } },
}
export const staggerSlow = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
}
export const fadeIn = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
}
export const slideUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] } },
}
export const fadeOnly = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.4 } },
}
