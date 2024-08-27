<template>
    <div class="p-4 min-h-screen">
        <h1 class="text-4xl font-bold">
            <span class="italic text-blue-800">Art</span>ificial Intelligence
        </h1>
        <div class="mt-6 w-full md:w-1/2 max-w-md mx-auto my-12">
            <form @submit.prevent="loadImages" class="relative shadow-md rounded-md">
                <label for="default-search" class="mb-2 font-medium text-gray-900 sr-only ">Search</label>
                <div class="relative">
                    <input v-model="artQuery" type="search" id="default-search"
                        class="block w-full p-4 text-gray-900 bg-neutral-100 rounded-md"
                        placeholder="A woman in a black dress" required />
                    <button :disabled="loading" type="submit"
                        class="text-white absolute end-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800  font-medium rounded-lg text-sm px-4 py-2 ">
                        <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                        </svg>
                        <span v-if="!loading">Search</span>
                    </button>
                </div>
            </form>
        </div>
        <div class="flex justify-center  min-h-screen" v-if="mainImage">
            <div class="container mx-auto px-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="flex justify-center ">
                        <div v-if="loading && !mainImageLoaded"
                            class="animate-pulse bg-gray-300 rounded-2xl w-full aspect-square"></div>
                        <Transition name="fade" mode="out-in">
                            <div v-show="mainImageLoaded">
                                <NuxtImg v-show="mainImageLoaded" :src="mainImage?.image_url" :key="mainImageKey"
                                    class="rounded-2xl max-w-full h-auto object-cover" @load="onMainImageLoad" />
                                <div v-if="mainImageLoaded">
                                    <p class="text-lg ">
                                        {{ mainImage.long_title }} -
                                        <span class="italic"> {{ mainImage.artist }}</span>
                                    </p>
                                </div>
                            </div>
                        </Transition>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div v-for="(relatedImage, index) in relatedImages" :key="relatedImageKeys[index]"
                            class="flex justify-center items-center">
                            <div v-if="loading && !relatedImagesLoaded[index]"
                                class="animate-pulse bg-gray-300 rounded-2xl w-full aspect-square"></div>
                            <Transition name="fade" mode="out-in">
                                <div v-show="relatedImagesLoaded[index]">
                                    <NuxtImg v-show="relatedImagesLoaded[index]" :src="relatedImage.image_url"
                                        class="rounded-2xl max-w-full h-auto object-cover"
                                        @load="onRelatedImageLoad(index)" :key="relatedImageKeys[index]" />
                                    <div v-if="relatedImagesLoaded[index]">
                                        <p class="text-lg ">
                                            {{ relatedImage.long_title }} -
                                            <span class="italic"> {{ relatedImage.artist }}</span>
                                        </p>
                                    </div>
                                </div>
                            </Transition>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const artQuery = ref("");
const previousQuery = ref("");
const loading = ref(false);
const mainImage = ref<Artwork | null>(null);
const relatedImages = ref<Artwork[]>([]);
const mainImageLoaded = ref(false);
const relatedImagesLoaded = ref<boolean[]>([]);
const mainImageKey = ref("");
const relatedImageKeys = ref<string[]>([]);

interface Artwork {
    original_id: string;
    image_url: string;
    artist: string;
    id: number;
    long_title: string;
    x: number;
    y: number;
}

const generateUniqueKey = () => {
    return Math.random().toString(36).substring(2, 22);
};

const fetchArtworks = async (): Promise<Artwork[]> => {
    try {
        const topK = 5;
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
    if (previousQuery.value === artQuery.value) {
        return;
    }
    loading.value = true;
    relatedImagesLoaded.value = [];
    try {
        const artworks = await fetchArtworks();
        if (artworks.length > 0) {
            const [first, ...rest] = artworks;
            mainImage.value = first;
            relatedImages.value = rest;
            relatedImagesLoaded.value = new Array(rest.length).fill(false);
            mainImageLoaded.value = false;
            mainImageKey.value = generateUniqueKey();
            relatedImageKeys.value = rest.map(() => generateUniqueKey());
        } else {
            mainImage.value = null;
            relatedImages.value = [];
        }
        previousQuery.value = artQuery.value
    } catch (error) {
        console.error("Error loading artworks:", error);
        mainImage.value = null;
        relatedImages.value = [];
    }
};

const onMainImageLoad = () => {
    mainImageLoaded.value = true;
    checkAllImagesLoaded();
};

const onRelatedImageLoad = (index: number) => {
    relatedImagesLoaded.value[index] = true;
    checkAllImagesLoaded();
};

const checkAllImagesLoaded = () => {
    if (mainImageLoaded.value && relatedImagesLoaded.value.every(loaded => loaded)) {
        loading.value = false;
    }
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
