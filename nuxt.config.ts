// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
<<<<<<< HEAD
  ssr: true
=======
  ssr: true,
  css: ['~/assets/css/tailwind.css'],
  postcss: {
    plugins: {
      '@tailwindcss/postcss': {}, // ← Tailwind v4 はこれ！
      autoprefixer: {},
    }}
>>>>>>> 8b98a6fd92b3aa1d9b1f9bf5941befe7cbb291b5
})
