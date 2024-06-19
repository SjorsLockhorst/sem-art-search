<template>
  <div class="p-4 h-screen">
    <button @click="clearPixiCache">destroy</button>
    <div>
      <h1 class="text-4xl font-bold">
        <span class="italic text-blue-800">Art</span>ificial Intelligence
      </h1>
      <div class="mt-6">
        <form @submit.prevent="fetchAndLoadQueryResults" class="bg-white border-2 border-black px-8 pt-6 pb-8 mb-4">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="query">
              Query
            </label>
            <input v-model="artQuery"
              class="appearance-none border-black border-2 w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="query" type="text" placeholder="A woman standing up and wearing a black dress" />
          </div>
          <div class="flex items-center justify-between">
            <button :disabled="loading"
              class="bg-blue-800 inline-flex hover:bg-blue-700 text-white font-bold py-2 px-4 focus:outline-none focus:shadow-outline"
              type="submit">
              <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              Search
            </button>
          </div>
        </form>
      </div>
    </div>
    <div ref="pixiContainer" class="w-full h-screen mt-4 overflow-hidden border-2 border-black">
      <canvas class=""></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Application, Graphics, Sprite, Assets, Text, Cache } from 'pixi.js';
import { Viewport } from 'pixi-viewport';

const pixiContainer = ref<HTMLDivElement | null>(null);
const { width, height } = useElementSize(pixiContainer)
const artQuery = ref("");
const loading = ref(false);
const images = ref<Sprite[]>([]);
const points = ref<{ x: number, y: number }[]>([
  // Example points; replace these with your actual data
  { x: 100, y: 100 },
  { x: 200, y: 200 },
  { x: 300, y: 300 },
  { x: 400, y: 400 },
  { x: 500, y: 500 },
  { x: 600, y: 600 },
  { x: 700, y: 700 },
  { x: 800, y: 800 },
  { x: 900, y: 900 },
  { x: 1000, y: 1000 },
]);
const baseOffset = 5000; // Base distance between images, otherwise they overlap
const scale = ref(1);
const pixiApp = ref<Application>();
const viewport = ref<Viewport>();

const fetchImageUrls = async () => {
  try {
    const topK = 5;
    const response = await $fetch(
      `http://127.0.0.1:8000/query?art_query=${artQuery.value}&top_k=${topK}`
    );
    return response.map((item: { image_url: string }) => item.image_url);
  } catch (error) {
    console.error("Error fetching image URLs:", error);
    return [];
  }
};

const loadImages = async () => {
  const urls = await fetchImageUrls();
  const textures = {};

  for (const [index, url] of urls.entries()) {
    textures[`image-${index}`] = await Assets.load({
      src: url,
      loadParser: 'loadTextures'
    });
  }

  return textures;
};

const fetchAndLoadQueryResults = async () => {
  try {
    // TODO: Only remove image childeren, the scatterplot should remains
    images.value.forEach((sprite) => {
      viewport.value?.removeChild(sprite);
    });

    loading.value = true;

    const textures = await loadImages();
    images.value = Object.values(textures).map((texture: any) => new Sprite(texture));

    // Constants for centering and offset
    const centerX = width.value / 2;
    const centerY = height.value / 2;
    const offset = baseOffset * scale.value;

    // Add images and points to the viewport
    images.value.forEach((sprite, index) => {
      sprite.interactive = true;
      sprite.anchor.set(0.5);

      let pos = { x: centerX, y: centerY };

      // Calculate positions for the surrounding images
      if (index > 0) {
        switch (index) {
          case 1:
            pos = { x: centerX + offset, y: centerY }; // Right
            break;
          case 2:
            pos = { x: centerX - offset, y: centerY }; // Left
            break;
          case 3:
            pos = { x: centerX, y: centerY + offset }; // Bottom
            break;
          case 4:
            pos = { x: centerX, y: centerY - offset }; // Top
            break;
        }
      }

      sprite.x = pos.x;
      sprite.y = pos.y;

      sprite.on('pointerdown', () => {
        console.log(`Image ${index} clicked!`);
        // TODO: Add click handling logic
      });
      viewport.value.addChild(sprite);
    });

  } catch (error) {
    console.error("Error loading images:", error);
  } finally {
    loading.value = false;
  }
};

const initializePixi = async () => {
  if (!pixiContainer.value) return;

  const app = new Application();
  // Create a new application
  await app.init({
    canvas: document.querySelector("canvas"),
    width: width.value,
    height: height.value,
    background: '#fff',
    antialias: true,
    autoDensity: true,
    resolution: 2,
  });

  pixiApp.value = app;

  // Create viewport
  const vp = new Viewport({
    passiveWheel: false,
    events: pixiApp.value.renderer.events
  }).drag().pinch().wheel().decelerate();

  viewport.value = vp;

  // Add the viewport to the stage
  pixiApp.value.stage.addChild(viewport.value);

  // Load scatter plot points
  loadScatterPlotPoints(viewport.value);
};

const loadScatterPlotPoints = (viewport) => {

  const text = viewport.addChild(
    new Text({
      text: 'hello world 😁',
      style: {
        fontFamily: 'short-stack'
      }
    })
  );

  text.anchor.set(0.5);
  text.resolution = 8;
  text.x = viewport.screenWidth / 2;
  text.y = viewport.screenHeight / 2;
  const graphics = new Graphics();

  points.value.forEach((point) => {
    graphics.circle(point.x, point.y, 15).fill("blue", 1);
  });

  graphics.interactive = true;
  graphics.on('pointerdown', (event) => {
    const clickX = event.global.x;
    const clickY = event.global.y;

    points.value.forEach((point) => {
      if (
        clickX >= point.x - 2 &&
        clickX <= point.x + 2 &&
        clickY >= point.y - 2 &&
        clickY <= point.y + 2
      ) {
        console.log(`Point clicked at (${point.x}, ${point.y})`);
        // TODO: Add your click handling logic here
      }
    });
  });

  viewport.addChild(graphics);
};

onMounted(() => {
  initializePixi();
});

</script>
