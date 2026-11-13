from tree import Nodo
from lexico import tokenizar_es


class ParserGramatica:
    def __init__(self, reglas, etiquetar, inicio="O", max_arboles=50):
        self.reglas = reglas
        self.etiquetar = etiquetar      # lectura de una palabra -> etiqueta del preterminal
        self.inicio = inicio
        self.max_arboles = max_arboles

    # ---------- API ----------
    def analizar(self, texto):
        """Devuelve la lista de árboles (vacía si la oración no pertenece al lenguaje)."""
        self.palabras = tokenizar_es(texto)       # puede lanzar ErrorLexicoES
        self.etiquetas = []
        for p in self.palabras:
            etiquetas = {self.etiquetar(a) for a in p.analisis}
            etiquetas.discard(None)
            self.etiquetas.append(etiquetas)
        self.lejos, self.esperados = 0, set()
        n = len(self.palabras)
        arboles = []
        if n == 0:
            return arboles
        for nodo, j in self._derivar(self.inicio, 0):
            if j == n:
                arboles.append(nodo)
                if len(arboles) >= self.max_arboles:
                    break
            else:
                self._fallo(j, "<fin de la oración>")
        return arboles

    def diagnostico(self):
        """Explica hasta dónde llegó el análisis antes de fallar."""
        n = len(self.palabras)
        esp = ", ".join(sorted(self.esperados)[:8])
        if self.esperados == {"<fin de la oración>"}:
            return (f"sobran palabras a partir de la palabra {self.lejos + 1} "
                    f"({self.palabras[self.lejos].texto!r})")
        if self.lejos >= n:
            return f"la oración terminó antes de tiempo; se esperaba: {esp}"
        return (f"falló en la palabra {self.lejos + 1} ({self.palabras[self.lejos].texto!r}); "
                f"se esperaba: {esp}")

    # ---------- núcleo ----------
    def _fallo(self, i, simbolo):
        if i > self.lejos:
            self.lejos, self.esperados = i, {simbolo}
        elif i == self.lejos:
            self.esperados.add(simbolo)

    def _derivar(self, simbolo, i):
        """Genera todos los (nodo, siguiente_posicion) con que 'simbolo' deriva desde i."""
        if simbolo in self.reglas:
            for alternativa in self.reglas[simbolo]:
                for hijos, j in self._secuencia(alternativa, i):
                    if hijos:
                        yield Nodo(simbolo, hijos), j
                    else:
                        yield None, j          # derivación vacía: no se dibuja
        elif i < len(self.palabras) and simbolo in self.etiquetas[i]:
            yield Nodo(simbolo, valor=self.palabras[i].texto), i + 1
        else:
            self._fallo(i, simbolo)

    def _secuencia(self, simbolos, i):
        if not simbolos:
            yield [], i
            return
        for nodo, j in self._derivar(simbolos[0], i):
            for resto, k in self._secuencia(simbolos[1:], j):
                yield ([nodo] if nodo is not None else []) + resto, k