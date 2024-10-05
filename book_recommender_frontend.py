import streamlit as st
import pickle
import pandas as pd
import numpy as np

with open('books_with_tags.pkl', 'rb') as f:
    books_with_tags = pickle.load(f)

with open('similarity_score.pkl', 'rb') as f:
    similarity_score = pickle.load(f)

books_names = books_with_tags['title'].values

def get_min_max_normalization(df, col):
    return (df[col] - df[col].min()) / (df[col].max() - df[col].min())

def recommend(book_name):
  index = books_with_tags[books_with_tags['title'] == book_name].index[0]
  similar_books = similarity_score[index]
  recs = []
  for book in similar_books:
    recs.append(book[0])
  recommendations = books_with_tags.loc[recs]
  similar_scores = [book[1] for book in similar_books]
  recommendations['similarity_score'] = similar_scores

  recommendations['normalized_similarity_score'] = get_min_max_normalization(recommendations, 'similarity_score')
  recommendations['normalized_average_rating'] = get_min_max_normalization(recommendations, 'average_rating')
  recommendations['normalized_ratings_count'] = get_min_max_normalization(recommendations, 'ratings_count')

  weights = {
    'similarity_score': 0.8,
    'average_rating': 0.15,
    'ratings_count': 0.05
  }

  recommendations['weighted_score'] = (recommendations['normalized_similarity_score'] * weights['similarity_score'] +
                                       recommendations['normalized_average_rating'] * weights['average_rating'] +
                                       recommendations['normalized_ratings_count'] * weights['ratings_count'])

  recommendations = recommendations.sort_values(by='weighted_score', ascending=False)  
  return recommendations[1:31]

st.title(":red[NextRead]")
st.subheader(":blue[_Book recommendations_] you will :red[<3]!")
st.page_link("https://github.com/MehalPandkar/next-read-project", label="Check out the source code here.")
selected_book = st.selectbox(
    "",
    books_names,
    placeholder="Search for a book",
    index=None
)

if st.button("Recommend Books", type="primary"):
    if selected_book:
        recommendations = recommend(selected_book)
        
        num_books = len(recommendations)
        num_cols = 5
        rows = num_books // num_cols + (num_books % num_cols > 0)
        
        for row in range(rows):
            cols = st.columns(num_cols)
            for i, col in enumerate(cols):
                book_index = row * num_cols + i
                if book_index < num_books:
                    with col:
                        st.text(recommendations.iloc[book_index]['title'])
                        image_url = recommendations.iloc[book_index]['image_url']
                        target_url = f"https://goodreads.com/book/show/{recommendations.iloc[book_index]['book_id']}"
                        st.markdown(f'<a href="{target_url}" target="_blank"><img src="{image_url}" alt="Clickable Image" style="width:300px;"></a>', unsafe_allow_html=True)   

        