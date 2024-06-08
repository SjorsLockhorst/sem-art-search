<template>
  <div class="p-4 h-screen">
    <div>
      <h1 class="text-4xl font-bold"><span class="italic">Art</span>ificial Intelligence</h1>
    </div>
    <div class="w-full h-full mt-4 overflow-hidden">
      <canvas ref="canvas" class="block w-full h-full border-2 border-black" @mousedown="startDrag" @mousemove="drag"
        @mouseup="endDrag" @wheel="zoom"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

const canvas = ref<HTMLCanvasElement | null>(null);
let ctx: CanvasRenderingContext2D | null = null;
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let imgPositions = [];
let scale = 1;
let images: HTMLImageElement[] = [];

const fetchImageUrls = async () => {
  try {
    const artQuery = "woman in a black dress"
    const topK = 5
    const response = await $fetch<string[]>(`http://127.0.0.1:8000/query?art_query=${artQuery}&top_k=${topK}`);
    return response.map((item: { image_url: string }) => item.image_url);
  } catch (error) {
    console.error('Error fetching image URLs:', error);
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
          img.onerror = () => reject(new Error(`Failed to load image at ${url}`));
        })
    )
  );
};

const initializeCanvas = async () => {
  const canvasEl = canvas.value;
  if (!canvasEl) return;

  ctx = canvasEl.getContext('2d');
  resizeCanvas();

  try {
    images = await loadImages();
    positionImages();
    redraw();
  } catch (error) {
    console.error('Error loading images:', error);
  }
};

const positionImages = () => {
  if (!canvas.value) return;
  const { width, height } = canvas.value;

  const centerX = width / 2;
  const centerY = height / 2;
  const offset = 100;

  imgPositions = [
    { x: centerX, y: centerY }, // Center image
    { x: centerX - offset, y: centerY - offset }, // Top-left
    { x: centerX + offset, y: centerY - offset }, // Top-right
    { x: centerX - offset, y: centerY + offset }, // Bottom-left
    { x: centerX + offset, y: centerY + offset }, // Bottom-right
  ];
};

const resizeCanvas = () => {
  const canvasEl = canvas.value;
  if (!canvasEl || !ctx) return;
  canvasEl.width = canvasEl.offsetWidth;
  canvasEl.height = canvasEl.offsetHeight;
  redraw();
};

onMounted(() => {
  initializeCanvas();
  window.addEventListener('resize', resizeCanvas);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCanvas);
});

const startDrag = (e: MouseEvent) => {
  isDragging = true;
  dragStart = { x: e.clientX, y: e.clientY };
};

const drag = (e: MouseEvent) => {
  if (!isDragging || !ctx || images.length === 0) return;

  const dx = e.clientX - dragStart.x;
  const dy = e.clientY - dragStart.y;
  dragStart = { x: e.clientX, y: e.clientY };

  imgPositions.forEach(pos => {
    pos.x += dx;
    pos.y += dy;
  });

  redraw();
};

const endDrag = () => {
  isDragging = false;
};

const zoom = (e: WheelEvent) => {
  e.preventDefault();
  const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
  scale *= zoomFactor;

  redraw();
};

const redraw = () => {
  if (!ctx || !canvas.value || images.length === 0) return;
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height);
  images.forEach((image, index) => {
    const pos = imgPositions[index];
    if (pos && image) {
      ctx.drawImage(image, pos.x - (image.width * scale) / 2, pos.y - (image.height * scale) / 2, image.width * scale, image.height * scale);
    }
  });
};
</script>
