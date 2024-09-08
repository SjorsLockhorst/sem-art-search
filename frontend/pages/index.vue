<template>
    <div class="p-4 h-screen">
        <div>
            <h1 class="text-4xl font-bold">
                <span class="italic text-blue-800">Art</span>ificial Intelligence
            </h1>
            <h2 class="text-l mt-1">Search through Rijksmuseum artworks based on <span class="italic text-blue-800">meaning</span></h2>
        </div>
        <!-- Position selectedArtwork absolutely in the bottom right corner of the page -->

        <div ref="pixiContainer" class="relative w-full h-full mt-4 overflow-hidden border-2 border-black">
            <canvas></canvas>
            <!-- Floating form in the top-left corner -->
            <form @submit.prevent="fetchAndLoadQueryResults" 
                class="absolute top-8 left-8 shadow-md rounded-md bg-white w-96">
                <label for="default-search" class="mb-2 font-medium text-gray-900 sr-only">Search</label>
                <input v-model="artQuery" 
                    type="search" 
                    id="default-search"
                    class="block w-full p-4 text-gray-900 bg-neutral-100 rounded-md"
                    placeholder="A woman standing in a black dress" required />
                <button :disabled="loading" 
                    type="submit"
                    class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 font-medium rounded-lg text-sm px-4 py-2">
                    <svg v-if="loading" 
                        class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg" 
                        fill="none" 
                        viewBox="0 0 24 24">
                        <circle class="opacity-25" 
                            cx="12" 
                            cy="12" 
                            r="10" 
                            stroke="currentColor" 
                            stroke-width="4"></circle>
                        <path class="opacity-75" 
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span v-if="!loading">Search</span>
                </button>
            </form>

        <div v-if="selectedArtwork" class="absolute top-32 left-8 shadow-md rounded-md bg-neutral-100 w-96 p-4">
            <img :src="selectedArtwork.image_url" :alt="selectedArtwork.long_title" class="max-h-[50vh]">
            <h3 class="font-bold text-blue-800">{{ selectedArtwork.artist }}</h3>
            <h4>{{ selectedArtwork.long_title}} </h4>
                <button :disabled="loading" 
                    @click="loadImageResults(selectedArtwork.id)"
                    class="text-white right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 font-medium rounded-lg text-sm px-4 py-2 mt-2">
                    <svg v-if="loading" 
                        class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg" 
                        fill="none" 
                        viewBox="0 0 24 24">
                        <circle class="opacity-25" 
                            cx="12" 
                            cy="12" 
                            r="10" 
                            stroke="currentColor" 
                            stroke-width="4"></circle>
                        <path class="opacity-75" 
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span v-if="!loading">Search using this image</span>
                </button>
                <!-- <a :href="`https://www.rijksmuseum.nl/en/collection/${selectedArtwork.original_id}`" class="border-black border-2 p-8 bg-blue-700">View at Rijks</a> -->
        </div>
            <!-- End of form -->
        </div>
    </div>
</template>


<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { Application, Sprite, Assets, Point, Ticker, Container, Text } from "pixi.js";
import { Viewport } from "pixi-viewport";
import { Simple } from "~/utils/pixi-cull";

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
let ticker: Ticker;

const WORLD_WIDTH = 15000;
const WORLD_HEIGHT = 15000;
const imgWidth = 500;

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

const fetchArtworksById = async(id: number): Promise<QueryResponse> => {
    loading.value = true;
    try {
        const response = await $fetch<QueryResponse>(
            `http://127.0.0.1:8000/image?id=${id}&top_k=${topK.value}`
        );
        return response;
    } catch (error) {
        console.error("Error fetching artworks:", error);
        throw error;
    } finally {
        loading.value = false;
    }
}

const fetchArtworks = async (): Promise<QueryResponse> => {
    loading.value = true
    try {
        const response: QueryResponse = await $fetch<QueryResponse>(
            `http://127.0.0.1:8000/query?art_query=${artQuery.value}&top_k=${topK.value}`
        );
        return response;
    } catch (error) {
        console.error("Error fetching artworks:", error);
        throw error;
    } finally {
        loading.value = false;
    }
}

function getAverage(points: Artwork[]): { averageX: number, averageY: number } {
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
function animateScale(sprite: Sprite, factor: number, startScaleX: number, startScaleY: number, duration = 0.1) {
    const startTime = Date.now();


    const scaleSprite = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        const progress = Math.min(elapsed / duration, 1);

        sprite.scale.x = startScaleX + (startScaleX * (1 + factor) - startScaleX) * progress;
        sprite.scale.y = startScaleY + (startScaleY * (1 + factor) - startScaleY) * progress;

        if (progress === 1) {
            Ticker.shared.remove(scaleSprite, sprite);
        }
    }

    Ticker.shared.add(scaleSprite, sprite);
}

const drawArtWorks = (artworks: Artwork[], indexOffset: number) => {
    const {averageX, averageY} = getAverage(artworks);
    const middlePoint = new Point(averageX * WORLD_WIDTH, averageY * WORLD_HEIGHT);
    viewport.animate( { position: middlePoint, scale: 0.15 });

    artworks
        .filter(artwork => !seenArtObjects.has(artwork.id))
        .forEach(async (artwork, index) => {
            seenArtObjects.add(artwork.id)
            artwork.image_url = artwork.image_url.replace("=s0", `=w${imgWidth}`)
            const texture = await Assets.load({src: artwork.image_url, loadParser: "loadTextures"});
            const sprite = Sprite.from(texture);
            sprite.anchor.set(0.5)
            sprite.x = artwork.x * WORLD_WIDTH;
            sprite.y = artwork.y * WORLD_HEIGHT;
            sprite.interactive = true;

            const startScaleX = sprite.scale.x;
            const startScaleY = sprite.scale.y;

            sprite.on('mouseover', () => {
                sprite.zIndex += 10000
                animateScale(sprite, .2, startScaleX, startScaleY)
            });
            sprite.on('mouseleave', () => {
                sprite.zIndex -= 10000
                animateScale(sprite, -.2, startScaleX, startScaleY)
            });
            sprite.on('pointerdown', () => {
                selectedArtworkIndex.value = index + indexOffset
                console.log("Your mouse is down")
            });

            cull.add(sprite);
            container.addChild(sprite);
    })
}

const loadImageResults = async (artwork_id: number) => {
    const newArtworks = await fetchArtworksById(artwork_id);
    drawArtWorks(newArtworks.art_objects_with_coords, allArtworks.value.length);
    allArtworks.value = [...allArtworks.value, ...newArtworks.art_objects_with_coords]
}

const fetchAndLoadQueryResults = async () => {
    try {
        const queryResponse = await fetchArtworks();
        const queryPoint = new Point(queryResponse.query_x * WORLD_WIDTH, queryResponse.query_y * WORLD_HEIGHT);

        let text = new Text({text: artQuery.value, style: {
            fontFamily: "Arial",
            fontSize: 128

        }});
        text.position = queryPoint;
        container.addChild(text);
        drawArtWorks(queryResponse.art_objects_with_coords, allArtworks.value.length);
        allArtworks.value = [...allArtworks.value, ...queryResponse.art_objects_with_coords]

    } catch (error) {
        console.error("Error loading images:", error);
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

