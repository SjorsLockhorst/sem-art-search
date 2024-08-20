<template>
    <div class="p-4 h-screen">
        <div>
            <h1 class="text-4xl font-bold">
                <span class="italic text-blue-800">Art</span>ificial Intelligence
            </h1>
            <div class="mt-6">
                <form @submit.prevent="fetchAndLoadQueryResults"
                    class="bg-white border-2 border-black px-8 pt-6 pb-8 mb-4">
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
                            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
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
            <canvas></canvas>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Application, Graphics, Sprite, Assets, Text, RenderTexture, Container, Ticker } from "pixi.js";
import { Viewport } from "pixi-viewport";
import { Simple } from "../../utils/pixi-cull/index"

const pixiContainer = ref<HTMLDivElement | null>(null);
const { width, height } = useElementSize(pixiContainer);
const artQuery = ref("");
const loading = ref(false);
const images = ref<Sprite[]>([]);
const baseOffset = 5000; // Base distance between images, otherwise they overlap
const scale = ref(1);

let pixiApp: Application;
let viewport: Viewport;

interface Artwork {
    original_id: string;
    image_url: string;
    artist: string;
    id: number;
    long_title: string;
    x: number;
    y: number;
}

const fetchArtworks = async (): Promise<Artwork[]> => {
    try {
        const topK = 10;
        const response: Artwork[] = await $fetch<Artwork[]>(
            `http://127.0.0.1:8000/query?art_query=${artQuery.value}&top_k=${topK}`
        );
        return response;
    } catch (error) {
        console.error("Error fetching artworks:", error);
        return [];
    }
};

const loadImages = async () => {
    const artworks = await fetchArtworks();
    const urls = artworks.map((item: { image_url: string }) => item.image_url);
    const textures = {};

    for (const [index, url] of urls.entries()) {
        textures[`image-${index}`] = await Assets.load({
            src: url,
            loadParser: "loadTextures"
        });
    }

    return textures;
};

const generateRandomPoints = (numPoints: number, maxX: number, maxY: number) => {
    const pointsArray = [];
    for (let i = 0; i < numPoints; i++) {
        pointsArray.push({
            x: Math.round(Math.random() * maxX),
            y: Math.round(Math.random() * maxY),
        });
    }
    return pointsArray;
};

const fetchAndLoadQueryResults = async () => {
    try {
        loading.value = true;

        const artworks = await fetchArtworks();

        const urls = artworks.map((item: { image_url: string }) => item.image_url);
        const textures = {};

        for (const [index, url] of urls.entries()) {
            textures[`image-${index}`] = await Assets.load({
                src: url,
                loadParser: "loadTextures"
            });
        }

        images.value = Object.values(textures).map(
            (texture: any) => new Sprite(texture)
        );

        // Add images and points to the viewport
        images.value.forEach((sprite, index) => {
            sprite.interactive = true;
            sprite.anchor.set(0.5);

            const artwork = artworks[index]

            const scalefactor = 10000;
            sprite.x = artwork.x * scalefactor + sprite.width;
            sprite.y = artwork.y * scalefactor + sprite.height;

            sprite.on("pointerdown", () => {
                console.log(`Image ${index} clicked!`);
            });

            viewport.addChild(sprite);

        });
    } catch (error) {
        console.error("Error loading images:", error);
    } finally {
        loading.value = false;
    }
};

const initializePixi = async () => {
    if (!pixiContainer.value) return;

    pixiApp = new Application();
    await pixiApp.init({
        canvas: document.querySelector("canvas") as HTMLCanvasElement,
        width: width.value,
        height: height.value,
        background: "#fff",
        antialias: true,
        autoDensity: true,
        resolution: 2,
    });

    pixiContainer.value.appendChild(pixiApp.canvas);

    // Create viewport
    viewport = new Viewport({
        screenWidth: width.value,
        screenHeight: height.value,
        worldWidth: 10000,
        worldHeight: 10000,
        events: pixiApp.renderer.events
    })
        .drag()
        .pinch()
        .wheel()
        .decelerate();

    // Add the viewport to the stage
    pixiApp.stage.addChild(viewport);

    const cull = new Simple({ dirtyTest: true });
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
};

onMounted(() => {
    initializePixi();
});
</script>
