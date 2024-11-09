// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    "@nuxtjs/tailwindcss",
    "@vueuse/nuxt",
    "@nuxt/image",
    "@nuxtjs/plausible"
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
    apiHost: "https://analytics.artexplorer.ai",
    // Enable tracking of outbound links. In our case links to the Rijksmuseum and Github
    autoOutboundTracking: true
  },
});
