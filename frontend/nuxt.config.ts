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

  app: {
    head: {
      script: [
        { src: "https://cdn.otusanalytics.com/otusanalytics/otus.js", async: true },
        {
          innerHTML: `window.otus=window.otus||function(){(otus.q=otus.q||[]).push(arguments)},otus.init=otus.init||function(i){otus.o=i||{}};
  otus.init({ siteId: 4, endpoint: "https://ingest.otusanalytics.com/e" })`,
        },
      ],
    },
  },

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