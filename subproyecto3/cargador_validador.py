from __future__ import annotations

import json
from typing import Any, Iterable, List, Sequence, Set

from .models import Entrada, Etapa, Interaccion


class EntradaInvalidaError(ValueError):
    def __init__(self, campo: str, motivo: str):
        super().__init__(f"{campo}: {motivo}")
        self.campo = campo
        self.motivo = motivo


def _assert_entero(valor: Any, campo: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise EntradaInvalidaError(campo, "debe ser un entero")
    return valor


def _validar_no_negativo(valor: Any, campo: str) -> int:
    valor_int = _assert_entero(valor, campo)
    if valor_int < 0:
        raise EntradaInvalidaError(campo, "no puede ser negativo")
    return valor_int


def _derivar_categorias(categorias_decl: Any, interacciones: Sequence[dict]) -> Set[str]:
    if categorias_decl is not None:
        if not isinstance(categorias_decl, list):
            raise EntradaInvalidaError("auditoria.categorias", "debe ser una lista")
        categorias = set()
        for categoria in categorias_decl:
            if not isinstance(categoria, str):
                raise EntradaInvalidaError("auditoria.categorias", "cada categoría debe ser una cadena")
            categorias.add(categoria)
        return categorias

    categorias = set()
    for interaccion in interacciones:
        if not isinstance(interaccion, dict):
            continue
        for categoria in interaccion.get("categorias", []):
            if not isinstance(categoria, str):
                raise EntradaInvalidaError("auditoria.interacciones[].categorias", "cada categoría debe ser una cadena")
            categorias.add(categoria)
    return categorias


def _verificar_factibilidad(categorias_objetivo: Iterable[str], interacciones: Sequence[dict]) -> None:
    categorias_cubiertas = set()
    for interaccion in interacciones:
        if not isinstance(interaccion, dict):
            continue
        categorias = interaccion.get("categorias", [])
        if not isinstance(categorias, list):
            raise EntradaInvalidaError("auditoria.interacciones[].categorias", "debe ser una lista")
        for categoria in categorias:
            categorias_cubiertas.add(categoria)

    faltantes = set(categorias_objetivo) - categorias_cubiertas
    if faltantes:
        faltantes_str = ", ".join(sorted(faltantes))
        raise EntradaInvalidaError("auditoria", f"las categorías {faltantes_str} no están cubiertas por ninguna interacción")


def cargar_entrada(ruta_json: str, require_auditoria_costo: bool = False) -> Entrada:
    with open(ruta_json, "r", encoding="utf-8") as fh:
        try:
            payload = json.load(fh)
        except json.JSONDecodeError as exc:
            raise EntradaInvalidaError("json", f"archivo JSON no válido: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise EntradaInvalidaError("root", "la entrada debe ser un objeto JSON")

    presupuesto = payload.get("presupuesto")
    if presupuesto is None:
        raise EntradaInvalidaError("presupuesto", "es obligatorio")
    presupuesto = _validar_no_negativo(presupuesto, "presupuesto")

    etapas_raw = payload.get("etapas", [])
    if not isinstance(etapas_raw, list):
        raise EntradaInvalidaError("etapas", "debe ser una lista")

    etapas: List[Etapa] = []
    ids_etapas = set()
    for idx, etapa_raw in enumerate(etapas_raw):
        if not isinstance(etapa_raw, dict):
            raise EntradaInvalidaError(f"etapas[{idx}]", "debe ser un objeto")

        eid = etapa_raw.get("id")
        if not isinstance(eid, str):
            raise EntradaInvalidaError(f"etapas[{idx}].id", "debe ser una cadena")
        if eid in ids_etapas:
            raise EntradaInvalidaError(f"etapas[{idx}].id", f"duplicado: {eid}")
        ids_etapas.add(eid)

        t = _validar_no_negativo(etapa_raw.get("tiempo_ejecucion"), f"etapas[{idx}].tiempo_ejecucion")
        c = _validar_no_negativo(etapa_raw.get("costo_aceleracion"), f"etapas[{idx}].costo_aceleracion")
        ta = _validar_no_negativo(etapa_raw.get("duracion_acelerada"), f"etapas[{idx}].duracion_acelerada")
        if ta > t:
            raise EntradaInvalidaError(f"etapas[{idx}].duracion_acelerada", "no puede ser mayor que tiempo_ejecucion")

        etapas.append(Etapa(id=eid, tiempo_ejecucion=t, costo_aceleracion=c, duracion_acelerada=ta))

    precedencias = payload.get("precedencias", [])
    if precedencias is None:
        precedencias = []
    if not isinstance(precedencias, list):
        raise EntradaInvalidaError("precedencias", "debe ser una lista")

    ids_validos = {etapa.id for etapa in etapas}
    visitados = set()
    camino = set()

    def dfs(nodo: str) -> None:
        if nodo in camino:
            raise EntradaInvalidaError("precedencias", "hay un ciclo en el grafo")
        if nodo in visitados:
            return
        if nodo not in ids_validos:
            raise EntradaInvalidaError("precedencias", f"la etapa {nodo} no existe")
        visitados.add(nodo)
        camino.add(nodo)
        for origen, destino in precedencias:
            if origen == nodo:
                if destino not in ids_validos:
                    raise EntradaInvalidaError("precedencias", f"la etapa {destino} no existe")
                dfs(destino)
        camino.remove(nodo)

    for idx, pareja in enumerate(precedencias):
        if not isinstance(pareja, (list, tuple)) or len(pareja) != 2:
            raise EntradaInvalidaError(f"precedencias[{idx}]", "debe ser un par [origen, destino]")
        origen, destino = pareja
        if not isinstance(origen, str) or not isinstance(destino, str):
            raise EntradaInvalidaError(f"precedencias[{idx}]", "cada valor debe ser una cadena")
        if origen not in ids_validos or destino not in ids_validos:
            raise EntradaInvalidaError("precedencias", "referencia una etapa inexistente")
        if origen == destino:
            raise EntradaInvalidaError("precedencias", "no puede haber un ciclo de longitud 1")

    for nodo in ids_validos:
        dfs(nodo)

    auditoria = payload.get("auditoria", {})
    if auditoria is None:
        auditoria = {}
    if not isinstance(auditoria, dict):
        raise EntradaInvalidaError("auditoria", "debe ser un objeto")

    interacciones_raw = auditoria.get("interacciones", [])
    if not isinstance(interacciones_raw, list):
        raise EntradaInvalidaError("auditoria.interacciones", "debe ser una lista")

    interacciones: List[Interaccion] = []
    ids_inter = set()
    for idx, interaccion_raw in enumerate(interacciones_raw):
        if not isinstance(interaccion_raw, dict):
            raise EntradaInvalidaError(f"auditoria.interacciones[{idx}]", "debe ser un objeto")

        iid = interaccion_raw.get("id")
        if not isinstance(iid, str):
            raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].id", "debe ser una cadena")
        if iid in ids_inter:
            raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].id", f"duplicado: {iid}")
        ids_inter.add(iid)

        categorias = interaccion_raw.get("categorias")
        if not isinstance(categorias, list) or not categorias:
            raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].categorias", "no puede ser vacía")
        cats = set()
        for categoria in categorias:
            if not isinstance(categoria, str):
                raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].categorias", "cada categoría debe ser una cadena")
            cats.add(categoria)

        categorias_decl = auditoria.get("categorias")
        if categorias_decl is not None:
            if not isinstance(categorias_decl, list):
                raise EntradaInvalidaError("auditoria.categorias", "debe ser una lista")
            categorias_validas = set()
            for categoria in categorias_decl:
                if not isinstance(categoria, str):
                    raise EntradaInvalidaError("auditoria.categorias", "cada categoría debe ser una cadena")
                categorias_validas.add(categoria)
            faltantes = cats - categorias_validas
            if faltantes:
                faltantes_str = ", ".join(sorted(faltantes))
                raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].categorias", f"categorías no declaradas: {faltantes_str}")

        costo_aud = interaccion_raw.get("costo_auditoria")
        if require_auditoria_costo:
            if costo_aud is None:
                raise EntradaInvalidaError(f"auditoria.interacciones[{idx}].costo_auditoria", "es obligatorio en esta ejecución")
            costo_aud = _validar_no_negativo(costo_aud, f"auditoria.interacciones[{idx}].costo_auditoria")
        elif costo_aud is not None:
            costo_aud = _validar_no_negativo(costo_aud, f"auditoria.interacciones[{idx}].costo_auditoria")

        interacciones.append(Interaccion(id=iid, categorias=frozenset(cats), costo_auditoria=costo_aud))

    categorias_decl = auditoria.get("categorias")
    categorias = _derivar_categorias(categorias_decl, interacciones_raw)
    _verificar_factibilidad(categorias, interacciones_raw)

    return Entrada(
        presupuesto=presupuesto,
        etapas=etapas,
        precedencias=precedencias,
        categorias=categorias,
        interacciones=interacciones,
    )
