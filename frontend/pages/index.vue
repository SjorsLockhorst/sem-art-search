<template>
  <div class="p-4 min-h-screen">
    <div>
      <h1 class="text-4xl font-bold">
        <span class="italic text-blue-800">Art</span>ificial Intelligence
      </h1>
      <h2 class="text-l mt-1">Search through Rijksmuseum artworks based on <span
          class="italic text-blue-800">meaning</span>
      </h2>
    </div>

    <div ref="pixiContainer" class="relative w-full h-full mt-4 overflow-hidden border-2 border-black">
      <canvas class="h-screen"></canvas>
      <form @submit.prevent="fetchAndLoadQueryResults"
        class="absolute top-8 left-8 shadow-md rounded-md bg-white w-5/6 lg:w-96">
        <div>
          <label for="hs-trailing-button-add-on-with-icon" class="sr-only">Label</label>
          <div class="flex rounded-lg shadow-sm">
            <input v-model="artQuery" type="text" id="hs-trailing-button-add-on-with-icon"
              name="hs-trailing-button-add-on-with-icon"
              class="py-3 px-4 block w-full border-gray-200 shadow-sm rounded-s-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none ">
            <button type="submit"
              class="w-[2.875rem] h-[2.875rem] shrink-0 inline-flex justify-center items-center gap-x-2 text-sm font-semibold rounded-e-md border border-transparent bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:bg-blue-700 disabled:opacity-50 disabled:pointer-events-none">
              <svg v-if="loading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                </circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <svg v-else class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </svg>
            </button>
          </div>
        </div>
      </form>
      <div v-if="selectedArtwork"
        class="absolute top-28 lg:top-32 left-8 shadow-md rounded-md bg-neutral-100 w-5/6 lg:w-[500px] p-4">
        <div class="text-right mb-2">
          <button @click="closePopUp">
            <svg fill="#000000" height="12px" width="12px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
              xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 490 490" xml:space="preserve">
              <polygon points="456.851,0 245,212.564 33.149,0 0.708,32.337 212.669,245.004 0.708,457.678 33.149,490 245,277.443 456.851,490 
	489.292,457.678 277.331,245.004 489.292,32.337 " />
            </svg>
          </button>
        </div>
        <div class="flex items-center justify-center mb-4">
          <img :src="selectedArtwork.image_url" :alt="selectedArtwork.long_title" class="max-h-[40vh] lg:max-h-[50vh]">
        </div>
        <h3 class="text-xl font-bold text-blue-800">{{ selectedArtwork.artist }}</h3>
        <h4>{{ selectedArtwork.long_title }} </h4>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-2 gap-y-2 lg:gap-y-0 mt-4">
          <div>
            <button :disabled="loading" @click="loadImageResults(selectedArtwork.id)"
              class="w-full flex items-center justify-center space-x-2 text-white  bg-blue-700 border-blue-700 border-2 hover:bg-blue-800 hover:border-blue-800 font-medium rounded-lg px-4 py-2">
              <svg v-if="loading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <span v-if="!loading">Search using this image</span>
              <span v-else>Loading...</span>
            </button>
          </div>
          <div>
            <a :href="`https://www.rijksmuseum.nl/en/collection/${selectedArtwork.original_id}`" target="_blank"
              class="flex items-center justify-center space-x-2 text-blue-700 hover:text-white  border-blue-700 border-2 hover:bg-blue-800 hover:border-blue-800 font-medium rounded-lg px-4 py-2">
              <svg v-if="loading" class="animate-spin h-5 w-5 text-blue-700" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <span v-if="!loading">More information</span>
              <span v-else>Loading...</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Viewport } from "pixi-viewport";
import { Application, Assets, Container, Point, Sprite, Ticker, Text } from "pixi.js";
import { computed, onMounted, ref } from "vue";
import { Simple } from "~/utils/pixi-cull";

// Init composables
const config = useRuntimeConfig()
const { $toast } = useNuxtApp()

// Local state
const pixiContainer = ref<HTMLDivElement | null>(null);
const { width, height } = useElementSize(pixiContainer);
const artQuery = ref("");
const loading = ref(false);
const topK = ref(10);
const selectedArtworkIndex = ref<number | null>(null);
const allArtworks = ref<Artwork[]>([]);

let app: Application;
let viewport: Viewport;
let container: Container;
let cull: Simple;
let seenArtObjects: Set<number> = new Set<number>();
let querySet: Set<string> = new Set();
let ArtworkIdSet: Set<number> = new Set();

const apiBaseUrl = config.public.apiBase
const WORLD_WIDTH = 20000;
const WORLD_HEIGHT = 20000;
const imgWidth = 500;

// Typing
interface QueryResponse {
  query_x: number;
  query_y: number;
  art_objects_with_coords: Artwork[]
}

interface Artwork {
  original_id: string;
  image_url: string;
  artist: string;
  id: number;
  long_title: string;
  x: number;
  y: number;
}

// Methods
const closePopUp = () => {
  selectedArtworkIndex.value = null
}

const fetchArtworksById = async (id: number): Promise<Artwork[]> => {
  try {
    loading.value = true;

    const url = `${apiBaseUrl}/image?idx=${id}&top_k=${topK.value}`
    const response = await $fetch<Artwork[]>(url);

    return response;
  } catch (error) {
    $toast.error("Error fetching artworks")
    throw error;
  } finally {
    loading.value = false;
  }
}

const fetchArtworks = async (): Promise<QueryResponse> => {
  try {
    loading.value = true

    const url = `${apiBaseUrl}/query?art_query=${artQuery.value}&top_k=${topK.value}`
    const response: QueryResponse = await $fetch<QueryResponse>(url);

    return response;
  } catch (error) {
    $toast.error("Error fetching artworks")
    throw error;
  } finally {
    loading.value = false;
  }
}

const getAverage = (points: Artwork[]): { averageX: number, averageY: number } => {
  const total = points.reduce((acc, point) => {
    acc.x += point.x;
    acc.y += point.y;
    return acc;
  }, { x: 0, y: 0 });

  const count = points.length;

  return {
    averageX: total.x / count,
    averageY: total.y / count
  };
};

const animateScale = (sprite: Sprite, targetScaleX: number, targetScaleY: number, duration = 0.1) => {
  const startScaleX = sprite.scale.x;
  const startScaleY = sprite.scale.y;
  const startTime = Date.now();

  const scaleSprite = () => {
    const elapsed = (Date.now() - startTime) / 1000;
    const progress = Math.min(elapsed / duration, 1);

    sprite.scale.x = startScaleX + (targetScaleX - startScaleX) * progress;
    sprite.scale.y = startScaleY + (targetScaleY - startScaleY) * progress;

    if (progress === 1) {
      Ticker.shared.remove(scaleSprite, sprite);
    }
  };
  Ticker.shared.add(scaleSprite, sprite);
};

const drawArtWorks = (artworks: Artwork[], indexOffset: number) => {
  artworks
    .forEach(async (artwork, index) => {
      seenArtObjects.add(artwork.id)
      artwork.image_url = artwork.image_url.replace("=s0", `=w${imgWidth}`)

      const texture = await Assets.load({ src: artwork.image_url, loadParser: "loadTextures" });
      const sprite = Sprite.from(texture);

      sprite.anchor.set(0.5)
      sprite.x = artwork.x * WORLD_WIDTH;
      sprite.y = artwork.y * WORLD_HEIGHT;
      sprite.interactive = true;

      const startScaleX = sprite.scale.x;
      const startScaleY = sprite.scale.y;

      sprite.on('mouseover', () => {
        sprite.zIndex += 10000;
        animateScale(sprite, startScaleX * 1.2, startScaleY * 1.2);
      });

      sprite.on('mouseleave', () => {
        sprite.zIndex -= 10000;
        animateScale(sprite, startScaleX, startScaleY);
      });

      sprite.on('pointerdown', () => {
        selectedArtworkIndex.value = index + indexOffset
      });

      cull.add(sprite);
      container.addChild(sprite);
    })
}

const loadImageResults = async (artwork_id: number) => {
  if (ArtworkIdSet.has(artwork_id)) {
    return;
  }

  let newArtworks = await fetchArtworksById(artwork_id);

  closePopUp();

  ArtworkIdSet.add(artwork_id)

  drawArtWorks(newArtworks, allArtworks.value.length);

  allArtworks.value = [...allArtworks.value, ...newArtworks]

  const { averageX, averageY } = getAverage(newArtworks);
  const middlePoint = new Point(averageX * WORLD_WIDTH, averageY * WORLD_HEIGHT);

  viewport.animate({ position: middlePoint, scale: 0.15 });
}

const fetchAndLoadQueryResults = async () => {
  try {
    if (querySet.has(artQuery.value)) {
      return;
    }

    const newArtworks = await fetchArtworks();

    closePopUp();

    querySet.add(artQuery.value);

    if (newArtworks.art_objects_with_coords.length !== 0) {
      drawArtWorks(newArtworks.art_objects_with_coords, allArtworks.value.length);
      allArtworks.value = [...allArtworks.value, ...newArtworks.art_objects_with_coords];

      const { averageX, averageY } = getAverage(newArtworks.art_objects_with_coords);
      const middlePoint = new Point(averageX * WORLD_WIDTH, averageY * WORLD_HEIGHT);
      viewport.animate({ position: middlePoint, scale: 0.15 });

      let text = new Text({
        text: artQuery.value, style: {
          fontFamily: "Arial",
          fontSize: 128
        }
      });
      text.position = middlePoint;

      artQuery.value = "";

      container.addChild(text);
    }
  } catch (error) {
    $toast.error("Error loading images")
  }
};

const initializePixi = async () => {
  if (!pixiContainer.value) return;

  app = new Application();

  await app.init({
    canvas: document.querySelector("canvas") as HTMLCanvasElement,
    width: width.value,
    height: height.value,
    background: "#fff",
    antialias: true,
    autoDensity: true,
    resolution: 2,
  });

  globalThis.__PIXI_APP__ = app;

  pixiContainer.value.appendChild(app.canvas);

  viewport = new Viewport({
    passiveWheel: false,
    events: app.renderer.events,
    worldWidth: WORLD_WIDTH,
    worldHeight: WORLD_HEIGHT
  })

  // activate plugins
  viewport.drag().pinch().wheel().decelerate()

  app.stage.addChild(viewport);

  cull = new Simple({ dirtyTest: true });
  cull.addList(viewport.children);
  cull.cull(viewport.getVisibleBounds());

  const ticker = Ticker.shared;

  // cull whenever the viewport moves
  ticker.add(() => {
    if (viewport.dirty) {
      cull.cull(viewport.getVisibleBounds(), true);
      viewport.dirty = false;
    }
  });

  ticker.start();

  container = new Container();
  viewport.addChild(container);
};

const selectedArtwork = computed(() => {
  if (selectedArtworkIndex.value != null) {
    return allArtworks.value[selectedArtworkIndex.value]
  }
  return null
})

onMounted(() => {
  initializePixi();
});

</script>
