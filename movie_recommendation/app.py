from flask import Flask, request, render_template
import pickle

app = Flask(__name__)

# Load saved models and data
new_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def recommend(movie):
    movie = movie.lower().strip().replace(" ", "")
    movie_index = new_df[new_df['title'].str.lower().str.replace(" ", "") == movie].index
    if len(movie_index) == 0:
        return []
    movie_index = movie_index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    return [new_df.iloc[i[0]].title for i in movies_list]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie = request.form['movie']
        recommendations = recommend(movie)
        return render_template('index.html', movie=movie, recommendations=recommendations)
    return render_template('index.html', movie=None, recommendations=None)

if __name__ == '__main__':
    app.run(debug=True)
