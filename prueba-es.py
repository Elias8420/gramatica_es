import sys
from lexico import ErrorLexicoES
from parser_es import ParserGramatica
from gramaticas_es import (VERSIONES, contar, contar_lexicas, imprimir_gramatica,
                           gramatica_respectivamente, etiquetar_v2)

ORACIONES = [
    # ---- oraciones simples
    ("el gato come el pescado",               True,  1, "simple"),
    ("la niña lee un libro",                  True,  1, "simple"),
    ("yo veo la casa",                        True,  1, "simple"),
    ("ana compra una casa",                   True,  1, "simple"),
    ("los gatos duermen",                     True,  1, "simple"),
    ("nosotros leemos los libros",            True,  1, "simple"),
    ("la gata negra come el pescado",         True,  1, "concordancia ok"),
    ("los niños felices duermen",             True,  1, "concordancia ok"),
    ("una estudiante grande duerme",          True,  1, "género ambiguo"),
    # ---- errores de concordancia
    ("la gato come el pescado",               False, 1, "artículo-sustantivo"),
    ("el gato negra come el pescado",         False, 1, "sustantivo-adjetivo"),
    ("los gatos duerme",                      False, 1, "sujeto-verbo (núm.)"),
    ("yo comes el pescado",                   False, 1, "sujeto-verbo (pers.)"),
    ("las niñas lee el libro",                False, 1, "sujeto-verbo (núm.)"),
    # ---- subordinadas
    ("juan dice que el gato come el pescado", True,  3, "subordinada"),
    ("maría cree que el niño duerme",         True,  3, "subordinada"),
    ("maría dice que juan cree que el niño duerme", True, 3, "recursión"),
    ("juan quiere que el gato venga",         True,  3, "subjuntivo"),
    ("yo quiero que tú vengas",               True,  3, "subjuntivo"),
    ("juan quiere que el niño coma el pescado", True, 3, "subjuntivo"),
    ("yo creo que tú vienes",                 True,  3, "indicativo"),
    ("yo quiero que tú vienes",               False, 3, "modo erróneo"),
    ("yo creo que tú vengas",                 False, 3, "modo erróneo"),
    # ---- modificadores
    ("el gato negro grande come el pescado",  True,  4, "2 adjetivos"),
    ("el niño corre rápidamente",             True,  4, "adverbio"),
    ("el niño come rápidamente",              True,  4, "objeto omitido"),
    ("el niño duerme en la casa",             True,  4, "frase prepos."),
    ("el niño come el pescado en la casa",    True,  4, "ambigüedad PP"),
    ("el niño vio la casa con el telescopio", True,  4, "ambigüedad PP"),
    ("juan dice que el niño duerme lentamente", True, 4, "ambigüedad adv."),
    ("el niño come rápidamente el pescado",   True,  4, "orden libre"),
    # ---- fuera de alcance de esta gramática
    ("comemos el pescado",                    True,  1, "sujeto omitido"),
    ("duermen los gatos",                     True,  1, "orden VS"),
    ("la pequeña niña duerme",                True,  1, "adjetivo antepuesto"),
    ("el gato come la zanahoria",             True,  1, "palabra fuera del léxico"),
    ("ana, luis y pedro son doctora, ingeniero y abogado respectivamente",
                                              True,  1, "dep. cruzadas"),
]


def evaluar(parser, texto):
    try:
        arboles = parser.analizar(texto)
    except ErrorLexicoES:
        return "lexico", 0
    return ("acepta" if arboles else "rechaza"), len(arboles)


def celda(estado, n, real, desde, v):
    if v < desde:
        return "·"
    if estado == "lexico":
        return "léxico"
    acepta = estado == "acepta"
    if acepta == real:
        return "correcto" + (f" ({n} árb.)" if n > 1 else "")
    return "sobre" if acepta else "falta"


def reporte():
    parsers = {v: ParserGramatica(g(), e) for v, (_, g, e) in VERSIONES.items()}

    print("=== 1. Tamaño de cada gramática ===")
    print(f"{'versión':<54}{'reglas':>7}{'no term.':>9}{'preterm.':>9}{'reglas léx.':>12}{'cat. léx.':>10}")
    for v, (nombre, g, e) in VERSIONES.items():
        c = contar(g())
        rl, cl = contar_lexicas(e)
        print(f"{nombre:<54}{c['reglas']:>7}{c['no_terminales']:>9}{c['preterminales']:>9}{rl:>12}{cl:>10}")

    print("\n=== 2. Oraciones frente a cada versión ===")
    print("correcto = decisión correcta | sobre = acepta algo incorrecto | falta = rechaza algo correcto")
    print("· = fenómeno aún fuera de alcance de esa versión | (n árb.) = ambigüedad\n")
    print(f"{'oración':<68}{'fenómeno':<26}{'real':<6}" + "".join(f"{'v'+str(v):<15}" for v in parsers))
    totales = {v: {"ok": 0, "sobre": 0, "falta": 0, "lexico": 0} for v in parsers}
    for texto, real, desde, fen in ORACIONES:
        fila = f"{texto:<68}{fen:<26}{'sí' if real else 'no':<6}"
        for v, p in parsers.items():
            estado, n = evaluar(p, texto)
            c = celda(estado, n, real, desde, v)
            fila += f"{c:<15}"
            if v >= desde:
                clave = ("lexico" if c == "léxico" else "ok" if c.startswith("✅")
                         else "sobre" if "sobre" in c else "falta")
                totales[v][clave] += 1
        print(fila)

    print("\nResumen (solo oraciones dentro del alcance de cada versión):")
    for v, t in totales.items():
        print(f"  v{v}: {t['ok']} correctas | {t['sobre']} aceptadas de más | "
              f"{t['falta']} rechazadas de más | {t['lexico']} palabra desconocida")

    experimento_respectivamente()


def experimento_respectivamente():
    print("\n=== 3. 'respectivamente': dependencias cruzadas ===")
    print("Una regla por cada longitud n y por cada combinación de géneros (2^n).\n")
    frases = [
        ("n=2", "ana y luis son doctora y abogado respectivamente", True),
        ("n=3", "ana, luis y pedro son doctora, ingeniero y abogado respectivamente", True),
        ("n=3 (género roto)", "ana, luis y pedro son doctora, ingeniera y abogado respectivamente", False),
        ("n=4", "ana, luis, pedro y maría son doctora, ingeniero, abogado y doctora respectivamente", True),
    ]
    print(f"{'gramática hecha para':<22}{'reglas':>7}   " + "   ".join(f"{f[0]:<18}" for f in frases))
    for n_max in (2, 3, 4, 5):
        R = gramatica_respectivamente(n_max)
        p = ParserGramatica(R, etiquetar_v2)
        celdas = []
        for _, texto, real in frases:
            estado, _ = evaluar(p, texto)
            acepta = estado == "acepta"
            celdas.append(("acepta" if acepta else "rechaza"))
        print(f"{'n ≤ ' + str(n_max):<22}{contar(R)['reglas']:>7}   " + "   ".join(f"{c:<18}" for c in celdas))


def main():
    args = sys.argv[1:]
    if not args:
        return reporte()
    if args[0] == "gramatica":
        v = int(args[1].lstrip("v"))
        return imprimir_gramatica(VERSIONES[v][1]())
    v = int(args[0].lstrip("v"))
    texto = " ".join(args[1:])
    parser = ParserGramatica(VERSIONES[v][1](), VERSIONES[v][2])
    try:
        arboles = parser.analizar(texto)
    except ErrorLexicoES as e:
        return print(f"Error léxico: {e}")
    if not arboles:
        return print(f"Rechazada por la versión {v}: {parser.diagnostico()}")
    print(f"✅ Aceptada por la versión {v}: {len(arboles)} árbol(es)\n")
    for i, a in enumerate(arboles, 1):
        print(f"--- árbol {i} ---")
        a.imprimir()


if __name__ == "__main__":
    main()