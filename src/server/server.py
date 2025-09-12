from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from .auth import require_api_key
from .audio_pack import save_song
from .audio_pack import match_audio_clip
from io import BytesIO
from datetime import datetime
import time

app = Flask(__name__, 
    static_folder='../public',
    template_folder='../public')


results_storage = {} 


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/ping')
def ping():
    return 'Server is running', 200



@app.route('/songs/match', methods=['POST'])
def match_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    audio_data = BytesIO(audio_file.read())
    print(audio_file.filename,audio_file.content_type,audio_data.getbuffer().nbytes)

    result = match_audio_clip(audio_data)

    result_id = datetime.now().strftime("%Y%m%d%H%M%S")
    return jsonify({
        'message': 'Audio matched successfully',
        'result_id': result_id,
        'matches': result
    }), 200


@app.route('/upload')
def upload_page():
    return send_from_directory(app.template_folder, 'upload.html')

# @require_api_key
@app.route('/songs/save', methods=['POST'])
def upload_song():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    song_name = request.form.get('songName')
    
    if audio_file.filename == '' or not song_name:
        return jsonify({'error': 'Missing song name or file'}), 400
    
    audio_data = BytesIO(audio_file.read())
    save_song(audio_data, song_name)
    
    return jsonify({
        'message': 'Song uploaded successfully',
        'song_id': song_name
    }), 200


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


def start():
    app.run(host="0.0.0.0",debug=True, port=80)


if __name__ == '__main__':
    start()