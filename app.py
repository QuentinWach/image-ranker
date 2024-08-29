from flask import Flask, render_template, request, jsonify
import os
import random
import itertools
from elo import EloRanking

app = Flask(__name__)
elo_ranking = EloRanking()

IMAGE_FOLDER = 'static/images'

def get_image_paths():
    image_paths = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths

image_pairs = []
current_pair_index = 0

def initialize_image_pairs():
    global image_pairs, current_pair_index
    image_paths = get_image_paths()
    image_pairs = list(itertools.combinations(image_paths, 2))
    random.shuffle(image_pairs)
    current_pair_index = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_images')
def get_images():
    global current_pair_index
    if current_pair_index >= len(image_pairs):
        return jsonify({'error': 'All comparisons completed'})
    
    img1, img2 = image_pairs[current_pair_index]
    current_pair_index += 1
    return jsonify({
        'image1': '/' + os.path.relpath(img1).replace('\\', '/'),
        'image2': '/' + os.path.relpath(img2).replace('\\', '/'),
        'progress': {
            'current': current_pair_index,
            'total': len(image_pairs)
        }
    })

@app.route('/update_elo', methods=['POST'])
def update_elo():
    data = request.json
    winner = data['winner']
    loser = data['loser']
    elo_ranking.update_elo(winner, loser)
    return jsonify({'success': True})

@app.route('/get_rankings')
def get_rankings():
    rankings = elo_ranking.get_rankings()
    return jsonify([
        {
            'image': image,
            'elo': elo,
            'count': elo_ranking.counts.get(image, 0),
            'upvotes': elo_ranking.upvotes.get(image, 0),
            'downvotes': elo_ranking.downvotes.get(image, 0)
        }
        for image, elo in rankings
    ])

@app.route('/get_progress')
def get_progress():
    return jsonify({
        'current': current_pair_index,
        'total': len(image_pairs)
    })

if __name__ == '__main__':
    initialize_image_pairs()
    app.run(debug=True)