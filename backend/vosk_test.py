import wave
import json
from vosk import Model, KaldiRecognizer

def test_vosk_model(audio_file, model_path):
    try:
        # Load Vosk model
        print("Loading model...")
        model = Model(model_path)

        # Open the audio file
        wf = wave.open(audio_file, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio file must be mono PCM at 16kHz.")

        # Initialize recognizer
        recognizer = KaldiRecognizer(model, wf.getframerate())

        # Process audio
        print("Transcribing...")
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                print(f"Intermediate result: {result}")
                results.append(result.get("text", ""))
        
        # Final result
        final_result = json.loads(recognizer.FinalResult())
        print(f"Final result: {final_result}")
        results.append(final_result.get("text", ""))

        # Combine results
        transcription = " ".join([r for r in results if r.strip()])
        print(f"Transcription: {transcription}")
        return transcription

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example Usage
audio_file = "uploads/output.wav"  # Replace with your audio file path
model_path = "model/en"  # Replace with your model directory path
transcription = test_vosk_model(audio_file, model_path)
if transcription:
    print("Vosk model is working correctly.")
else:
    print("Vosk model failed to transcribe.")
