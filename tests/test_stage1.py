import json
from pathlib import Path

import pytest

from subproyecto3.cadena_dp import CadenaDP, brute_force_best
from subproyecto3.cargador_validador import EntradaInvalidaError, cargar_entrada
from subproyecto3.demo import generar_ejemplos

ROOT = Path(__file__).resolve().parents[1]


def test_carga_ejemplo_valido():
    entrada = cargar_entrada(str(ROOT / "ejemplo_entrada.json"))
    assert entrada.presupuesto == 10
    assert len(entrada.etapas) == 3
    assert [e.id for e in entrada.etapas] == ["E1", "E2", "E3"]
    assert sum(e.reduccion for e in entrada.etapas) == 3 + 3 + 2


def test_reduccion_y_duracion():
    entrada = cargar_entrada(str(ROOT / "ejemplo_entrada.json"))
    solver = CadenaDP(entrada)
    tabla = solver.tabla_dp()
    assert tabla[-1][-1] == 8
    seleccionadas, reduccion, _ = solver.reconstruir(tabla)
    assert seleccionadas == ["E1", "E2", "E3"]
    assert reduccion == 8
    assert solver.duracion_total(seleccionadas) == 15 - 8


def test_rechaza_entrada_invalida():
    path = ROOT / "tmp_invalid.json"
    payload = {
        "presupuesto": -1,
        "etapas": [{"id": "E1", "tiempo_ejecucion": 4, "costo_aceleracion": 2, "duracion_acelerada": 7}],
        "precedencias": [],
        "auditoria": {"categorias": [], "interacciones": []},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    try:
        with pytest.raises(EntradaInvalidaError):
            cargar_entrada(str(path))
    finally:
        path.unlink(missing_ok=True)


def test_fila_final_coincide_con_cota():
    entrada = cargar_entrada(str(ROOT / "ejemplo_entrada.json"))
    solver = CadenaDP(entrada)
    fila = solver.tabla_dp()[-1]
    assert fila[0] == 0
    assert fila[10] == solver.mejor_reduccion_por_presupuesto(10)
    assert fila[8] <= fila[10]


def test_bruteforce_best_matches_dp_for_small_cases():
    entrada = cargar_entrada(str(ROOT / "ejemplo_entrada.json"))
    brute = brute_force_best(entrada)
    solver = CadenaDP(entrada)
    best = solver.mejor_reduccion_por_presupuesto(entrada.presupuesto)
    assert brute["reduccion"] == best


def test_generar_ejemplos_guarda_entradas_resultados_e_informe(tmp_path):
    archivos = generar_ejemplos(tmp_path)
    assert len(archivos) == 7
    assert {path.name for path in tmp_path.iterdir()} == {
        "ejemplo_03_etapas.json",
        "ejemplo_10_etapas.json",
        "ejemplo_25_etapas.json",
        "resultado_03_etapas.json",
        "resultado_10_etapas.json",
        "resultado_25_etapas.json",
        "informe.html",
    }

    resultado = json.loads((tmp_path / "resultado_25_etapas.json").read_text(encoding="utf-8"))
    assert resultado["exacta"] is True
    assert len(resultado["tabla_dp"]) == 26
    assert len(resultado["etapas_aceleradas"]) <= 25
    assert len(resultado["recorrido_dp"]) == 26
    assert resultado["recorrido_dp"][-1]["fila"] == 0
    assert {
        paso["etapa"]
        for paso in resultado["recorrido_dp"]
        if paso["decision"] == "acelerar"
    } == set(resultado["etapas_aceleradas"])

    informe = (tmp_path / "informe.html").read_text(encoding="utf-8")
    assert "25 etapas" in informe
    assert "path-accelerate" in informe
    assert "path-skip" in informe
    assert "path-start" in informe
    assert "Ver decisiones de la reconstrucción" in informe
