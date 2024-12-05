# Introducing [artexplorer.ai](https://artexplorer.ai)

A search engine that lets you search through artworks based on a 'vibe', aka the meaning or semantics of a text.
Try it out by going to [artexplorer.ai](https://artexplorer.ai), and searching for a vibe. For example:

> 'A gloomy landscape in the winter',

will give these results:

![result of A gloomy landscape in the winter on artexplorer.ai](/images/projects/art-search/gloomy_landscape.png)


You can also click images to find out more about them, and find more similar images like them.
Images will keep on being added to your screen, until you refresh, which clears the page.

Currently, it supports all public artworks from [Rijksmuseum Amsterdam](https://www.rijksmuseum.nl/en), with the ambition to add art from other open sources at a later moment.
## Background

Imagine this, you just finished your visit to the Amsterdam Rijksmuseum and you want to tell your friends about this amazing piece of art that you saw. It was this beautiful painting of a group of people in a bar, having a great time. However, you don't remember the title... Now what?

You could go to [this website](https://randomrijks.com/) which shows you a random artwork from their collection, but that gives you about a 1/500.000 chance each time you request a new artwork. Not ideal. You also can go to [Rijksstudio](https://www.rijksmuseum.nl/nl/rijksstudio) and see if you can find the paiting by keyword or even color, but what if that doesn't work? Wouldn't it be great if you could just normal language, much like asking ChatGPT a question, to find what you are looking for? That is exactly what we thought!

# How does it work?  🧰

## TLDR;
The art search leverages OpenAI's multi-modal vision and language model [CLIP](https://arxiv.org/abs/2103.00020) to embed images and texts in a shared [embedding space](https://en.wikipedia.org/wiki/Latent_space). 
We scrape the Rijksmuseum API, embed all images with the [CLIPVisionModel](https://huggingface.co/docs/transformers/model_doc/clip#transformers.CLIPVisionModelWithProjection) and store them in Postgres using [pgvector](https://github.com/pgvector/pgvector). 
When a user enters a text query, we embed their query using [CLIPTextModel](https://huggingface.co/docs/transformers/model_doc/clip#transformers.CLIPTextModelWithProjection).
We use this text query embedding to search for the top-k nearest neighbours in our `pgvector` database. Before sending the response, we use [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html#sklearn.decomposition.PCA) to project down the CLIP embeddings from 512 dimensions to 2 dimensions (x, y) for visualization of the embedding space.

The frontend displays the retrieved artworks in their respective places.
The user can now also do image-to-image search with one of the retrieved artworks.

![Training of CLIP](/images/projects/art-search/CLIP_training.png)
*Image taken from [CLIP paper](https://arxiv.org/abs/2103.00020)*



## ETL pipeline  🏗️

![ETL pipeline schematic drawing](/images/projects/art-search/etl-drawing.png)
### 1. API crawling  🕷️
A pipeline was created to extract all metadata of images from the [Rijksmuseum API](https://data.rijksmuseum.nl/docs/api/).

TODO: Stefan write a bit about your journey of writing this extraction and landing upon the XML api and stuff.


### 2. Image embedding  🖼️ → 🤖  →   📊

Now that we have all metadata of the images we want to embed, we need to do four things.

1. Fetch all metadata of artworks without embedding, divide them over n processes.

Then each process:

2. Downloads the images,
3. embeds them using CLIP,
4. stores the embeddings in pgvector,

where each of these steps runs its own thread.


#### Fetching artworks without embeddings  🖼️
Once we start the embedding phase, we do a simple SQL query, where we fetch all artworks that have no embedding yet.
Then we divide these artworks over the total amount of processes n.
We spawn n processes each with their own artworks to embed.

#### Downloading the images ⬇️


Since we have quite a reasonable scale of ~560.000 images, we prefer this to be fast. 
Luckily all images are served via a Google CDN, which is blazingly fast as is.
We considered downloading and saving images to an object storage like S3, but we figured that fetching the images from Google CDN directly is simpler. 
Additionally, the Google CDN allows you to control the resolution of the image by a query parameter.

Consider the following example URL: `https://lh3.googleusercontent.com/ZYQ7IcfJ45yQOPnmhzBkZK2mc2F_e7bUMDgKaY-miSl0f8y3o-Q--H3R81q-2q1cfqFqoDlDgyLDW3OHJqin_ugnB_KRIfZaV-9xX2Y=s0`
Notice how URL ends with `=s0`. This means the image is returned in full original resolution.

![An example artwork, image of a wooden cabinet](https://lh3.googleusercontent.com/ZYQ7IcfJ45yQOPnmhzBkZK2mc2F_e7bUMDgKaY-miSl0f8y3o-Q--H3R81q-2q1cfqFqoDlDgyLDW3OHJqin_ugnB_KRIfZaV-9xX2Y=s0)

We can change this parameter to control the resolution of the image. If we pass `=w400` instead, it will fetch the image rescaled to have width 400 pixels, while keeping the correct aspect ratio:

![An example artwork, image of a wooden cabinet, rescaled](https://lh3.googleusercontent.com/ZYQ7IcfJ45yQOPnmhzBkZK2mc2F_e7bUMDgKaY-miSl0f8y3o-Q--H3R81q-2q1cfqFqoDlDgyLDW3OHJqin_ugnB_KRIfZaV-9xX2Y=w400)

This was very helpful, since we probably need a lower resolution for embedding, than we do for finally displaying the artworks in the frontend.
For embedding, we settled on a resolution of `w1000`.

Downloading of the images runs in its own thread. This is done so the downloading of images doesn't block the embedding of images, or saving of embeddings to database.
The thread is essentially a consumer of `list[tuple[id, image_url]]` and a producer of `list[tuple[id, image]]`. There's no need to persist images to disk, so images always remain in-memory as bytes.

We fetch images [async](https://docs.python.org/3/library/asyncio.html) in batches of a configurable `retrieval_batch_size`, and put these images in a queue. 

#### Embedding the images  🤖

Embedding of the images is done by a thread that consumes items from the queue which is being filled by the image download thread.
This thread thus consumes `list[tuple[id, image]]` and produces `list[tuple[id, embedding]]` by using CLIP.
This is again done in batches, which is configurable by `embedding_batch_size`. 
This thread will thus wait untill at least `embedding_batch_size` id image pairs are in the queue, and then start embedding the images.
The results are put in another queue, which is read by the tread that commits the results to the database.

#### Store embeddings in vector database  🗄️

This thread simply reads each batch out of the previous queue, and commits them to the `pgvector` database.


## Backend  🖥️

The backend is [FastAPI](https://fastapi.tiangolo.com/). It has the CLIP text model loaded in memory and embeds incoming text queries on CPU.
Check out the [backend docs](https://backend.artexplorer.ai/docs) for the openAPI spec.

### TODO: Write about SQLModel and the pgvector python plugin


### Text-to-image search  📜 → 🖼️

When a user text query comes in, we simply embed it using the CLIP text model, and find the top-k nearest neighbors using `pgvector`.
We pass the embeddings through our fitted PCA, which projects the embeddings down to (x, y), which the frontend uses to position the artwork.

### Image-to-image search 🖼️ → 🖼️

The user passes us a unique `id` of an artwork. We use this to find the embedding of that artwork, and the top-k closest artworks. We again use PCA to obtain (x, y) for each artwork, and return all data.

### Performance tuning  🚀
We use the [HSNW](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) index that `pgvector` supports as a vector index.
TODO: Add some stuff about the troubles we had here and how we ended up fixing it.



## Frontend  💻
We have a simple [Nuxt](https://nuxt.com/) frontend. We use [pixi.js](https://pixijs.com/) for rendering of all the images and animations, and [pixi-viewport](https://github.com/pixi-viewport/pixi-viewport)
as a viewport to allow scrolling, zooming and all that good stuff.
We chose `pixi.js` as it comes with niceties out of the box, such as hardware acceleration, an animation framework and a mature ecosystem.

When new artworks come in, we plot them in the pixi canvas, at point:

```javascript
(x * WORLD_WIDTH, y * WORLD_HEIGTH)
```

This works, because the backend scales the (x, y) to be within \[0, 1\], using [min max scaling](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html). 
The image is loaded from the metadata `image_url`, which is a URL to the image served by the Google CDN.
To only render images in the current viewport, we adjusted the [pixi-cull](https://github.com/pixi-viewport/pixi-cull) library to be compatible with the latest pixi version.

TODO: Stefan write something here about culling.


## Deployment  🌐

For deployment, we chose to experiment with [Dokploy](https://dokploy.com/), a kind of open source alternative to Heroku, Vercel and Netlify.
We deployed this on a [Hetzner](https://www.hetzner.com/) VPS, as their servers are cheap and reliable. 
We end up with a monolith that hosts our postgres database, frontend and backend.
We can decide to scale vertically by increasing to a more performant VPS, or we could add more servers and configure Docker swarm for autoscaling. 
These were considered overkill for our hobby project purposes.

TODO: Add more bout nixpacks and stuff with the backend having to spin up the model, zero downtime deployment, etc.

## Total cost 💰

- Hetzner hosting: €7.62/month (also hosts other projects)
- Runpod serverless GPU: $7.33 ~ €6.95 once (includes all test runs)
- [artexplorer.ai](https://artexplorer.ai) domain name on Namecheap: €76.23/year

As you can see, hosting a simple and fun AI application doesn't have to be expensive! Especially if you don't feel the need to buy a fancy .ai domain 😉.


## What we learned  🧑🏻‍🎓

We learned a ton from this project! Both of us had quite some experience with `PostgreSQL`, but we'd never tried to `pgvector` before.
It was fun to see how easily we could now use it as a vector database! 

We also learned a lot about making Python performant, when a lot of IO and compute needs to happen at the same time.
Our approach, where we write code that combines multiprocessing, multithreading and asynchronous IO, is probably not ideal.
While very performant, it ended up being relatively complex. In the future, it might be worth just using many serverless workers, calling each with a `list[tuple[id, image_url]]` to be processed. 
This would prevent the need of doing explicit multiprocessing, making the code less complex and easier to maintain.

TODO: Add more here


## TODO  ✔️

- [ ] Find publicly available art API's to scrape
  - [ ] Write a wrapper for them
  - [ ] Rerun pipeline

- [ ] Use some orchestration tool to trigger extract and embed pipelines.
- [ ] Experiment with other dimension reduction algorithms like [umap](https://umap-learn.readthedocs.io/en/latest/)

