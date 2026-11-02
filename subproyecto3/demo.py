from __future__ import annotations

import html
import json
from pathlib import Path
from typing import List

from .cadena_dp import CadenaDP
from .cargador_validador import cargar_entrada
from .models import Entrada


TAMANOS_EJEMPLO = (3, 10, 25)


def _crear_entrada(numero_etapas: int) -> dict:
    etapas = []
    for i in range(1, numero_etapas + 1):
        tiempo = 8 + (i * 7) % 12
        reduccion = 1 + (i * 5) % tiempo
        etapas.append(
            {
                "id": f"E{i:02}",
                "tiempo_ejecucion": tiempo,
                "costo_aceleracion": 1 + (i * 3) % 8,
                "duracion_acelerada": tiempo - reduccion,
            }
        )

    costo_total = sum(etapa["costo_aceleracion"] for etapa in etapas)
    return {
        "presupuesto": max(1, round(costo_total * 0.42)),
        "etapas": etapas,
        "precedencias": [],
    }


def _render_tabla_dp(tabla: List[List[int]], recorrido: List[dict]) -> str:
    presupuesto = len(tabla[0]) - 1
    encabezado = "".join(f"<th scope=\"col\">{b}</th>" for b in range(presupuesto + 1))
    estados = {(paso["fila"], paso["presupuesto"]): paso for paso in recorrido}
    filas = []
    for i, valores in enumerate(tabla):
        celdas = []
        for b, valor in enumerate(valores):
            paso = estados.get((i, b))
            if paso is None:
                celdas.append(f"<td>{valor}</td>")
                continue
            clase = {
                "acelerar": "path-accelerate",
                "no_acelerar": "path-skip",
                "inicio": "path-start",
            }[paso["decision"]]
            descripcion = paso.get("etapa", "Inicio del recorrido")
            celdas.append(
                f'<td class="{clase}" title="{html.escape(descripcion)}">{valor}</td>'
            )
        filas.append(f"<tr><th scope=\"row\">{i}</th>{''.join(celdas)}</tr>")
    return (
        "<div class=\"table-scroll\"><table class=\"dp-table\">"
        f"<thead><tr><th scope=\"col\">Etapas</th>{encabezado}</tr></thead>"
        f"<tbody>{''.join(filas)}</tbody></table></div>"
    )


def _crear_recorrido_dp(tabla: List[List[int]], entrada: Entrada) -> List[dict]:
    fila = len(entrada.etapas)
    presupuesto = entrada.presupuesto
    recorrido = []
    while fila > 0:
        etapa = entrada.etapas[fila - 1]
        if tabla[fila][presupuesto] != tabla[fila - 1][presupuesto]:
            decision = "acelerar"
            presupuesto_anterior = presupuesto - etapa.costo_aceleracion
        else:
            decision = "no_acelerar"
            presupuesto_anterior = presupuesto
        recorrido.append(
            {
                "fila": fila,
                "presupuesto": presupuesto,
                "decision": decision,
                "etapa": etapa.id,
                "presupuesto_anterior": presupuesto_anterior,
            }
        )
        presupuesto = presupuesto_anterior
        fila -= 1

    recorrido.append(
        {
            "fila": 0,
            "presupuesto": presupuesto,
            "decision": "inicio",
            "etapa": "Inicio",
            "presupuesto_anterior": presupuesto,
        }
    )
    return recorrido


def _render_decisiones(recorrido: List[dict]) -> str:
    pasos = []
    for paso in reversed(recorrido[:-1]):
        decision = "Acelerar" if paso["decision"] == "acelerar" else "No acelerar"
        pasos.append(
            f"<li><strong>{decision} {html.escape(paso['etapa'])}</strong>: "
            f"presupuesto {paso['presupuesto']} → {paso['presupuesto_anterior']}</li>"
        )
    if not pasos:
        return "<p>No hay etapas que procesar.</p>"
    return f"<ol class=\"decisions\">{''.join(pasos)}</ol>"


def _render_reporte(resultados: List[dict]) -> str:
    tarjetas = []
    for resultado in resultados:
        etapas = ", ".join(resultado["etapas_aceleradas"]) or "Ninguna"
        tarjetas.append(
            f"""
            <section class="card">
              <p class="eyebrow">{resultado['numero_etapas']} etapas</p>
              <h2>{html.escape(resultado['nombre'])}</h2>
              <dl class="metrics">
                <div><dt>Presupuesto</dt><dd>{resultado['presupuesto']}</dd></div>
                <div><dt>Costo usado</dt><dd>{resultado['costo_aceleracion']}</dd></div>
                <div><dt>Reducción máxima</dt><dd>{resultado['reduccion_maxima']}</dd></div>
                <div><dt>Duración total</dt><dd>{resultado['duracion_total']}</dd></div>
              </dl>
              <p><strong>Etapas aceleradas:</strong> {html.escape(etapas)}</p>
              <details>
                <summary>Ver decisiones de la reconstrucción</summary>
                <p class="hint">Se recorre la tabla desde la última etapa y el presupuesto máximo hacia la fila cero.</p>
                {_render_decisiones(resultado['recorrido_dp'])}
              </details>
              <details>
                <summary>Ver tabla completa de programación dinámica</summary>
                <p class="hint">Cada celda indica la mejor reducción posible con las primeras etapas y ese presupuesto. Las celdas resaltadas muestran el camino seguido al reconstruir la respuesta.</p>
                <p class="legend"><span class="legend-accelerate">●</span> Etapa acelerada
                <span class="legend-skip">●</span> Etapa no acelerada
                <span class="legend-start">●</span> Inicio del recorrido</p>
                {_render_tabla_dp(resultado['tabla_dp'], resultado['recorrido_dp'])}
              </details>
              <p class="files">Archivos: <code>{html.escape(resultado['archivo_entrada'])}</code> ·
              <code>{html.escape(resultado['archivo_salida'])}</code></p>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resultados de aceleración de etapas</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, Segoe UI, sans-serif; color: #172033; background: #f3f6fb; }}
    body {{ margin: 0; }}
    header {{ padding: 2rem max(1rem, calc((100% - 1100px) / 2)); background: #14213d; color: white; }}
    header p {{ max-width: 720px; line-height: 1.6; color: #dce5f6; }}
    main {{ max-width: 1100px; margin: 1.5rem auto; padding: 0 1rem 2rem; }}
    .card {{ background: white; border: 1px solid #dfe5ef; border-radius: 12px; margin: 1rem 0; padding: 1.25rem; box-shadow: 0 3px 12px #1720330b; }}
    h1 {{ margin: 0; font-size: clamp(1.6rem, 3vw, 2.2rem); }}
    h2 {{ margin: .25rem 0 1rem; }}
    .eyebrow {{ color: #4263a0; text-transform: uppercase; letter-spacing: .08em; font-size: .78rem; font-weight: 700; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: .75rem; }}
    .metrics div {{ background: #f3f6fb; border-radius: 8px; padding: .8rem; }}
    dt {{ font-size: .85rem; color: #53627a; }} dd {{ margin: .25rem 0 0; font-size: 1.35rem; font-weight: 700; }}
    details {{ margin-top: 1rem; }} summary {{ cursor: pointer; color: #234a8a; font-weight: 650; }}
    .hint, .files {{ color: #53627a; font-size: .9rem; }}
    code {{ background: #eef2f8; padding: .15rem .35rem; border-radius: 4px; }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ border-collapse: collapse; font-size: .82rem; }}
    th, td {{ border: 1px solid #dfe5ef; padding: .35rem .5rem; text-align: right; }}
    thead th, tbody th {{ background: #eef2f8; }}
    td.path-accelerate {{ background: #b7efce; color: #104c2b; font-weight: 800; outline: 2px solid #21834a; outline-offset: -2px; }}
    td.path-skip {{ background: #ffedaa; color: #594500; font-weight: 800; outline: 2px solid #c18a00; outline-offset: -2px; }}
    td.path-start {{ background: #cfe0ff; color: #183c78; font-weight: 800; outline: 2px solid #4875c1; outline-offset: -2px; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 1rem; font-size: .9rem; }}
    .legend-accelerate {{ color: #21834a; }} .legend-skip {{ color: #b77c00; }} .legend-start {{ color: #4875c1; }}
    .decisions {{ line-height: 1.8; }}
    footer {{ max-width: 1100px; margin: 0 auto; padding: 0 1rem 2rem; color: #53627a; font-size: .9rem; }}
  </style>
</head>
<body>
  <header>
    <h1>Resultados: aceleración de la cadena</h1>
    <p>La programación dinámica elige las etapas que maximizan la reducción total sin superar el presupuesto. Abre cada tabla para consultar todos los presupuestos.</p>
  </header>
  <main>{''.join(tarjetas)}</main>
  <footer>Generado por <code>python -m subproyecto3 generar-ejemplos</code>. La tabla DP completa también está en cada archivo JSON de resultados.</footer>
</body>
</html>
"""


def generar_ejemplos(directorio_salida: str | Path) -> List[Path]:
    salida = Path(directorio_salida)
    salida.mkdir(parents=True, exist_ok=True)
    resultados: List[dict] = []
    archivos: List[Path] = []

    for numero_etapas in TAMANOS_EJEMPLO:
        nombre = f"ejemplo_{numero_etapas:02}_etapas"
        archivo_entrada = salida / f"{nombre}.json"
        archivo_resultado = salida / f"resultado_{numero_etapas:02}_etapas.json"
        entrada_json = _crear_entrada(numero_etapas)
        archivo_entrada.write_text(
            json.dumps(entrada_json, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        entrada = cargar_entrada(str(archivo_entrada))
        solver = CadenaDP(entrada)
        tabla = solver.tabla_dp()
        aceleradas, reduccion, fila_final = solver.reconstruir(tabla)
        recorrido = _crear_recorrido_dp(tabla, entrada)
        costo = sum(
            etapa.costo_aceleracion
            for etapa in entrada.etapas
            if etapa.id in set(aceleradas)
        )
        resultado = {
            "entrada": archivo_entrada.name,
            "metodo": "programacion_dinamica_0_1",
            "exacta": True,
            "presupuesto": entrada.presupuesto,
            "costo_aceleracion": costo,
            "etapas_aceleradas": aceleradas,
            "reduccion_maxima": reduccion,
            "duracion_total": solver.duracion_total(aceleradas),
            "fila_final": fila_final,
            "tabla_dp": tabla,
            "recorrido_dp": recorrido,
        }
        archivo_resultado.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        resultados.append(
            {
                **resultado,
                "nombre": nombre,
                "numero_etapas": numero_etapas,
                "archivo_entrada": archivo_entrada.name,
                "archivo_salida": archivo_resultado.name,
            }
        )
        archivos.extend((archivo_entrada, archivo_resultado))

    reporte = salida / "informe.html"
    reporte.write_text(_render_reporte(resultados), encoding="utf-8")
    archivos.append(reporte)
    return archivos
