// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  devtools: { enabled: true },

  modules: [
    "@nuxtjs/tailwindcss",
    "@vueuse/nuxt",
    "@nuxt/image",
    "@nuxtjs/plausible",
    "@nuxt/fonts"
  ],

  runtimeConfig: {
    public: {
      apiBase: "http://localhost:8000"
    }
  },

  plausible: {
    // Prevent tracking on localhost
    ignoredHostnames: ['localhost'],
    // Set our custom host
    apiHost: "https://plausible.lockhorst.dev",
    // Enable tracking of outbound links. In our case links to the Rijksmuseum and Github
    autoOutboundTracking: true
  },

  compatibilityDate: "2024-12-11",
});