from flask import Flask, jsonify, request
from pytubefix import YouTube
from pathlib import Path

app = Flask(__name__)

AUDIO_DIR = Path("downloads/audio")
VIDEO_DIR = Path("downloads/video")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/streams", methods=["POST"])
def list_streams():
    """
    Retorna streams disponíveis (áudio e vídeo)
    """
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL não informada"}), 400

    yt = YouTube(url)

    audio_streams = yt.streams.filter(only_audio=True).order_by("abr").desc()
    video_streams = yt.streams.filter(progressive=True, file_extension="mp4")

    return jsonify({
        "title": yt.title,
        "audio": [
            {"index": i, "abr": s.abr, "mime": s.mime_type}
            for i, s in enumerate(audio_streams)
        ],
        "video": [
            {"index": i, "resolution": s.resolution, "mime": s.mime_type}
            for i, s in enumerate(video_streams)
        ]
    })


@app.route("/download/audio", methods=["POST"])
def download_audio():
    data = request.json
    url = data.get("url")
    index = data.get("index", 0)

    if not url:
        return jsonify({"error": "URL não informada"}), 400

    yt = YouTube(url)
    streams = yt.streams.filter(only_audio=True).order_by("abr").desc()

    if not streams:
        return jsonify({"error": "Nenhum áudio disponível"}), 404

    try:
        stream = streams[int(index)]
        file_path = stream.download(
            output_path=AUDIO_DIR,
            filename=stream.default_filename.replace(".mp4", ".mp3")
        )
        return jsonify({
            "message": "Áudio baixado com sucesso",
            "file": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/video", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")
    index = data.get("index", 0)

    if not url:
        return jsonify({"error": "URL não informada"}), 400

    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension="mp4")

    if not streams:
        return jsonify({"error": "Nenhum vídeo disponível"}), 404

    try:
        stream = streams[int(index)]
        file_path = stream.download(output_path=VIDEO_DIR)
        return jsonify({
            "message": "Vídeo baixado com sucesso",
            "file": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
