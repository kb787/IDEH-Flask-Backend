from flask import Blueprint, request, jsonify
from app.modules.web_application.methods.prompt_methods import PromptService

prompt_bp = Blueprint("prompt", __name__)
processor = PromptService()


@prompt_bp.route("/generate-prompt", methods=["POST"])
def generate_prompt():
    data = request.json
    url = data.get("url")
    user_prompt = data.get("prompt")

    if not url or not user_prompt:
        return jsonify({"error": "URL and prompt are required"}), 400

    try:
        result = processor.process_prompt(url, user_prompt)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
