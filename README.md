
# NLTK Recommendation

Probar una recomendacion con nltk y tokenización, estoy usando python, sklearn, dask, pandas, numpy, flask, entre otros.

```
docker compose up -d
```
Eso es todo, revisa tu puerto **8000**

## Dockerhub
Tambien tengo el repositorio en Dockerhub
https://hub.docker.com/repository/docker/eddlihuisi/recomendation-nltk-api/general

```
docker pull eddlihuisi/recomendation-nltk-api
```
Primero debes cargar los datos en la ruta
```
/load_data
```
Depués haces la recomendacion deseada "The Avengers"
```
/recommendations/The Avengers
```
![Ejemplo vista de los datos](https://github.com/LihuisiEd/recomendation-nltk/blob/main/img.jpg)

¿Próximo paso?
- Usar el dataset de **25M Movielens**
### Fin.