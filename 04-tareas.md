# 04. Plan de tareas

Cada tarea indica los requisitos que cubre (ver `02-requisitos.md`) y sus dependencias. Las tareas se ejecutan en el orden de su etapa.

## Etapa 1: aceleración de la cadena (análoga a la mochila)

**Objetivo de la etapa:** Parte I completa, con validación de entrada.

| ID | Tarea | Requisitos | Depende de |
|---|---|---|---|
| T1.1 | Definir los modelos `Etapa`, `Interaccion`, `Entrada` y `Solucion` | RF-01 | — |
| T1.2 | Implementar la carga desde JSON | RF-01 | T1.1 |
| T1.3 | Implementar las validaciones 1 a 8 | RF-02 | T1.2 |
| T1.4 | Derivar *d_i* y verificar 0 ≤ *d_i* ≤ *t_i* | RF-03 | T1.1 |
| T1.5 | Implementar la DP de la cadena con tabla completa | RF-10, RNF-01 | T1.4 |
| T1.6 | Implementar la reconstrucción del conjunto acelerado | RF-11 | T1.5 |
| T1.7 | Exponer la consulta de la fila final para cualquier *b* | RF-12 | T1.5 |
| T1.8 | Implementar la fuerza bruta de la Parte I para verificación | RF-10 | T1.4 |
| T1.9 | Pruebas de la Parte I contra fuerza bruta (*n* ≤ 12) | RF-10, RF-11, RNF-06 | T1.6, T1.8 |
| T1.10 | Documentar la reducción desde Mochila 0/1 y el carácter pseudo-polinomial | Sección 4.2 del documento original | T1.5 |
| T1.11 | Registro de decisiones y exportación a JSON | RNF-04, RNF-05 | T1.6 |

**Criterio de cierre de la etapa 1:** T1.9 pasa en todas las instancias y T1.3 rechaza cada caso inválido de prueba.

## Etapa 2: cobertura mínima de auditoría con algoritmos voraces

**Objetivo de la etapa:** Parte II completa y variante V1.

| ID | Tarea | Requisitos | Depende de |
|---|---|---|---|
| T2.1 | Implementar la validación 9 (factibilidad) en O(*n* · *r*) | RF-20 | T1.2 |
| T2.2 | Implementar el voraz no ponderado con desempate por *id* | RF-21, RNF-03 | T2.1 |
| T2.3 | Implementar la fuerza bruta de cobertura no ponderada (*n* ≤ 20) | RF-22 | T2.1 |
| T2.4 | Calcular H(*d*) y comparar la razón contra el óptimo | RF-23 | T2.2, T2.3 |
| T2.5 | Implementar el voraz ponderado (*a_j* / nuevas_*j*) | RF-24 | T2.1 |
| T2.6 | Implementar la fuerza bruta ponderada y verificar la cota H(*d*) | RF-24 | T2.5 |
| T2.7 | Verificar la complejidad O(min(*n*, *r*) · *n* · *r*) con instancias de tamaño creciente | RNF-02 | T2.2 |
| T2.8 | Documentar la reducción desde Cobertura de Vértices (Karp, 1972) | Proposición 4.3.1 | — |
| T2.9 | Citar Johnson (1974) y Chvátal (1979) en la documentación de H(*d*) | Teorema 4.3.1 y V1 | T2.4 |
| T2.10 | Pruebas de la Parte II contra fuerza bruta | RF-21 a RF-24, RNF-06 | T2.4, T2.6 |

**Criterio de cierre de la etapa 2:** T2.10 pasa y ninguna razón medida supera H(*d*).

## Etapa 3: combinación mediante optimización heurística

**Objetivo de la etapa:** caso conjunto (V2), mejora por optimización, variante DAG (V3) y tabla comparativa.

| ID | Tarea | Requisitos | Depende de |
|---|---|---|---|
| T3.1 | Implementar el reparto de presupuesto con prioridad a la auditoría | RF-30 | T1.5, T2.6 |
| T3.2 | Implementar el método exacto del caso conjunto (*a** y DP con *B* − *a**) | RF-30 | T3.1 |
| T3.3 | Implementar el método heurístico con voraz ponderado | RF-31 | T2.5, T3.1 |
| T3.4 | Medir la pérdida de reducción del heurístico frente al exacto | RF-31, V2 | T3.2, T3.3 |
| T3.5 | Implementar búsqueda local con los cuatro movimientos definidos | RF-32 | T3.3 |
| T3.6 | Implementar recocido simulado sobre los mismos movimientos | RF-32 | T3.5 |
| T3.7 | Fijar semillas y verificar reproducibilidad | RNF-03 | T3.5, T3.6 |
| T3.8 | Implementar la duración del DAG con programación dinámica en orden topológico | RF-33 | T1.1 |
| T3.9 | Implementar la enumeración exacta del DAG (*n* ≤ 15) | RF-34 | T3.8 |
| T3.10 | Implementar la heurística de razón *d_i* / *c_i* sobre la ruta crítica | RF-34 | T3.8 |
| T3.11 | Encontrar y documentar una instancia donde la heurística DAG no es óptima | RF-34 | T3.9, T3.10 |
| T3.12 | Generar la tabla comparativa de calidad y tiempo | RF-35 | T3.4, T3.6, T3.10 |
| T3.13 | Pruebas de integración de todos los métodos | RNF-06 | T3.12 |

**Criterio de cierre de la etapa 3:** T3.13 pasa, la tabla de T3.12 está generada y existe la instancia documentada de T3.11.

## Resumen de cobertura de requisitos

| Requisito | Tareas |
|---|---|
| RF-01 a RF-03 | T1.1, T1.2, T1.4 |
| RF-10 a RF-13 | T1.5 a T1.8 |
| RF-20 a RF-24 | T2.1 a T2.6 |
| RF-30 a RF-35 | T3.1 a T3.12 |
| RNF-01 a RNF-06 | T1.5, T2.7, T3.7, T1.11, T1.9, T3.13 |
