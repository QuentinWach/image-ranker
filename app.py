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
import threading

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
elo_ranking = TrueSkillRanking()
excluded_images = set()

IMAGE_FOLDER = 'static/images'
image_pairs_lock = threading.Lock()

def get_image_paths():
    image_paths = []
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.jfif', '.avif', '.heic', '.heif')):
                image_path = os.path.join(root, file).replace('\\', '/')
                if image_path not in excluded_images:
                    image_paths.append(image_path)
    random.shuffle(image_paths)
    return image_paths

image_pairs = []
current_pair_index = 0
last_shown_image = None

def initialize_image_pairs(a=False):
    global image_pairs, current_pair_index
    image_paths = get_image_paths()
    n = len(image_paths)
    initial_pairs = []
    for i in range(n):
        pair = (image_paths[i], image_paths[(i+1) % n])
        initial_pairs.append(pair)
    random.shuffle(initial_pairs)
    remaining_pairs = list(itertools.combinations(image_paths, 2))
    remaining_pairs = [pair for pair in remaining_pairs if pair not in initial_pairs]
    image_pairs = initial_pairs + remaining_pairs
    image_pairs = [pair for pair in image_pairs if pair[0] not in excluded_images and pair[1] not in excluded_images]
    random.shuffle(image_pairs[n:])
    current_pair_index = 0

@app.route('/')
def index():
    return render_template('index.html')

def smart_shuffle():
    """
    Reorders the image pairs based on their ELO ratings and comparison counts.

    This function removes the image pairs that have already been compared, 
    retrieves the current ELO rankings and comparison counts, and then 
    sorts the remaining image pairs based on their ELO differences and 
    comparison counts. The image pairs with the smallest ELO differences 
    and comparison counts are placed first in the list.
    """
    global image_pairs
    global current_pair_index
    
    with image_pairs_lock:
        image_pairs = image_pairs[current_pair_index:]
        current_pair_index = 0
        rankings = elo_ranking.get_rankings()
        elo_dict = {image: rating.mu for image, rating in rankings}
        count_dict = {image: elo_ranking.counts.get(image, 0) for image in elo_dict}
        
        def get_elo_difference(pair):
            return abs(elo_dict.get(pair[0], 0) - elo_dict.get(pair[1], 0)) + 0.8 * (count_dict.get(pair[0], 0) + count_dict.get(pair[1], 0))
        
        image_pairs.sort(key=get_elo_difference)
        
@app.route('/smart_shuffle')
def smart_shuffle_route():
    try:
        smart_shuffle()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_images')
def get_images():
    global current_pair_index
    global last_shown_image

    with image_pairs_lock:
        if current_pair_index >= len(image_pairs):
            return jsonify({'error': 'All comparisons completed in get_images'})
        
        img1, img2 = image_pairs[current_pair_index]
        if last_shown_image is not None:
            if img1 == last_shown_image:
                img1, img2 = img2, img1
            elif img2 == last_shown_image:
                pass
        last_shown_image = img1
        current_pair_index += 1
        total_pairs = len(image_pairs)
        completed_pairs = len(elo_ranking.comparison_history)
    return jsonify({
        'image1':  img1,
        'image2':  img2,
        'progress': {
            'current': completed_pairs,
            'total': total_pairs
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
    elo_ranking.update_rating((winner, loser))
    if data.get('exclude_loser', False):
        excluded_images.add(loser)
        # Recalculate image pairs
        initialize_image_pairs()
    return jsonify({'success': True})

@app.route('/remove_image', methods=['POST'])
def remove_image():
    image = request.json['del_img']
    global image_pairs
    image_pairs = [(img1, img2) for img1, img2 in image_pairs if img1!= image and img2!= image]
    elo_ranking.remove_image(image)
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
                'downvotes': elo_ranking.downvotes.get(image, 0),
                'excluded': image in excluded_images
            }
            for image, rating in rankings
        ])
    except Exception as e:
        app.logger.error(f"Error in get_rankings: {str(e)}.")
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
        root.attributes('-topmost', True)
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
    app.logger.info("Export rankings route called.")
    try:
        rankings = elo_ranking.get_rankings()
        app.logger.info(f"Rankings: {rankings}")
        if not rankings:
            app.logger.warning("No rankings data available.")
            return jsonify({'error': 'No rankings data available. Please make some comparisons first.'}), 400

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Image', 'ELO', 'Uncertainty', 'Upvotes', 'Downvotes'])
        for image, rating in rankings:
            writer.writerow([
                image,
                round(rating.mu, 2),
                round(rating.sigma, 2),
                elo_ranking.upvotes.get(image, 0),
                elo_ranking.downvotes.get(image, 0)
            ])
        
        output.seek(0)
        app.logger.info("CSV data created successfully.")
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": "attachment; filename=image_rankings.csv"}
        )
    except Exception as e:
        app.logger.error(f"Error in export_rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export_comparisons')
def export_comparisons():
    app.logger.info("Export comparisons route called.")
    try:
        comparisons = elo_ranking.comparison_history
        app.logger.info(f"Comparisons: {comparisons}")
        if not comparisons:
            app.logger.warning("No comparisons data available.")
            return jsonify({'error': 'No comparisons data available. Please make some comparisons first.'}), 400

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Winner', 'Loser'])
        for winner, loser in comparisons:
            if winner is None:
                writer.writerow(['None', loser])
            else:
                writer.writerow([winner, loser])
        
        output.seek(0)
        app.logger.info("CSV data created successfully.")
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": "attachment; filename=comparisons.csv"}
        )
    except Exception as e:
        app.logger.error(f"Error in export_comparisons: {str(e)}.")
        return jsonify({'error': str(e)}), 500

@app.route('/import_comparison_history', methods=['POST'])
def import_comparison_history():
    global image_pairs
    file = request.files['file']
    append = request.form.get('append', 'false') == 'true'

    reader = csv.reader(file.read().decode('utf-8').splitlines())
    next(reader)  # Skip header row

    if not append:
        elo_ranking.comparison_history = []
        elo_ranking.recalculate_rankings()

    pairs_to_add = set()
    losers_to_remove = set()
    pairs_to_remove = set()
    for row in reader:
        winner, loser = row
        if winner == 'None':  # Handle cases where winner is None
            losers_to_remove.add(loser)
        else:
            pairs_to_add.add((winner, loser))
        # Collect pairs to remove
        pairs_to_remove.add((winner, loser))
        pairs_to_remove.add((loser, winner))

    # Remove losers from image_pairs and elo_ranking
    image_pairs = [(img1, img2) for img1, img2 in image_pairs if img1 not in losers_to_remove and img2 not in losers_to_remove]
    elo_ranking.update_rating(pairs_to_add)
    elo_ranking.remove_image(losers_to_remove)
    
    # Remove duplicate pairs from image_pairs
    image_pairs = [(img1, img2) for img1, img2 in image_pairs if (img1, img2) not in pairs_to_remove]

    return jsonify({'success': True})

@app.route('/exclude_image', methods=['POST'])
def exclude_image():
    global excluded_images
    data = request.json
    excluded_image = data['excluded_image']
    excluded_images.add(excluded_image)
    # Recalculate image pairs
    initialize_image_pairs()
    return jsonify({'success': True})

@app.route('/clear_excluded_images', methods=['POST'])
def clear_excluded_images():
    global excluded_images
    excluded_images.clear()
    # Recalculate image pairs
    initialize_image_pairs()
    return jsonify({'success': True})

if __name__ == '__main__':
    initialize_image_pairs()
    app.run(debug=False)