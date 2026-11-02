# Subproyecto 3: Ruta crítica con aceleración bajo presupuesto y cobertura mínima de auditoría

## Contexto general

Un flujo de trabajo procesa cada solicitud a través de una cadena de *n* etapas en serie. Cada etapa *i* tiene una duración normal *t_i* y puede acelerarse a un costo *c_i*, reduciendo su duración en *d_i* unidades de tiempo (con 0 ≤ *d_i* ≤ *t_i*). Hay un presupuesto total *B* para acelerar etapas.

Por separado, cada solicitud puede requerir una revisión de cumplimiento normativo a fondo. Como revisar todas es demasiado costoso, solo se audita un subconjunto de interacciones.

El subproyecto tiene dos partes:

1. **Parte I, aceleración de la cadena bajo presupuesto** (equivalente a Mochila 0/1).
2. **Parte II, cobertura mínima de auditoría** (equivalente a Cobertura de Conjuntos).

## Parte I: Aceleración óptima de la cadena bajo presupuesto

**Entrada:** *B* (presupuesto, entero) y una lista de etapas, cada una con tiempo de ejecución *t_i*, costo de aceleración *c_i* y duración acelerada. A partir de la duración acelerada se deriva *d_i* = *t_i* − duración acelerada, con 0 ≤ *d_i* ≤ *t_i*. Las etapas forman una cadena en el orden de la lista, salvo que se declaren precedencias (variante V3). Ver `spec/01-entrada-datos.md`.

**Objetivo:** elegir un subconjunto de etapas *A* a acelerar, sin exceder *B*, para minimizar la duración total, que es la suma de las duraciones de todas las etapas. Como la cadena es en serie, todas están siempre en la ruta crítica. La duración total es Σ(t_i − d_i) sobre i ∈ A más Σ t_i sobre el resto. Minimizarla equivale a maximizar Σ d_i para i ∈ A, sujeto a Σ c_i ≤ B.

**Reducción NP-dura (Proposición 4.2.1):** desde Mochila 0/1 con pesos *w_i*, valores *v_i*, capacidad *W* y umbral *V*. Se construye una etapa por objeto con c_i = w_i, d_i = v_i y t_i = v_i (lo que garantiza d_i ≤ t_i), con B = W. La respuesta es afirmativa si y solo si la mochila admite valor al menos V. Hay que presentar la reducción en esa dirección exacta.

**Algoritmo (programación dinámica):** tabla indexada por etapa y presupuesto usado, de tamaño (n+1) × (B+1), con cada celda calculada en tiempo constante. Complejidad O(n·B), más O(n) para reconstruir el conjunto acelerado recorriendo la tabla hacia atrás.

**Observación obligatoria:** la cota es pseudo-polinomial. Es eficiente cuando B es pequeño, pero exponencial en el tamaño de su representación en bits. No contradice la NP-dureza, porque el problema es NP-difícil en sentido débil. Debe explicarse explícitamente.

## Parte II: Cobertura mínima de auditoría

**Entrada:** una lista de interacciones candidatas, cada una con el conjunto de categorías de riesgo que cubre y su costo de auditoría *a_j* (este último solo se usa en las variantes ponderadas). *r* es el número de categorías distintas, que se declara o se deriva de la unión. La factibilidad se verifica antes de ejecutar cualquier algoritmo. Ver `spec/01-entrada-datos.md`.

**Objetivo:** elegir el menor número de interacciones tal que todas las *r* categorías queden cubiertas al menos una vez. Se asume que la unión de todas cubre las *r* categorías, y esta factibilidad debe verificarse en O(n·r) antes de ejecutar cualquier algoritmo.

**Reducción NP-completa (Proposición 4.3.1):** desde Cobertura de Vértices (Karp, 1972). Las categorías de riesgo son las aristas del grafo, cada vértice es una interacción que cubre sus aristas incidentes, y existe cobertura de vértices de tamaño ≤ k si y solo si existe auditoría de ≤ k interacciones que cubre todas las categorías. Hay que presentar la reducción estándar.

**Algoritmo voraz:** en cada paso se elige la interacción que cubre más categorías aún no cubiertas.

- **Cota (Teorema 4.3.1):** el voraz usa a lo sumo H(d) = 1 + 1/2 + ... + 1/d veces el óptimo, donde d es el máximo de categorías que cubre una sola interacción. Como d ≤ r, se tiene H(d) ≤ H_r ≈ ln r + 1. Citar a Johnson (1974) y Chvátal (1979).
- **Eficiencia:** cada paso cubre al menos una categoría nueva, así que hay a lo sumo min(n, r) pasos. Cada paso revisa las n interacciones con costo O(n·r), por lo que el peor caso es O(min(n,r) · n · r).
- **Verificación obligatoria:** comparar contra el óptimo calculado por fuerza bruta en instancias pequeñas.

## Variantes obligatorias

### V1. Cobertura ponderada por costo de auditoría

Auditar la interacción *j* tiene costo *a_j* (por ejemplo, según su longitud). Se busca cubrir todas las categorías con costo total mínimo.

- El voraz elige en cada paso la interacción de menor costo por categoría nueva cubierta (a_j / nuevas_j).
- Demostrar o citar correctamente que la cota H(d) se conserva (Chvátal, 1979) y derivar la función de eficiencia.

### V2. Combinación de ambas partes con presupuesto conjunto

Hay un único presupuesto *B* para acelerar etapas y auditar interacciones. La auditoría debe cubrir todas las categorías, y lo que sobre se usa para acelerar.

- La solución exacta consiste en resolver la cobertura ponderada de costo mínimo a* y luego aplicar la programación dinámica con presupuesto B − a*.
- Usar el voraz de cobertura da una solución factible, pero con costo de auditoría de hasta H(d) · a*. Hay que analizar, teórica y experimentalmente, cuánta reducción de tiempo se pierde por ese exceso.
- La última fila de la tabla DP[n][·] ya contiene la mejor reducción para todos los presupuestos posibles, lo que facilita el análisis.

### V3. Etapas en paralelo (grafo acíclico dirigido)

El flujo es un DAG general con *n* etapas y *m* aristas de precedencia. La duración es la de la ruta más larga.

- Se calcula con programación dinámica sobre el orden topológico en T(n, m) = O(n + m). Hay que deducirla.
- Decidir qué acelerar ya no es una mochila, porque al acelerar la ruta crítica cambia. El problema (compromiso tiempo-costo discreto) es fuertemente NP-difícil (De et al., 1997), así que la DP pseudo-polinomial no se extiende.
- Solución exacta por enumeración de subconjuntos para instancias pequeñas: O(2^n (n + m)).
- Heurística: en cada paso se recalcula la ruta crítica y se acelera, entre las etapas de esa ruta que caben en el presupuesto restante, la de mejor razón d_i / c_i. Costo O(n · (n + m)).
- Comparar ambas experimentalmente y mostrar una instancia donde la heurística no es óptima.

## Plan de desarrollo en tres etapas

### Etapa 1: Aceleración de la cadena (análoga a la mochila)

**Objetivo:** implementar la Parte I.

**Entregables:**
- Modelo de entrada: lista de etapas con (t_i, c_i, d_i) y presupuesto B, con validación 0 ≤ d_i ≤ t_i.
- Implementación de la DP O(n·B) con reconstrucción del conjunto acelerado.
- Demostración de la reducción desde Mochila 0/1 en la dirección correcta.
- Explicación del carácter pseudo-polinomial con ejemplos de B grande.
- Pruebas: comparar contra fuerza bruta en instancias pequeñas.

### Etapa 2: Cobertura mínima de auditoría con algoritmos voraces

**Objetivo:** implementar la Parte II y la variante V1.

**Entregables:**
- Verificación de factibilidad en O(n·r).
- Reducción desde Cobertura de Vértices (Karp, 1972) con la construcción de categorías como aristas.
- Algoritmo voraz para cobertura no ponderada y ponderada por costo.
- Verificación del factor H(d) contra el óptimo de fuerza bruta en instancias pequeñas, con citas a Johnson (1974) y Chvátal (1979).
- Análisis de eficiencia del voraz.

### Etapa 3: Combinación de ambas partes mediante optimización heurística

**Objetivo:** resolver el problema conjunto con presupuesto compartido (V2) y, si el tiempo lo permite, el caso de DAG (V3).

**Entregables:**
- Solución exacta para el caso conjunto: cobertura ponderada óptima a*, luego DP con B − a*.
- Versión heurística usando el voraz de cobertura y la DP. Análisis teórico del factor H(d) · a* y medición experimental de la pérdida de reducción de tiempo.
- Heurística de optimización para el caso conjunto, por ejemplo búsqueda local o recocido simulado sobre la solución del voraz, para intentar recuperar el óptimo. Comparar contra la solución exacta en instancias pequeñas.
- Para la variante V3: enumeración exacta O(2^n (n + m)) y heurística de razón d_i / c_i, mostrando una instancia donde no es óptima.
- Tabla comparativa final: calidad de solución frente a tiempo de ejecución para cada método.

## Reglas para el asistente de IA que trabaje en este proyecto

- Presentar las reducciones en la dirección correcta y con la construcción exacta indicada en cada proposición.
- Citar los resultados correctamente: Karp (1972), Johnson (1974), Chvátal (1979), De et al. (1997). No inventar atribuciones.
- Toda afirmación sobre complejidad debe indicar si es pseudo-polinomial, NP-completa, NP-difícil en sentido débil o fuertemente NP-difícil, según corresponda.
- Toda propuesta de algoritmo voraz o heurístico debe venir acompañada de una verificación empírica contra fuerza bruta en instancias pequeñas.
- Verificar la condición de factibilidad (unión de categorías cubre todo) antes de ejecutar la cobertura.
- Mantener la notación del documento: *n* etapas, *B* presupuesto, *t_i*, *c_i*, *d_i* para la Parte I; *n* interacciones, *r* categorías, *a_j* costo de auditoría, *d* máximo de categorías por interacción para la Parte II.
