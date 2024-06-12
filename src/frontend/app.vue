<template>
  <div class="p-4 h-screen">
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
    <div class="w-full h-full mt-4 overflow-hidden">
      <canvas ref="canvas" class="block w-full h-full border-2 border-black" @mousedown="startDrag" @mousemove="drag"
        @mouseup="endDrag" @wheel="zoom"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
const canvas = ref<HTMLCanvasElement | null>(null);
const isDragging = ref(false);
const imgPositions = ref([]);
const scale = ref(0.10);
const images = ref<HTMLImageElement[]>([]);
const baseOffset = 2500; // Base distance between images, otherwise they overlap
const ctx = ref<CanvasRenderingContext2D | null>(null);
const dragStart = ref({ x: 0, y: 0 });
const artQuery = ref("");
const loading = ref(false);

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
  return Promise.all(
    urls.map(
      (url: string) =>
        new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.src = url;
          img.onload = () => resolve(img);
          img.onerror = () =>
            reject(new Error(`Failed to load image at ${url}`));
        })
    )
  );
};

const fetchAndLoadQueryResults = async () => {
  try {
    loading.value = true;
    images.value = await loadImages();
    positionImages();
    redraw();
  } catch (error) {
    console.error("Error loading images:", error);
  } finally {
    loading.value = false;
  }
};

const initializeCanvas = async () => {
  const canvasEl = canvas.value;
  if (!canvasEl) return;

  ctx.value = canvasEl.getContext("2d");
  resizeCanvas();

  // try {
  //   images.value = await loadImages();
  //   positionImages();
  //   redraw();
  // } catch (error) {
  //   console.error('Error loading images:', error);
  // }
};

const positionImages = () => {
  if (!canvas.value) return;
  const { width, height } = canvas.value;

  const centerX = width / 2;
  const centerY = height / 2;
  const offset = baseOffset * scale.value;

  imgPositions.value = [
    { x: centerX, y: centerY }, // Center image
    { x: centerX - offset, y: centerY - offset }, // Top-left
    { x: centerX + offset, y: centerY - offset }, // Top-right
    { x: centerX - offset, y: centerY + offset }, // Bottom-left
    { x: centerX + offset, y: centerY + offset } // Bottom-right
  ];
};

const resizeCanvas = () => {
  const canvasEl = canvas.value;
  if (!canvasEl || !ctx.value) return;
  canvasEl.width = canvasEl.offsetWidth;
  canvasEl.height = canvasEl.offsetHeight;
  positionImages();
  redraw();
};

onMounted(() => {
  initializeCanvas();
  window.addEventListener("resize", resizeCanvas);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCanvas);
});

const startDrag = (e: MouseEvent) => {
  isDragging.value = true;
  dragStart.value = { x: e.clientX, y: e.clientY };
};

const drag = (e: MouseEvent) => {
  if (!isDragging.value || !ctx.value || images.value.length === 0) return;

  const dx = e.clientX - dragStart.value.x;
  const dy = e.clientY - dragStart.value.y;
  dragStart.value = { x: e.clientX, y: e.clientY };

  imgPositions.value.forEach((pos) => {
    pos.x += dx;
    pos.y += dy;
  });

  redraw();
};

const endDrag = () => {
  isDragging.value = false;
};

const zoom = (e: WheelEvent) => {
  e.preventDefault();
  const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
  scale.value *= zoomFactor;
  positionImages();

  redraw();
};

const redraw = () => {
  if (!ctx.value || !canvas.value || images.value.length === 0) return;
  ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);
  images.value.forEach((image, index) => {
    const pos = imgPositions.value[index];
    if (pos && image) {
      ctx.value.drawImage(
        image,
        pos.x - (image.width * scale.value) / 2,
        pos.y - (image.height * scale.value) / 2,
        image.width * scale.value,
        image.height * scale.value
      );
    }
  });
};
</script>
