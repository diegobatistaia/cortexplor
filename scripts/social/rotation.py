"""Rodízio de estilos de carrossel: nunca o mesmo estilo duas vezes seguidas."""
import random

STYLES = ["edicao", "terminal", "dossie", "duotone", "jornal", "poster", "cobalto", "meiatinta", "cartao"]


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
