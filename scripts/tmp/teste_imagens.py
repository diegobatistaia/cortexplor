import requests
from scripts.engine import images
H = {"User-Agent": images.USER_AGENT}
for s in ["Sam Altman", "Jensen Huang", "Mark Zuckerberg"]:
    r = requests.get(images.WIKIPEDIA_API, params={"action": "query", "format": "json", "titles": s, "redirects": 1, "prop": "pageimages", "piprop": "name"}, headers=H).json()
    name = list(r["query"]["pages"].values())[0].get("pageimage")
    r = requests.get(images.COMMONS_API, params={"action": "query", "format": "json", "titles": f"File:{name}", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata"}, headers=H).json()
    for p in r["query"]["pages"].values():
        i = (p.get("imageinfo") or [{}])[0]; m = i.get("extmetadata", {})
        print(s, name, i.get("mime"), i.get("width"), i.get("height"), m.get("LicenseShortName", {}).get("value"))
