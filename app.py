import streamlit as st
import pickle
import pandas as pd
import requests
import kagglehub
import os

# Download dataset from Kaggle (public dataset, no auth needed)
dataset_path = kagglehub.dataset_download("ridatarique/movie-recommendation-system-data")

# Load preprocessed data
new_df = pickle.load(open(os.path.join(dataset_path, "small_movies_all.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(dataset_path, "small_similarity.pkl"), "rb"))

# OMDb API call for posters + IMDb link
def fetch_poster_omdb(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey=8df2f934"
    try:
        data = requests.get(url, timeout=5).json()
        poster = data.get("Poster")
        imdb_id = data.get("imdbID")
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else None
        return poster, imdb_url
    except Exception as e:
        st.error(f"Poster fetch failed: {e}")
        return None, None

def recommend(movie):
    try:
        movie_index = new_df[new_df['Name'] == movie].index[0]
    except IndexError:
        return [], []  # movie not found

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]

    recommended_movie_names = []
    recommended_movie_data = []

    for i in movie_list:
        title = new_df.iloc[i[0]].Name
        poster, imdb_url = fetch_poster_omdb(title)
        recommended_movie_names.append(title)
        recommended_movie_data.append((poster, imdb_url))

    return recommended_movie_names, recommended_movie_data

# Streamlit UI
st.title(":blue[Movie Recommendation Website] :sunglasses:", text_alignment="center")

# Dropdown for movie selection
movie_list = new_df['Name'].values
selected_movie = st.selectbox("Type or select a movie", movie_list)

if st.button("Show Recommendations"):
    st.subheader(f"Recommendations for **{selected_movie}**:")
    recommended_movie_names, recommended_movie_data = recommend(selected_movie)

    if recommended_movie_names:
        cols = st.columns(4)  # display 4 posters per row
        for idx, movie in enumerate(recommended_movie_names):
            poster, imdb_url = recommended_movie_data[idx]
            with cols[idx % 4]:
                st.markdown(f"**{movie}**")
                if poster:
                    if imdb_url:
                        st.markdown(f"[![Poster]({poster})]({imdb_url})", unsafe_allow_html=True)
                    else:
                        st.image(poster)
                else:
                    st.image("https://via.placeholder.com/300x450?text=No+Poster")
    else:
        st.warning("Movie not found. Try another name.")