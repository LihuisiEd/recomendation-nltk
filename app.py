from flask import Flask, request, jsonify
import pandas as pd 
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
from flask_cors import CORS

nltk.download('punkt')

app = Flask(__name__)
CORS(app)

app.config['DATA_LOADED'] = False
app.config['DF'] = None
app.config['SIMILARITY'] = None

def read_files():
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
    return movies, credits

def merge_data(movies, credits):
    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id','title','genres','cast','overview','keywords','crew']]
    movies.dropna(inplace=True)
    return movies

def transform(obj):
    List = []
    for i in ast.literal_eval(obj):
        List.append(i['name'])
    return List

def transform1(obj):
    List = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            List.append(i['name'])
            counter += 1
        else:
            break
    return List

def fetch_director(text):
    List = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            List.append(i['name'])
    return List 

def apply_transform(movies):
    movies['genres'] = movies['genres'].apply(transform)
    movies['keywords'] = movies['keywords'].apply(transform)
    movies['cast'] = movies['cast'].apply(transform1)
    movies['crew'] = movies['crew'].apply(fetch_director)
    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    return movies

def format_data(movies):
    movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ","") for i in x])
    movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ","") for i in x])
    movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ","") for i in x])
    movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ","") for i in x])
    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'] 
    df = movies[['movie_id','title','tags']]
    df['tags'] = df['tags'].apply(lambda x: " ".join(x))
    df['tags'] = df['tags'].apply(lambda x: x.lower())
    return df

def tokenization(df):
    ps = PorterStemmer()
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(df['tags'])
    feature_names = cv.get_feature_names_out()
    stemmed_feature_names = [" ".join([ps.stem(word) for word in word_tokenize(feature)]) for feature in feature_names]
    unique_stemmed_feature_names = []
    seen = set()
    for feature in stemmed_feature_names:
        if feature not in seen:
            unique_stemmed_feature_names.append(feature)
            seen.add(feature)
    similarity = cosine_similarity(vectors)
    return similarity, df

@app.route("/recommendations/<string:movie_title>", methods=['GET'])
def get_recommendations_for_movie(movie_title):
    if not app.config['DATA_LOADED']:
        return jsonify({'error': 'Data has not been loaded. Call /load_data first.'})

    movie_lower = movie_title.lower()
    df = app.config['DF']
    similarity = app.config['SIMILARITY']

    df['title_lower'] = df['title'].str.lower()
    movie_index1 = df[df['title_lower'] == movie_lower].index

    if not movie_index1.empty:
        movie_index1 = movie_index1[0]
        distances = similarity[movie_index1]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
        recommendations = [df.iloc[i[0]].title for i in movies_list]
        return jsonify({'movie_title': movie_title, 'recommendations': recommendations})
    else:
        return jsonify({'error': 'Movie not found in the dataset.'})


@app.route("/", methods=['POST','GET'])
def hello():
    return jsonify({'message': 'API v1'})

@app.route('/load_data', methods=['GET'])
def load_data():
    if not app.config['DATA_LOADED']:
        movies, credits = read_files()
        movies = merge_data(movies, credits)
        movies = apply_transform(movies)
        df = format_data(movies)
        similarity, df = tokenization(df)
        app.config['DATA_LOADED'] = True
        app.config['DF'] = df
        app.config['SIMILARITY'] = similarity
        return jsonify({'message': 'Data loaded successfully!'})
    else:
        return jsonify({'message': 'Data has already been loaded.'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)