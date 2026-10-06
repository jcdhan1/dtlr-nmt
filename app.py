import argparse
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import argostranslate.package
import argostranslate.translate
import argostranslate.sbd
import stanza

app = Flask(__name__)


def configure_cors(app):
    environment = os.environ.get("APP_ENV", "development").strip().lower()

    if environment == "production":
        allowed_origins = [
            origin.strip()
            for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
            if origin.strip()
        ]
        if not allowed_origins:
            raise RuntimeError(
                "ALLOWED_ORIGINS must contain at least one origin when APP_ENV=production"
            )
    elif environment == "development":
        # Allows local frontends, including a Windows frontend calling the WSL backend.
        allowed_origins = "*"
    else:
        raise RuntimeError("APP_ENV must be either 'development' or 'production'")

    CORS(app, resources={r"/*": {"origins": allowed_origins}})


configure_cors(app)

@app.after_request
def set_referrer_policy(response):
    environment = os.environ.get("APP_ENV", "development").strip().lower()
    
    if environment == "production":
        response.headers['Referrer-Policy'] = 'no-referrer'
    elif environment == "development":
        response.headers['Referrer-Policy'] = 'unsafe-url'  # Full URL for debugging
    
    return response

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

def load_local_models(reinstall_models=False):
    if reinstall_models or not argostranslate.package.get_installed_packages():
        if os.path.exists(MODELS_DIR):
            for file in os.listdir(MODELS_DIR):
                if file.endswith(".argosmodel"):
                    model_path = os.path.join(MODELS_DIR, file)
                    print(f"Installing custom model: {model_path}")
                    argostranslate.package.install_from_path(model_path)
    print("Model initialisation complete.")

if __name__ != '__main__':
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reinstall-models",
        action="store_true",
        help="Reinstall models from /models, overwriting any identically named ones.",
    )
    args, _ = parser.parse_known_args()
    load_local_models(reinstall_models=args.reinstall_models)
    # Listen on all network interfaces inside WSL
    app.run(host='0.0.0.0', port=5000)
