from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import difflib
import os

app = Flask(__name__)

# Load model data
new_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html', movie=None, recommendations=None)

@app.route('/', methods=['POST'])
def index():
    movie = request.form['movie']
    recommendations, matched_title = recommend(movie)
    return render_template('index.html', movie=matched_title or movie, recommendations=recommendations)

@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').lower()
    suggestions = new_df[new_df['title'].str.lower().str.contains(query)]
    titles = suggestions['title'].head(5).tolist()
    return jsonify(titles)

def recommend(movie):
    movie = movie.lower().strip()

    # Partial match
    matches = new_df[new_df['title'].str.lower().str.contains(movie)]
    if not matches.empty:
        matched_title = matches.iloc[0]['title']
    else:
        # Fuzzy match
        close_matches = difflib.get_close_matches(movie, new_df['title'].str.lower(), n=1, cutoff=0.6)
        if not close_matches:
            return [], None
        matched_title = new_df[new_df['title'].str.lower() == close_matches[0]]['title'].values[0]

    movie_index = new_df[new_df['title'] == matched_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_titles = [new_df.iloc[i[0]].title for i in movies_list]

    return recommended_titles, matched_title



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host='0.0.0.0', port=port)


