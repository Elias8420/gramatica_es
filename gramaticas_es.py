from itertools import product
from lexico import LEXICO

GN = [("m", "s"), ("m", "p"), ("f", "s"), ("f", "p")]     # género + número
PN = ["1s", "2s", "3s", "1p", "3p"]                       # persona + número


# ---------------------------------------------------------------- etiquetas
def etiquetar_v1(a):
    """Sin rasgos: solo la categoría (y la subcategoría del verbo)."""
    if a["cat"] == "V":
        return "V" + a["sub"]          # Vt, Vi, Vci, Vcs (el modo se ignora)
    return a["cat"]


def etiquetar_v2(a):
    """Con rasgos: la etiqueta incluye género, número, persona y modo."""
    c = a["cat"]
    if c in ("Det", "N", "Adj"):
        return f"{c}_{a['gen']}{a['num']}"
    if c in ("NP", "Prof"):
        return f"{c}_{a['gen']}"
    if c in ("Pron", "Ser"):
        return f"{c}_{a['pers']}{a['num']}"
    if c == "V":
        et = f"V{a['sub']}_{a['pers']}{a['num']}"
        return et + "_subj" if a["modo"] == "subj" else et
    return c


# ---------------------------------------------------------------- versiones
def gramatica_v1():
    return {
        "O":   [("SNs", "SV")],
        "SNs": [("SN",), ("Pron",)],
        "SN":  [("Det", "N"), ("Det", "N", "Adj"), ("NP",)],
        "SV":  [("Vi",), ("Vt", "SN"), ("Vt", "A", "SN")],
    }


def gramatica_v2():
    R = {}
    R["O"] = [(f"SNs_{pn}", f"SV_{pn}") for pn in PN]
    R["SNs_3s"] = [("SN_ms",), ("SN_fs",), ("Pron_3s",)]
    R["SNs_3p"] = [("SN_mp",), ("SN_fp",), ("Pron_3p",)]
    for pn in ("1s", "2s", "1p"):
        R[f"SNs_{pn}"] = [(f"Pron_{pn}",)]
    for g, n in GN:
        gn = g + n
        R[f"SN_{gn}"] = [(f"Det_{gn}", f"N_{gn}"), (f"Det_{gn}", f"N_{gn}", f"Adj_{gn}")]
    R["SN_ms"].append(("NP_m",))
    R["SN_fs"].append(("NP_f",))
    R["SNo"] = [(f"SN_{g}{n}",) for g, n in GN]          # objeto: cualquier SN
    for pn in PN:
        R[f"SV_{pn}"] = [(f"Vi_{pn}",), (f"Vt_{pn}", "SNo"), (f"Vt_{pn}", "A", "SNo")]
    return R


def gramatica_v3():
    R = gramatica_v2()
    R["Os"] = [(f"SNs_{pn}", f"SVs_{pn}") for pn in PN]   # oración con verbo en subjuntivo
    for pn in PN:
        R[f"SV_{pn}"] += [(f"Vci_{pn}", "Que", "O"),      # dice/cree... que + indicativo
                          (f"Vcs_{pn}", "Que", "Os")]     # quiere/espera... que + subjuntivo
        R[f"SVs_{pn}"] = [(f"Vi_{pn}_subj",), (f"Vt_{pn}_subj", "SNo"),
                          (f"Vt_{pn}_subj", "A", "SNo")]
    return R


def gramatica_v4():
    R = gramatica_v3()
    for g, n in GN:
        gn = g + n
        R[f"SN_{gn}"] = [(f"Det_{gn}", f"N_{gn}"),
                         (f"Det_{gn}", f"N_{gn}", f"ADJS_{gn}"),
                         (f"Det_{gn}", f"N_{gn}", "SP"),
                         (f"Det_{gn}", f"N_{gn}", f"ADJS_{gn}", "SP")]
        R[f"ADJS_{gn}"] = [(f"Adj_{gn}",), (f"Adj_{gn}", f"ADJS_{gn}")]
    R["SN_ms"].append(("NP_m",))
    R["SN_fs"].append(("NP_f",))
    R["SP"] = [("Prep", "SNo")]
    R["MV"] = [(), ("Adv", "MV"), ("SP", "MV")]           # modificadores del verbo
    # Truco para no multiplicar los modificadores por persona: se separa el núcleo
    # verbal (que sí concuerda) de sus modificadores (que no).
    for pn in PN:
        R[f"SVn_{pn}"] = R[f"SV_{pn}"]
        R[f"SV_{pn}"] = [(f"SVn_{pn}", "MV")]
        R[f"SVsn_{pn}"] = R[f"SVs_{pn}"]
        R[f"SVs_{pn}"] = [(f"SVsn_{pn}", "MV")]
    return R


VERSIONES = {
    1: ("v1: CFG simple (sin concordancia)", gramatica_v1, etiquetar_v1),
    2: ("v2: concordancia con no terminales multiplicados", gramatica_v2, etiquetar_v2),
    3: ("v3: + subordinadas con 'que' (modo)", gramatica_v3, etiquetar_v2),
    4: ("v4: + adjetivos, adverbios y frases preposicionales", gramatica_v4, etiquetar_v2),
}


# ---------------------------------------------------------------- experimento
def gramatica_respectivamente(n_max):
    def lista(cat, patron):
        n, seq = len(patron), []
        for i, g in enumerate(patron):
            seq.append(f"{cat}_{g}")
            if i < n - 2:
                seq.append("Coma")
            elif i == n - 2:
                seq.append("Conj")
        return seq

    R = {"O": []}
    for n in range(2, n_max + 1):
        for patron in product("mf", repeat=n):
            R["O"].append(tuple(lista("NP", patron) + ["Ser_3p"] + lista("Prof", patron) + ["Resp"]))
    return R


# ---------------------------------------------------------------- métricas
def contar(reglas):
    preterminales = {s for alts in reglas.values() for alt in alts for s in alt if s not in reglas}
    return {"reglas": sum(len(a) for a in reglas.values()),
            "no_terminales": len(reglas),
            "preterminales": len(preterminales)}


def contar_lexicas(etiquetar):
    """(reglas léxicas, categorías léxicas distintas) que produce el léxico."""
    pares, cats = set(), set()
    for palabra, lecturas in LEXICO.items():
        for a in lecturas:
            e = etiquetar(a)
            if e:
                pares.add((e, palabra))
                cats.add(e)
    return len(pares), len(cats)


def imprimir_gramatica(reglas):
    for nt, alts in reglas.items():
        cuerpo = " | ".join(" ".join(a) if a else "ε" for a in alts)
        print(f"{nt} → {cuerpo}")