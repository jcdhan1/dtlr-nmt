import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import argostranslate.package
import argostranslate.translate
import argostranslate.sbd
import stanza

app = Flask(__name__)
# Development: Allows a Windows frontend (localhost) to safely call WSL backend
CORS(app, resources={r"/*": {"origins": "*"}})

# Use a Stanza Pipeline object that avoids overwriting a custom model's own stanza/resources.json and allows unknown languages
def custom_lazy_pipeline(self):
    if self.stanza_pipeline is None:
        self.stanza_pipeline = stanza.Pipeline(
            lang=self.stanza_lang_code,
            dir=str(self.pkg.package_path / "stanza"),
            processors="tokenize",
            use_gpu=argostranslate.settings.device == "cuda",
            logging_level="WARNING",
            download_method=stanza.DownloadMethod.NONE,
            allow_unknown_language=True
        )
    return self.stanza_pipeline

argostranslate.sbd.StanzaSentencizer.lazy_pipeline = custom_lazy_pipeline

# Automatically find and install models in the models folder
MODELS_DIR = "models"

def load_local_models():
    if os.path.exists(MODELS_DIR):
        for file in os.listdir(MODELS_DIR):
            if file.endswith(".argosmodel"):
                model_path = os.path.join(MODELS_DIR, file)
                print(f"Installing custom model: {model_path}")
                argostranslate.package.install_from_path(model_path)
    print("Model initialisation complete.")

load_local_models()

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json() or {}
    text = data.get('text', '')
    # Make incoming BCP 47 tags entirely lower-case like Stanza does (e.g. resources.json has "zh-hans" and "zh-hant").
    from_lang = data.get('from', '').lower()
    to_lang = data.get('to', '').lower()

    if not text or not from_lang or not to_lang:
        return jsonify({"error": "Missing required fields: text, from, to"}), 400

    try:
        translated_text = argostranslate.translate.translate(text, from_lang, to_lang)
        return jsonify({
            "translated_text": translated_text,
            "from": from_lang,
            "to": to_lang
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Listen on all network interfaces inside WSL
    app.run(host='0.0.0.0', port=5000)
