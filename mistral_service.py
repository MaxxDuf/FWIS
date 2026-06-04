from dotenv import load_dotenv
from mistralai import Mistral
import os
import json
import re

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv(dotenv_path=".env", override=True)

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


# -------------------------
# JSON SAFE PARSER
# -------------------------
def extract_json(text):

    if not text:
        raise ValueError("Réponse vide")

    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())

    raise ValueError("JSON invalide")


# -------------------------
# 1. IA → requête optimisée
# -------------------------
def extract_request(user_input):

    prompt = f"""
Tu es un moteur de recherche e-commerce.

Transforme la demande en requête produit optimisée.

Répond uniquement en JSON :

{{
  "query": "requête produit optimisée",
  "category": "type produit",
  "budget_max": null,
  "keywords": [],
  "intent": "gaming|budget|premium|general"
}}

Utilisateur :
{user_input}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    print("DEBUG MISTRAL:", content)

    return extract_json(content)


# -------------------------
# 2. IA → filtre résultats (FIX IMPORTANT)
# -------------------------
def filter_results(user_query, results):

    if not results:
        return []

    prompt = f"""
Tu es un filtre e-commerce.

Objectif :
Garder uniquement les résultats pouvant mener à un PRODUIT ACHETABLE.

Règles :
- Autorisé : Amazon, Fnac, Cdiscount, Boulanger, AliExpress
- Autorisé : pages produit directes
- Autorisé : liens contenant un produit précis
- Interdit : blogs, comparatifs, guides, top 10, articles

IMPORTANT :
Si un lien est ambigu mais semble être un produit → GARDE-LE.

Utilisateur :
{user_query}

Résultats :
"""

    for r in results:
        prompt += f"- {r['title']} | {r['url']}\n"

    prompt += """
Répond uniquement en JSON :

{
  "results": [
    {"title": "...", "url": "..."}
  ]
}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    print("DEBUG FILTER:", content)

    filtered = extract_json(content).get("results", [])

    # -------------------------
    # FALLBACK (IMPORTANT)
    # -------------------------
    if not filtered and results:
        return results[:5]

    return filtered