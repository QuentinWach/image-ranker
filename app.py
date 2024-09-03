from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import random
import itertools
from elo import TrueSkillRanking
import tkinter as tk
from tkinter import filedialog
import csv
from io import StringIO
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
elo_ranking = TrueSkillRanking()

IMAGE_FOLDER = 'static/images'

def get_image_paths():
    image_paths = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.jfif', '.avif', '.heic', '.heif')):
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
        'image1': '/serve_image?path=' + img1.replace('\\', '/'),
        'image2': '/serve_image?path=' + img2.replace('\\', '/'),
        'progress': {
            'current': current_pair_index,
            'total': len(image_pairs)
        }
    })

@app.route('/serve_image')
def serve_image():
    image_path = request.args.get('path')
    if image_path.startswith('/serve_image'):
        image_path = image_path.split('=', 1)[1]
    file_extension = os.path.splitext(image_path)[1].lower()
    if file_extension == '.webp':
        mimetype = 'image/webp'
    else:
        mimetype = 'image/jpeg'
    return send_file(image_path, mimetype=mimetype)

@app.route('/update_elo', methods=['POST'])
def update_elo():
    data = request.json
    winner = data['winner']
    loser = data['loser']
    elo_ranking.update_rating(winner, loser)
    return jsonify({'success': True})

@app.route('/get_rankings')
def get_rankings():
    try:
        rankings = elo_ranking.get_rankings()
        return jsonify([
            {
                'image': image,
                'elo': rating.mu,
                'uncertainty': rating.sigma,
                'count': elo_ranking.counts.get(image, 0),
                'upvotes': elo_ranking.upvotes.get(image, 0),
                'downvotes': elo_ranking.downvotes.get(image, 0)
            }
            for image, rating in rankings
        ])
    except Exception as e:
        app.logger.error(f"Error in get_rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_progress')
def get_progress():
    return jsonify({
        'current': current_pair_index,
        'total': len(image_pairs)
    })

@app.route('/select_directory', methods=['POST'])
def select_directory():
    try:
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory(master=root)
        root.destroy()
        if directory:
            global IMAGE_FOLDER, elo_ranking, image_pairs, current_pair_index
            IMAGE_FOLDER = directory
            elo_ranking = TrueSkillRanking()  # Reset the ELO rankings
            initialize_image_pairs()
            current_pair_index = 0  # Reset the current pair index
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No directory selected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export_rankings')
def export_rankings():
    app.logger.info("Export rankings route called")
    try:
        rankings = elo_ranking.get_rankings()
        app.logger.info(f"Rankings: {rankings}")
        if not rankings:
            app.logger.warning("No rankings data available")
            return jsonify({'error': 'No rankings data available. Please make some comparisons first.'}), 400

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Image', 'ELO', 'Uncertainty', 'Upvotes', 'Downvotes'])
        for image, rating in rankings:
            writer.writerow([
                os.path.basename(image),
                round(rating.mu, 2),
                round(rating.sigma, 2),
                elo_ranking.upvotes.get(image, 0),
                elo_ranking.downvotes.get(image, 0)
            ])
        
        output.seek(0)
        app.logger.info("CSV data created successfully")
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": "attachment; filename=image_rankings.csv"}
        )
    except Exception as e:
        app.logger.error(f"Error in export_rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_csv')
def test_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Column1', 'Column2'])
    writer.writerow(['Data1', 'Data2'])
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='test.csv'
    )

@app.route('/debug_rankings')
def debug_rankings():
    return jsonify({
        'rankings': elo_ranking.get_rankings(),
        'upvotes': elo_ranking.upvotes,
        'downvotes': elo_ranking.downvotes
    })

if __name__ == '__main__':
    initialize_image_pairs()
    app.run(debug=True)