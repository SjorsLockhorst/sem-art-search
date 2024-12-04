# Introducing [artexplorer.ai](https://artexplorer.ai)

A search engine that lets you search through artworks based on a 'vibe'.
Try it out by going to [artexplorer.ai](https://artexplorer.ai), and searching for a vibe

> 'A gloomy landscape in the winter'.

You will be shown the 10 artworks that most fit your query.
You can also click images to find out more about them, and find more similar images like them.

Currently, it supports all public artworks from [Rijksmuseum Amsterdam](https://www.rijksmuseum.nl/en), with the ambition to add art from other open sources at a later moment.
## Background

Imagine this, you just finished your visit to the Amsterdam Rijks Museum and you want to tell your friends about this amazing piece of art that you saw. It was this beautiful painting of a group of people in a bar, having a great time. However, you don't remember the title... Now what?

You could go to [this website](https://randomrijks.com/) which shows you a random artwork from their collection, but that gives you about a 1/500.000 chance each time you request a new artwork. Not ideal. You also can go to [Rijksstudio](https://www.rijksmuseum.nl/nl/rijksstudio) and see if you can find the paiting by keyword or even color, but what if that doesn't work? Wouldn't it be great if you could just normal language, much like asking ChatGPT a question, to find what you are looking for? That is exactly what we thought!

# How does it work?

The art search leverages [CLIP](https://huggingface.co/docs/transformers/model_doc/clip) to map images and texts to vectors in a shared embedding space. 
To visualize this embedding space, we use [PCA](https://en.wikipedia.org/wiki/Principal_component_analysis) to project down from CLIP's 512 dimensions to 2 dimensions (x, y) for visualization of the embedding space.

### Embedding pipeline
A pipeline was created to extract all metadata of images from the [Rijksmuseum API](https://data.rijksmuseum.nl/docs/api/), to fetch the images, embed them with CLIP, and save the embedding vectors in a vector database (we used [pgvector](https://github.com/pgvector/pgvector)).
This process was sped up by fetching images async, and preventing Python from blocking during embedding using multithreading. Multiprocessing was used to divide the task among several Python processing, speeding up the embedding further and making more efficient use of our compute (we used [runpod](https://www.runpod.io/)'s serverless GPU workers). 

![image](/images/projects/art-search/sem-art-etl-drawing.png)

### Backend

The backend is [FastAPI](https://fastapi.tiangolo.com/). It has the CLIP text model loaded in memory and embeds incoming text queries on CPU.
Check out the [backend docs](https://backend.artexplorer.ai/docs) for the openAPI spec.
#### Text-to-image search
When a user text query comes in, we simply embed it using the CLIP text model, and find the top-k nearest neighbors using `pgvector`.
We pass the embeddings through our fitted PCA, which projects the embeddings down to (x, y), which the frontend uses to position the artwork.

#### Image-to-image search

The user passes us a unique `id` of an artwork. We use this to find the embedding of that artwork, and the top-k closest artworks. We again use PCA to obtain (x, y) for each artwork, and return all data.



### Frontend
We have a simple [Nuxt](https://nuxt.com/) frontend. We use [pixi.js](https://pixijs.com/) for rendering of all the images and animations, and [pixi-viewport](https://github.com/pixi-viewport/pixi-viewport)
as a viewport to allow scrolling, zooming and all that good stuff.
We chose `pixi.js` as it comes with niceties out of the box, such as hardware acceleration, an animation framework and a mature ecosystem.

When new artworks come in, we plot them in the pixi canvas, at point:

```javascript
(x * WORLD_WIDTH, y * WORLD_HEIGTH)
```

The image is loaded from the metadata `image_url`, which is a URL to the image served by the Google CDN.
To only render images in the current viewport, we adjusted the [pixi-cull](https://github.com/pixi-viewport/pixi-cull) library to be compatible with the latest pixi version.

TODO: Stefan write something here about culling.


### Deployment

For deployment, we chose to experiment with [Dokploy](https://dokploy.com/), a kind of open source alternative to Heroku, Vercel and Netlify.
We deployed this on a [Hetzner](https://www.hetzner.com/) VPS, as their servers are cheap and reliable. 
We end up with a monolith that hosts our postgres database, frontend and backend.
We can decide to scale vertically by increasing to a more performant VPS, or we could add more servers and configure Docker swarm for autoscaling. 
These were considered overkill for our hobby project purposes.



## The Project



### Architecture

General overview of the final architecture. Maybe with a nice excelidraw drawing

### Sourcing images

How did we get the images

### Embedding images

#### The model

#### The pipeline

#### Making the pipeline blazingly fast

##### Multithreading

### The API

### Depolyment

### Making things blazingly fast

Better indicies

## Some examples

## Future plans

Other museums

## Conclusions

