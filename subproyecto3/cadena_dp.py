from __future__ import annotations

from typing import List, Sequence, Tuple

from .models import Entrada


class CadenaDP:
    def __init__(self, entrada: Entrada):
        self.entrada = entrada

    def tabla_dp(self) -> List[List[int]]:
        n = len(self.entrada.etapas)
        B = self.entrada.presupuesto
        dp = [[0 for _ in range(B + 1)] for _ in range(n + 1)]
        for i, etapa in enumerate(self.entrada.etapas, start=1):
            reduccion = etapa.reduccion
            for b in range(B + 1):
                dp[i][b] = dp[i - 1][b]
                if etapa.costo_aceleracion <= b:
                    valor = dp[i - 1][b - etapa.costo_aceleracion] + reduccion
                    if valor > dp[i][b]:
                        dp[i][b] = valor
        return dp

    def mejor_reduccion_por_presupuesto(self, b: int) -> int:
        if b < 0:
            raise ValueError("b debe ser >= 0")
        if b > self.entrada.presupuesto:
            raise ValueError("b no puede ser mayor que el presupuesto de la entrada")
        return self.tabla_dp()[-1][b]

    def reconstruir(self, tabla: List[List[int]] | None = None) -> Tuple[List[str], int, List[int]]:
        if tabla is None:
            tabla = self.tabla_dp()
        B = self.entrada.presupuesto
        n = len(self.entrada.etapas)
        b = B
        seleccionadas: List[str] = []
        for i in range(n, 0, -1):
            etapa = self.entrada.etapas[i - 1]
            if tabla[i][b] != tabla[i - 1][b]:
                seleccionadas.append(etapa.id)
                b -= etapa.costo_aceleracion
        seleccionadas.reverse()
        reduccion = tabla[n][B]
        return seleccionadas, reduccion, [tabla[n][budget] for budget in range(B + 1)]

    def duracion_total(self, etapas_aceleradas: Sequence[str] | None = None) -> int:
        if etapas_aceleradas is None:
            etapas_aceleradas = self.reconstruir()[0]
        aceleradas = set(etapas_aceleradas)
        tiempo_total = sum(e.tiempo_ejecucion for e in self.entrada.etapas)
        reduccion_total = sum(e.reduccion for e in self.entrada.etapas if e.id in aceleradas)
        return tiempo_total - reduccion_total


def brute_force_best(entrada: Entrada):
    mejor_reduccion = -1
    mejor_seleccion: Tuple[str, ...] = tuple()
    mejor_costo = 0
    etapas = entrada.etapas
    n = len(etapas)
    for mask in range(1 << n):
        costo = 0
        reduccion = 0
        seleccion = []
        for i, etapa in enumerate(etapas):
            if (mask >> i) & 1:
                costo += etapa.costo_aceleracion
                reduccion += etapa.reduccion
                seleccion.append(etapa.id)
        if costo <= entrada.presupuesto and reduccion > mejor_reduccion:
            mejor_reduccion = reduccion
            mejor_seleccion = tuple(seleccion)
            mejor_costo = costo
    if mejor_reduccion == -1:
        return {"reduccion": 0, "costo": 0, "etapas": []}
    return {"reduccion": mejor_reduccion, "costo": mejor_costo, "etapas": list(mejor_seleccion)}


def obtener_resultado_cadena(entrada: Entrada) -> dict:
    solucion = CadenaDP(entrada)
    tabla = solucion.tabla_dp()
    seleccionadas, reduccion, fila_final = solucion.reconstruir(tabla)
    return {
        "presupuesto": entrada.presupuesto,
        "etapas_aceleradas": seleccionadas,
        "reduccion_maxima": reduccion,
        "duracion_total": solucion.duracion_total(seleccionadas),
        "tabla_dp": tabla,
        "fila_final": fila_final,
        "verificacion_fuerza_bruta": brute_force_best(entrada),
    }
