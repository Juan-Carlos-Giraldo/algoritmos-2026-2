import argparse
import json
import sys
from pathlib import Path

from .cargador_validador import EntradaInvalidaError, cargar_entrada
from .cadena_dp import CadenaDP, brute_force_best
from .demo import generar_ejemplos


def _parse_args():
    parser = argparse.ArgumentParser(description="Subproyecto 3 - Etapa 1")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    validar = subparsers.add_parser("validar", help="Valida una entrada JSON")
    validar.add_argument("entrada", help="Ruta al archivo JSON")

    cadena = subparsers.add_parser("cadena", help="Resuelve la Parte I")
    cadena.add_argument("entrada", help="Ruta al archivo JSON")
    cadena.add_argument("--comparar-fuerza-bruta", action="store_true", help="Muestra la verificación por fuerza bruta")
    cadena.add_argument("--salida", help="Carpeta donde guardar la respuesta JSON")

    ejemplos = subparsers.add_parser("generar-ejemplos", help="Crea ejemplos, resultados JSON e informe HTML")
    ejemplos.add_argument("--salida", default="salidas", help="Carpeta de salida (por defecto: salidas)")

    return parser.parse_args()


def _main():
    args = _parse_args()
    if args.comando == "generar-ejemplos":
        archivos = generar_ejemplos(args.salida)
        print(f"Se generaron {len(archivos)} archivos en {Path(args.salida).resolve()}:")
        for archivo in archivos:
            print(f"- {archivo}")
        return

    try:
        entrada = cargar_entrada(args.entrada)
    except EntradaInvalidaError as exc:
        print(f"ERROR: {exc.campo}: {exc.motivo}", file=sys.stderr)
        raise SystemExit(1)

    if args.comando == "validar":
        print(json.dumps({"valida": True, "presupuesto": entrada.presupuesto, "etapas": len(entrada.etapas)}, indent=2))
        return

    if args.comando == "cadena":
        solucion = CadenaDP(entrada)
        tabla = solucion.tabla_dp()
        seleccionadas, reduccion, fila_final = solucion.reconstruir(tabla)
        resultado = {
            "presupuesto": entrada.presupuesto,
            "etapas_aceleradas": seleccionadas,
            "reduccion_maxima": reduccion,
            "duracion_total": solucion.duracion_total(seleccionadas),
            "fila_final": fila_final,
            "tabla_dp": tabla,
        }
        if args.comparar_fuerza_bruta:
            resultado["verificacion_fuerza_bruta"] = brute_force_best(entrada)
        if args.salida:
            carpeta_salida = Path(args.salida)
            carpeta_salida.mkdir(parents=True, exist_ok=True)
            archivo_salida = carpeta_salida / f"resultado_{Path(args.entrada).stem}.json"
            archivo_salida.write_text(
                json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            resultado["archivo_guardado"] = str(archivo_salida)
        print(json.dumps(resultado, indent=2))
        return

    raise SystemExit(2)


if __name__ == "__main__":
    _main()
