# 03. Diseño

## 1. Visión general

El sistema se organiza en módulos independientes que se conectan por una estructura de datos común. Cada módulo corresponde a una etapa del plan.

```
entrada.json
    │
    ▼
[cargador_validador] ──► Entrada (modelo interno)
    │
    ├──► [cadena_dp]          (Parte I, etapa 1)
    │
    ├──► [cobertura]          (Parte II, etapa 2)
    │       ├── voraz_no_ponderado
    │       ├── voraz_ponderado
    │       └── fuerza_bruta   (verificación)
    │
    └──► [conjunto]           (etapa 3)
            ├── exacto (a* + DP con B − a*)
            ├── heuristico (voraz ponderado + DP)
            ├── mejora_local  (búsqueda local / recocido)
            └── dag           (ruta crítica, enumeración, heurística)
                    │
                    ▼
            [reporte] ──► salida.json + tabla comparativa
```

## 2. Modelo interno de datos

### 2.1 Etapa

```
Etapa {
  id: string
  t: int          // tiempo_ejecucion
  c: int          // costo_aceleracion
  ta: int         // duracion_acelerada
  d: int          // derivado: t − ta
}
```

### 2.2 Interacción

```
Interaccion {
  id: string
  categorias: set<string>   // conjunto, sin repetidos
  a: int | null             // costo_auditoria (null si no se requiere)
}
```

### 2.3 Entrada

```
Entrada {
  B: int
  etapas: list<Etapa>            // orden de la cadena
  precedencias: list<(string,string)>  // vacía para la cadena
  categorias: set<string>        // universo, derivado si no se declara
  interacciones: list<Interaccion>
}
```

### 2.4 Solución

```
Solucion {
  metodo: string
  exacta: bool
  etapas_aceleradas: list<string>
  interacciones_auditadas: list<string>
  costo_aceleracion: int
  costo_auditoria: int
  reduccion_total: int
  duracion_total: int
  factible: bool
  registro: list<string>       // decisiones, para trazabilidad (RNF-04)
}
```

## 3. Módulos

### 3.1 `cargador_validador`
- **Entrada:** ruta a un JSON.
- **Salida:** `Entrada` o lista de errores con campo y motivo.
- **Responsabilidad:** validaciones 1 a 9 de `01-entrada-datos.md`. La validación 9 (factibilidad) se hace en O(*n* · *r*).

### 3.2 `cadena_dp` (Parte I)

**Recurrencia.** Sea DP[*i*][*b*] la máxima reducción usando las primeras *i* etapas con presupuesto usado a lo sumo *b*:

- DP[0][*b*] = 0 para todo *b*.
- DP[*i*][*b*] = max(DP[*i*−1][*b*], DP[*i*−1][*b* − *c_i*] + *d_i*) si *c_i* ≤ *b*; si no, DP[*i*−1][*b*].

**Reconstrucción.** Recorrer desde DP[*n*][*B*] hacia atrás: si DP[*i*][*b*] ≠ DP[*i*−1][*b*], la etapa *i* fue acelerada y *b* se reduce en *c_i*.

**Duración total.** Σ *t_i* − DP[*n*][*B*].

**Complejidad.** O(*n* · *B*) en tiempo y memoria. Para recuperar solo la reducción se puede usar un arreglo de una fila, pero la reconstrucción y la consulta de RF-12 requieren la tabla completa.

**Nota de diseño.** La tabla completa ocupa (*n*+1)·(*B*+1) enteros. Para *B* grande conviene advertir al usuario antes de ejecutar, con un umbral configurable.

### 3.3 `cobertura` (Parte II)

**Interfaz común:**

```
cubrir(entrada, ponderado: bool) -> Solucion
```

**`voraz_no_ponderado`:** en cada paso elige la interacción con mayor número de categorías nuevas. Empates: menor *id* lexicográfico, para asegurar reproducibilidad (RNF-03).

**`voraz_ponderado`:** en cada paso elige la interacción con menor *a_j* / nuevas_*j*. Solo considera interacciones con nuevas_*j* > 0. Empates: menor *id*.

**`fuerza_bruta`:** recorre subconjuntos por tamaño creciente y devuelve el primero que cubre todo (no ponderado), o el de menor costo entre todos (ponderado). Límite configurable, por defecto *n* ≤ 20.

**Complejidad del voraz.** Como cada paso cubre al menos una categoría nueva, hay a lo sumo min(*n*, *r*) pasos. Cada paso revisa *n* interacciones con costo O(*r*) por interacción, dando O(min(*n*, *r*) · *n* · *r*).

**Verificación.** `comparador` calcula la razón solución/óptimo y la compara contra H(*d*) = Σ_{k=1}^{*d*} 1/*k*.

### 3.4 `conjunto` (etapa 3)

**`exacto`:**
1. Ejecutar `cobertura(ponderado=True)` por fuerza bruta o por programación exacta para obtener *a**.
2. Si *a** > *B*, devolver infactible.
3. Ejecutar `cadena_dp` con presupuesto *B* − *a**.
4. Combinar: interacciones auditadas del paso 1 y etapas aceleradas del paso 3.

**`heuristico`:** igual que `exacto`, pero en el paso 1 usa `voraz_ponderado`. Factible por construcción si el costo voraz + costo DP ≤ *B*. Como el costo del voraz puede ser mayor que *a**, se verifica: si *a*_voraz > *B*, se reporta infactible.

**`mejora_local`:** parte de la solución de `heuristico` y explora vecindarios. Movimientos:
- Agregar o quitar una interacción auditada.
- Intercambiar una interacción auditada por otra no auditada.
- Acelerar o desacelerar una etapa.

Cada movimiento mantiene la factibilidad (costo total ≤ *B*) y la cobertura. Se acepta si mejora la reducción, y en recocido simulado también con probabilidad exp(−Δ/*T*). Parámetros: número de iteraciones, temperatura inicial y factor de enfriamiento, todos configurables y fijados por semilla.

**`dag`:**
- Duración: ruta más larga con programación dinámica sobre orden topológico, O(*n* + *m*).
- `exacto_dag`: enumeración de subconjuntos, O(2^*n* · (*n* + *m*)). Límite configurable, por defecto *n* ≤ 15.
- `heuristico_dag`: en cada paso recalcula la ruta crítica y entre sus etapas que caben en el presupuesto restante elige la de mayor *d_i* / *c_i*. Costo O(*n* · (*n* + *m*)).

### 3.5 `reporte`
- Genera `salida.json` con la `Solucion` y la tabla comparativa de RF-35.
- Campos de la tabla: método, valor objetivo, costo de aceleración, costo de auditoría, tiempo de ejecución en segundos, exacto (sí/no).

## 4. Reparto del presupuesto en el caso conjunto

El presupuesto *B* se reparte en dos bloques: auditoría (*a*) y aceleración (*B* − *a*). La auditoría es obligatoria, por lo que tiene prioridad: primero se cubre todo, luego se usa lo que sobre. Esto sigue la especificación del documento original.

## 5. Interfaces de línea de comandos

```
subproyecto3 validar entrada.json
subproyecto3 cadena entrada.json
subproyecto3 cobertura entrada.json [--ponderado] [--fuerza-bruta]
subproyecto3 conjunto entrada.json [--metodo exacto|heuristico|mejora]
subproyecto3 dag entrada.json [--metodo exacto|heuristico]
subproyecto3 comparar entrada.json
```

`comparar` ejecuta todos los métodos aplicables y genera la tabla de RF-35.

## 6. Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Entrada en JSON con listas de registros | Separa etapas de interacciones y evita el problema de aristas con significados mezclados (ver `01-entrada-datos.md`, sección 5.2). |
| Desempate por *id* lexicográfico | Reproducibilidad (RNF-03). |
| Factibilidad verificada antes de algoritmos | Evita resultados engañosos sobre instancias sin solución. |
| Tabla DP completa guardada | Permite RF-12 y el análisis de la fila final pedido en V2. |
| Límites configurables para fuerza bruta | Evita tiempos de ejecución excesivos sin cambiar el código. |
| Semilla fija para mejora local | Reproducibilidad con métodos aleatorios. |
