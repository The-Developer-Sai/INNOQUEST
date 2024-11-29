import os
from flask import Flask, request, jsonify, render_template
from vosk import Model, KaldiRecognizer
import wave
import subprocess
import json

app = Flask(__name__)

# Directory for uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Vosk models dynamically
models = {}
available_languages = ["en", "hi", "ru", "cn", "nl"]

def get_model(language_code):
    """
    Load the Vosk model for the specified language.
    """
    if language_code not in models:
        model_path = f"model/{language_code}/"
        if os.path.exists(model_path):
            models[language_code] = Model(model_path)
        else:
            raise RuntimeError(f"Model for language '{language_code}' not found.")
    return models[language_code]

def extract_audio(file_path, output_path):
    """
    Convert audio or video to 16kHz mono WAV format using FFmpeg.
    """
    temp_output = os.path.splitext(output_path)[0] + "_temp.wav"
    
    # Ensure the input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file '{file_path}' not found.")
    
    # Remove existing files
    if os.path.exists(temp_output):
        os.remove(temp_output)
    if os.path.exists(output_path):
        os.remove(output_path)

    # Convert audio to WAV
    command = [
        "ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-f", "wav", temp_output, "-y"
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        os.rename(temp_output, output_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode()}")

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Audio for Transcription</title>
    </head>
    <body>
        <h1>Audio Transcription Service</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label for="file">Choose an audio file:</label><br><br>
            <input type="file" name="file" required><br><br>
            <label for="language">Language (en, hi, ru, cn, nl):</label><br><br>
            <input type="text" name="language" required><br><br>
            <button type="submit">Transcribe</button>
        </form>
    </body>
    </html>
    """

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handle file upload, audio conversion, and transcription.
    """
    try:
        if "file" not in request.files:
            return "Error: No file part in the request.", 400
        if "language" not in request.form:
            return "Error: No language specified.", 400

        language = request.form["language"]
        if language not in available_languages:
            return f"Error: Language '{language}' not supported.", 400

        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return "Error: No file selected.", 400

        # Save uploaded file
        input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        audio_path = os.path.splitext(input_path)[0] + ".wav"
        uploaded_file.save(input_path)

        # Convert to WAV format
        extract_audio(input_path, audio_path)
        if not os.path.exists(audio_path):
            return "Error: Converted audio file not found.", 500

        # Perform transcription
        model = get_model(language)
        recognizer = KaldiRecognizer(model, 16000)

        with wave.open(audio_path, "rb") as wf:
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    results.append(json.loads(result).get("text", ""))
                else:
                    recognizer.PartialResult()

        # Handle final result
        final_result = recognizer.FinalResult()
        final_text = json.loads(final_result).get("text", "").strip() if final_result else ""
        if final_text:
            results.append(final_text)

        # Aggregate results
        transcription = " ".join([r for r in results if r.strip()]).strip()
        if not transcription:
            return "Error: Transcription failed or returned empty output.", 500

        # Return transcription on HTML page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transcription Result</title>
        </head>
        <body>
            <h1>Transcription Result</h1>
            <p>{transcription}</p>
            <a href="/">Go back</a>
        </body>
        </html>
        """

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
