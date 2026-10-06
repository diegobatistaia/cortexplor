import json
from pathlib import Path
from scripts.engine import images
out = Path("teste-saida"); out.mkdir(exist_ok=True)
images.IMG_DIR = out
for s in ["Sam Altman", "Dario Amodei", "Jensen Huang", "The Pentagon", "Donald Trump", "Greg Brockman", "Satya Nadella", "Sundar Pichai", "Mark Zuckerberg", "Elon Musk", "Gavin Newsom", "Demis Hassabis"]:
    try:
        f = images._commons(s); p = images.download(f["url"], s.lower().replace(" ", "-"))
        print("COMMONS", s, "->", json.dumps({k: f.get(k) for k in ("author", "license", "license_url", "source_url")}, ensure_ascii=False), p)
    except Exception as e:
        print("COMMONS", s, "-> ERRO", e)
