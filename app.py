from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from mistral_service import extract_request, filter_results
from search_service import search_products

app = Flask(__name__)
CORS(app)  # ✅ FIX IMPORTANT "Failed to fetch"


@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# SEARCH (inchangé côté logique)
# -------------------------
@app.route("/api/search", methods=["POST"])
def search():

    data = request.get_json(force=True)  # 🔥 FIX sécurité fetch
    user_input = data.get("query", "")

    try:
        extracted = extract_request(user_input)

        query = extracted.get("query", user_input)

        results = search_products(query)

        filtered = filter_results(user_input, results)

        return jsonify({
            "query": query,
            "budget": extracted.get("budget_max"),
            "results": filtered
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# TRANSLATE (OBLIGATOIRE sinon ton UI casse)
# -------------------------
@app.route("/api/translate", methods=["POST"])
def translate():

    data = request.get_json(force=True)
    text = data.get("text", "")

    # version simple (tu peux upgrader après avec Mistral)
    return jsonify({
        "translated": text
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
