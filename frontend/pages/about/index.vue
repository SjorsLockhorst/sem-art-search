<template>
  <div class="p-4 min-h-screen">
    <h1 class="text-6xl mb-8 font-semibold">About this project</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-4">
      <div>
        <div class="mb-8">
          <h2 class="text-4xl font-medium">What is this project?</h2>
          <p class="text-2xl">
            A search engine that lets you search through artworks based on a 'vibe', aka the meaning or semantics of a
            text. You can try it out on the main page <NuxtLink to="/" class="underline text-blue-800">here.</NuxtLink>
          </p>
        </div>
        <div class="mb-8">
          <h2 class="text-4xl font-medium">How does this work?</h2>
          <p class="text-2xl">
            We actully wrote a blogpost detailing this! You can find it here: <a class="underline text-blue-800"
              href="https://blog.lockhorst.dev/projects/art-search" target="_blank">Blogpost</a>
          </p>
        </div>
        <div class="mb-8">
          <h2 class="text-4xl font-medium">Can I see the code?</h2>
          <p class="text-2xl">
            Yes, the whole project is open source! here you go:
            <a href="https://github.com/StefanVDWeide/modern-orange" target="_blank"
              class="underline text-blue-800">Github</a>
          </p>
        </div>
      </div>
      <div>
        <a href="https://www.rijksmuseum.nl/nl/collectie/object/Wiskundige--50173ce0e7a914f7a4a928c47cd46b42">
          <span class="italic text-2xl ">Wiskundige
            Jan Gillisz. van Vliet (vermeld op object), 1628 - 1637</span>
        </a>
        <div>
          <NuxtImg
            src="https://lh3.googleusercontent.com/uwQexn7HwJUVkuvHm4Z9n2Y-NraK3xXmLzUsuTIT4EmKabvJxVRS4x-mVx8Zs_Te-S9b6XtmOz7FfzgsFQavt1q3NhE=w0" />
        </div>
      </div>
    </div>
  </div>
</template>
