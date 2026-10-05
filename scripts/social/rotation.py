"""Rodízio de estilos de carrossel: nunca o mesmo estilo duas vezes seguidas."""
import random
from pathlib import Path

STYLES = ["edicao", "terminal", "dossie", "duotone", "jornal", "cobalto", "meiatinta", "cartao"]


PHOTO_MIN_W, PHOTO_MIN_H = 800, 500
DARK_PHOTO = 45  # luminância média (0-255) abaixo da qual a capa em meia-tinta fica ilegível
ROOT = Path(__file__).resolve().parents[2]


def photo_report(spec):
    """Avisos sobre a foto da matéria e estilos que ela exclui: (avisos, excluidos)."""
    from PIL import Image, ImageStat

    im = Image.open(ROOT / spec["image"]["path"])
    warns, excluded = [], []
    if im.width < PHOTO_MIN_W or im.height < PHOTO_MIN_H:
        warns.append(f"foto pequena ({im.width}x{im.height}); mínimo {PHOTO_MIN_W}x{PHOTO_MIN_H}")
    lum = ImageStat.Stat(im.convert("L")).mean[0]
    if lum < DARK_PHOTO:
        excluded.append("meiatinta")
        warns.append(f"foto muito escura (luminância {lum:.0f}); estilo meiatinta fora do rodízio desta matéria")
    return warns, excluded


def eligible_styles(spec):
    """Estilos que podem ser usados nesta matéria (a rotação do dia sorteia só entre eles)."""
    excl = photo_report(spec)[1]
    return [s for s in STYLES if s not in excl]


def pick_styles(n, styles=STYLES, last=None, rng=None):
    """Devolve n estilos em ordem aleatória, sem repetir em sequência.

    Usa "sacolas" embaralhadas com todos os estilos (distribuição equilibrada);
    `last` é o último estilo usado (ex.: do dia anterior) e também não repete.
    """
    rng = rng or random.Random()
    out = []
    prev = last
    while len(out) < n:
        bag = list(styles)
        rng.shuffle(bag)
        if bag[0] == prev:
            k = rng.randrange(1, len(bag))
            bag[0], bag[k] = bag[k], bag[0]
        out.extend(bag)
        prev = out[-1]
    return out[:n]


if __name__ == "__main__":
    for seed in range(5000):
        r = random.Random(seed)
        last = r.choice([None] + STYLES)
        n = r.randint(1, 12)
        s = pick_styles(n, last=last, rng=r)
        assert len(s) == n
        seq = ([last] if last else []) + s
        assert all(a != b for a, b in zip(seq, seq[1:])), (seed, seq)
    print("ok: sem repetição seguida em 5000 sorteios")
    print("exemplo (3 matérias):", pick_styles(3, rng=random.Random(7)))
