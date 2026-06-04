import requests
from bs4 import BeautifulSoup


def search_products(query):

    url = "https://html.duckduckgo.com/html/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(
            url,
            data={"q": query + " acheter prix"},
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        banned_words = [
            "meilleur", "top", "comparatif", "guide",
            "avis", "test", "classement", "sélection",
            "comment", "pourquoi", "astuce", "vs"
        ]

        for a in soup.find_all("a", class_="result__a"):

            title = a.get_text(strip=True)
            href = a.get("href")

            if not title or not href:
                continue

            # filtre anti contenu inutile
            if any(word in title.lower() for word in banned_words):
                continue

            results.append({
                "title": title,
                "url": href
            })

        return results[:10]

    except Exception as e:
        print("SEARCH ERROR:", e)
        return []