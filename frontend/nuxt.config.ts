// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	devtools: { enabled: true },
	modules: ["@nuxtjs/tailwindcss", "@vueuse/nuxt", "@nuxt/image"],
	runtimeConfig: {
		public: {
			apiBase: "http://localhost:8000"
		}
	},
	vite: {
		build: {
			rollupOptions: {
				external: [
					"sharp"
				]
			}
		},
	}
});
