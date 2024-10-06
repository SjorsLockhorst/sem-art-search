# sem-art-search

## Data collection

The image and image description data is retrieved using the [Rijksmuseum API](https://data.rijksmuseum.nl/object-metadata/api/#collection-api).

## TODOs

## ML MVP

- [ ] Attempt different dimention reduction algos
- [ ] Tweak PCA further
- [x] Integrate min max scaling into PCA

### UX MVP

- [ ] Find examples for the design of the frontend

  - More clearly explain how to use the app

- [ ] Make images clickable:

  - Popup that shows more info about the object, maybe link to Rijks
  - Allow selecting that image as image for new query

- [ ] Add backend route to allow finding the closest images to an existing Artobject

- [x] Have backend return (x, y) of the user inputted query

- [x] Have frontend display the place of the user query.

### ETL MVP

- [ ] Implement ability to retrieve all images based on artist, for unkown artist based on type

  - Keep in mind the rate limit of the API

- [ ] Make sure that it really works

### Deployment MVP

- [x] Restructure everything
- [x] Dockerize the things
- [ ] Determine what a good place is to init the database on startup
  - Fastapi lifespan
  - Backend Dockerfile
- [ ] Choose a cloud provider, give them your credit card
- [ ] Dabble in SST
