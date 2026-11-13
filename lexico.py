import re
from dataclasses import dataclass
from itertools import product

LEXICO = {}


def _agregar(palabra, **rasgos):
    claves = list(rasgos)
    opciones = [v if isinstance(v, tuple) else (v,) for v in rasgos.values()]
    for combo in product(*opciones):
        LEXICO.setdefault(palabra, []).append(dict(zip(claves, combo)))


# ---------- determinantes ----------
for _p, _g, _n in [("el", "m", "s"), ("la", "f", "s"), ("los", "m", "p"), ("las", "f", "p"),
                   ("un", "m", "s"), ("una", "f", "s"), ("unos", "m", "p"), ("unas", "f", "p")]:
    _agregar(_p, cat="Det", gen=_g, num=_n)


# ---------- sustantivos ----------
def _sust(sing, plur, gen):
    _agregar(sing, cat="N", gen=gen, num="s")
    _agregar(plur, cat="N", gen=gen, num="p")


for _s, _p in [("gato", "gatos"), ("niño", "niños"), ("perro", "perros"), ("libro", "libros"),
               ("pescado", "pescados"), ("hombre", "hombres"), ("parque", "parques"),
               ("telescopio", "telescopios"), ("profesor", "profesores"), ("pájaro", "pájaros")]:
    _sust(_s, _p, "m")
for _s, _p in [("gata", "gatas"), ("niña", "niñas"), ("casa", "casas"), ("mesa", "mesas"),
               ("carta", "cartas"), ("mujer", "mujeres"), ("profesora", "profesoras")]:
    _sust(_s, _p, "f")
_sust("estudiante", "estudiantes", ("m", "f"))      # sustantivo común en cuanto al género

# ---------- adjetivos ----------
for _base in ["negr", "roj", "pequeñ"]:
    for _suf, _g, _n in [("o", "m", "s"), ("a", "f", "s"), ("os", "m", "p"), ("as", "f", "p")]:
        _agregar(_base + _suf, cat="Adj", gen=_g, num=_n)
_agregar("grande", cat="Adj", gen=("m", "f"), num="s")
_agregar("grandes", cat="Adj", gen=("m", "f"), num="p")
_agregar("feliz", cat="Adj", gen=("m", "f"), num="s")
_agregar("felices", cat="Adj", gen=("m", "f"), num="p")

# ---------- adverbios, preposiciones y palabras funcionales ----------
for _p in ["rápidamente", "lentamente", "siempre", "ayer"]:
    _agregar(_p, cat="Adv")
for _p in ["de", "con", "en", "por", "para"]:
    _agregar(_p, cat="Prep")
_agregar("a", cat="A")                 # 'a' personal del objeto directo
_agregar("que", cat="Que")             # conjunción subordinante
_agregar("y", cat="Conj")
_agregar(",", cat="Coma")
_agregar("respectivamente", cat="Resp")

# ---------- pronombres sujeto, nombres propios, profesiones, verbo ser ----------
for _p, _pers, _n in [("yo", 1, "s"), ("tú", 2, "s"), ("él", 3, "s"), ("ella", 3, "s"),
                      ("nosotros", 1, "p"), ("ellos", 3, "p"), ("ellas", 3, "p")]:
    _agregar(_p, cat="Pron", pers=_pers, num=_n)
for _p, _g in [("ana", "f"), ("maría", "f"), ("sofía", "f"),
               ("luis", "m"), ("pedro", "m"), ("juan", "m")]:
    _agregar(_p, cat="NP", gen=_g)
for _p, _g in [("doctor", "m"), ("doctora", "f"), ("ingeniero", "m"), ("ingeniera", "f"),
               ("abogado", "m"), ("abogada", "f")]:
    _agregar(_p, cat="Prof", gen=_g)
_agregar("es", cat="Ser", pers=3, num="s")
_agregar("son", cat="Ser", pers=3, num="p")

# ---------- verbos ----------
PN = [(1, "s"), (2, "s"), (3, "s"), (1, "p"), (3, "p")]   # orden de las formas del presente


def _verbo(lema, sub, pres, pret=None, subj=None):
    for (pers, num), forma in zip(PN, pres):
        _agregar(forma, cat="V", lema=lema, sub=sub, modo="ind", tiempo="pres", pers=pers, num=num)
    for (pers, num), forma in (pret or {}).items():
        _agregar(forma, cat="V", lema=lema, sub=sub, modo="ind", tiempo="pret", pers=pers, num=num)
    if subj:
        for (pers, num), forma in zip(PN, subj):
            _agregar(forma, cat="V", lema=lema, sub=sub, modo="subj", tiempo="pres", pers=pers, num=num)


_verbo("comer", "t", ["como", "comes", "come", "comemos", "comen"],
       {(1, "s"): "comí", (3, "s"): "comió", (3, "p"): "comieron"},
       ["coma", "comas", "coma", "comamos", "coman"])
_verbo("ver", "t", ["veo", "ves", "ve", "vemos", "ven"],
       {(1, "s"): "vi", (3, "s"): "vio", (3, "p"): "vieron"})
_verbo("leer", "t", ["leo", "lees", "lee", "leemos", "leen"])
_verbo("comprar", "t", ["compro", "compras", "compra", "compramos", "compran"],
       {(1, "s"): "compré", (3, "s"): "compró", (3, "p"): "compraron"})
_verbo("mirar", "t", ["miro", "miras", "mira", "miramos", "miran"],
       {(1, "s"): "miré", (3, "s"): "miró", (3, "p"): "miraron"})
_verbo("dormir", "i", ["duermo", "duermes", "duerme", "dormimos", "duermen"])
_verbo("correr", "i", ["corro", "corres", "corre", "corremos", "corren"])
_verbo("llegar", "i", ["llego", "llegas", "llega", "llegamos", "llegan"],
       {(1, "s"): "llegué", (3, "s"): "llegó", (3, "p"): "llegaron"},
       ["llegue", "llegues", "llegue", "lleguemos", "lleguen"])
_verbo("venir", "i", ["vengo", "vienes", "viene", "venimos", "vienen"],
       None, ["venga", "vengas", "venga", "vengamos", "vengan"])
_verbo("decir", "ci", ["digo", "dices", "dice", "decimos", "dicen"])
_verbo("creer", "ci", ["creo", "crees", "cree", "creemos", "creen"])
_verbo("saber", "ci", ["sé", "sabes", "sabe", "sabemos", "saben"])
_verbo("pensar", "ci", ["pienso", "piensas", "piensa", "pensamos", "piensan"])
_verbo("querer", "cs", ["quiero", "quieres", "quiere", "queremos", "quieren"])
_verbo("esperar", "cs", ["espero", "esperas", "espera", "esperamos", "esperan"])


# ---------- el "lexer" del español ----------
class ErrorLexicoES(Exception):
    pass


@dataclass
class Palabra:
    texto: str
    analisis: list      # lista de lecturas (dicts de rasgos)


def tokenizar_es(texto):
    t = texto.lower()
    # Hack léxico: las contracciones 'al' y 'del' se separan (a el, de el).
    t = re.sub(r"\bal\b", "a el", t)
    t = re.sub(r"\bdel\b", "de el", t)
    palabras = re.findall(r"[a-záéíóúüñ]+|,", t)
    resultado = []
    for p in palabras:
        if p not in LEXICO:
            raise ErrorLexicoES(f"palabra desconocida: {p!r}")
        resultado.append(Palabra(p, LEXICO[p]))
    return resultado