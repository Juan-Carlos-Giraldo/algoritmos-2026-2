# 05. Plan de pruebas

## 1. Estrategia

Las pruebas verifican cada requisito de `02-requisitos.md`. Hay tres niveles:

1. **Unitarias:** validadores, derivación de *d_i*, cada algoritmo por separado.
2. **Contra referencia:** los algoritmos exactos se comparan contra fuerza bruta en instancias aleatorias pequeñas.
3. **De propiedades:** factibilidad, cotas teóricas y reproducibilidad, que deben cumplirse en cualquier instancia.

Todas las instancias aleatorias se generan con semilla fija y se guardan en `pruebas/instancias/`.

## 2. Casos de validación (RF-02)

| Caso | Entrada | Error esperado |
|---|---|---|
| V-01 | `presupuesto: -1` | Presupuesto negativo |
| V-02 | Dos etapas con id `E1` | Id duplicado |
| V-03 | Etapa con `duracion_acelerada: 7` y `tiempo_ejecucion: 5` | Duración acelerada fuera de rango |
| V-04 | Etapa con `duracion_acelerada: -1` | Duración acelerada fuera de rango |
| V-05 | `costo_aceleracion: 2.5` | Valor no entero |
| V-06 | Interacción con `categorias: []` | Categorías vacías |
| V-07 | Interacción usa `"ruido"` no declarada en `categorias` | Categoría desconocida |
| V-08 | Precedencias `[["E1","E2"],["E2","E1"]]` | Ciclo |
| V-09 | Precedencia que referencia `"E9"` | Etapa inexistente |
| V-10 | Ejecución de V1 con una interacción sin `costo_auditoria` | Falta costo |
| V-11 | Categoría declarada que ninguna interacción cubre | Infactible |

## 3. Casos de la Parte I (RF-10 a RF-13)

| Caso | Descripción | Verificación |
|---|---|---|
| C1-01 | `ejemplo_entrada.json` | Resultado igual a fuerza bruta |
| C1-02 | *B* = 0 | Ninguna etapa acelerada; duración = Σ *t_i* |
| C1-03 | *B* ≥ Σ *c_i* | Todas las etapas aceleradas; duración = Σ *ta_i* |
| C1-04 | *d_i* = 0 para una etapa | Esa etapa nunca se acelera de forma útil |
| C1-05 | Instancias aleatorias con *n* ≤ 12, *B* ≤ 30, 200 casos | Igualdad con fuerza bruta en los 200 |
| C1-06 | Reconstrucción | Σ *c_i* de las aceleradas ≤ *B*, y Σ *d_i* coincide con DP[*n*][*B*] |
| C1-07 | Consulta de la fila final | Para cada *b* ≤ *B*, el valor coincide con fuerza bruta con presupuesto *b* |
| C1-08 | Rendimiento | Tiempo y memoria crecen de forma lineal en *n* y en *B* |

## 4. Casos de la Parte II (RF-20 a RF-24)

| Caso | Descripción | Verificación |
|---|---|---|
| C2-01 | Factibilidad | Instancias infactibles producen V-11 antes de ejecutar |
| C2-02 | Voraz no ponderado, instancias aleatorias | Cubre todas las categorías y pasos ≤ min(*n*, *r*) |
| C2-03 | Razón del voraz no ponderado | Razón ≤ H(*d*) en 200 instancias aleatorias con *n* ≤ 15 |
| C2-04 | Caso de contraejemplo del voraz | Instancia donde el voraz no es óptimo, documentada |
| C2-05 | Voraz ponderado | Costo ≤ H(*d*) · óptimo ponderado en 200 instancias |
| C2-06 | Empates | Dos ejecuciones con la misma entrada dan la misma salida |
| C2-07 | Complejidad | Tiempo medido crece dentro del factor O(min(*n*, *r*) · *n* · *r*) |

## 5. Caso conjunto y DAG (RF-30 a RF-35)

| Caso | Descripción | Verificación |
|---|---|---|
| C3-01 | Caso conjunto exacto | Igual a fuerza bruta conjunta en 100 instancias con *n* ≤ 8 |
| C3-02 | *a** > *B* | Reporta infactible |
| C3-03 | Heurístico conjunto | Costo total ≤ *B*; pérdida de reducción reportada |
| C3-04 | Mejora local | Resultado factible y ≥ solución inicial |
| C3-05 | Recocido simulado | Factible; misma semilla da la misma salida |
| C3-06 | Duración del DAG | Igual a cálculo manual en 5 instancias pequeñas |
| C3-07 | DAG exacto | Igual a fuerza bruta en 50 instancias con *n* ≤ 8 |
| C3-08 | DAG heurístico | Factible; existe al menos una instancia donde no es óptima (C3-08 documentado) |
| C3-09 | Tabla comparativa | Incluye todas las columnas de RF-35 para cada método |

## 6. Propiedades transversales

- **P-01 Factibilidad:** toda solución factible cumple Σ costos ≤ *B*.
- **P-02 Cobertura:** toda solución de auditoría cubre las *r* categorías.
- **P-03 Reproducibilidad:** misma entrada y semilla, misma salida byte a byte (RNF-03).
- **P-04 Trazabilidad:** toda solución tiene un registro no vacío de decisiones (RNF-04).

## 7. Criterios de aceptación del proyecto

El proyecto se considera terminado cuando:

1. Todos los casos de las secciones 2 a 6 pasan.
2. Las tareas de `04-tareas.md` están cerradas con sus criterios de cierre.
3. La tabla comparativa de RF-35 se genera para `ejemplo_entrada.json` y para al menos cinco instancias aleatorias.
4. Las citas de Karp (1972), Johnson (1974), Chvátal (1979) y De et al. (1997) están en la documentación.
