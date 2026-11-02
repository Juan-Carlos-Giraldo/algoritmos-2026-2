# 02. Requisitos

Formato: cada requisito tiene un identificador, una descripción y criterios de aceptación verificables. Las referencias `[E1]`, `[E2]`, `[E3]` indican la etapa del plan en la que se implementa (ver `04-tareas.md`).

## 1. Requisitos de entrada

**RF-01 [E1, E2, E3]** El sistema carga la entrada desde un archivo JSON con la estructura de `01-entrada-datos.md`.
- Aceptación: `ejemplo_entrada.json` se carga sin errores.

**RF-02 [E1, E2, E3]** El sistema valida la entrada antes de ejecutar cualquier algoritmo y reporta el campo y el motivo de cada error.
- Aceptación: cada una de las nueve validaciones de la sección 4 de `01-entrada-datos.md` tiene un caso de prueba que produce el error esperado.

**RF-03 [E1]** El sistema deriva la reducción *d_i* = `tiempo_ejecucion` − `duracion_acelerada` para cada etapa.
- Aceptación: para cada etapa, *d_i* coincide con el cálculo manual y cumple 0 ≤ *d_i* ≤ *t_i*.

## 2. Parte I: aceleración de la cadena

**RF-10 [E1]** El sistema calcula el conjunto de etapas a acelerar que maximiza Σ *d_i* sujeto a Σ *c_i* ≤ *B*.
- Aceptación: el resultado coincide con la fuerza bruta en todas las instancias de prueba con *n* ≤ 12.

**RF-11 [E1]** El sistema reconstruye el conjunto de etapas aceleradas y reporta la duración total resultante.
- Aceptación: la duración total reportada es igual a Σ(*t_i* − *d_i*) sobre las etapas aceleradas más Σ *t_i* sobre las demás.

**RF-12 [E1]** El sistema registra la tabla DP completa y permite consultar la mejor reducción para cualquier presupuesto *b* ≤ *B*.
- Aceptación: la última fila de la tabla contiene, para cada *b*, el mejor valor de Σ *d_i*.

**RF-13 [E1]** La entrada de la Parte I se acepta sin aristas de precedencia (cadena) con las etapas en el orden de la lista.
- Aceptación: el orden de la lista define la cadena y todas las etapas están en la ruta crítica.

## 3. Parte II: cobertura mínima de auditoría

**RF-20 [E2]** El sistema verifica la factibilidad: la unión de las categorías de las interacciones cubre las *r* categorías.
- Aceptación: una entrada infactible produce el error de validación 9 antes de ejecutar cualquier algoritmo.

**RF-21 [E2]** El sistema calcula una cobertura voraz no ponderada: en cada paso elige la interacción que cubre más categorías aún no cubiertas.
- Aceptación: la solución cubre todas las categorías y el número de pasos es ≤ min(*n*, *r*).

**RF-22 [E2]** El sistema calcula el óptimo por fuerza bruta para instancias pequeñas.
- Aceptación: disponible para *n* ≤ 20.

**RF-23 [E2]** El sistema compara el voraz contra el óptimo y reporta la razón de aproximación obtenida.
- Aceptación: en todas las instancias de prueba, la razón es ≤ H(*d*), donde *d* es el máximo de categorías que cubre una interacción.

**RF-24 [E2]** El sistema calcula una cobertura voraz ponderada que elige en cada paso la interacción con menor costo por categoría nueva (*a_j* / nuevas_*j*).
- Aceptación: la solución cubre todas las categorías y su costo es ≤ H(*d*) · óptimo ponderado en las instancias de prueba.

## 4. Caso conjunto y variante DAG

**RF-30 [E3]** El sistema resuelve el problema conjunto con presupuesto *B* compartido: primero la cobertura ponderada de costo mínimo *a** y luego la DP de la Parte I con presupuesto *B* − *a**.
- Aceptación: si *a** > *B*, el sistema reporta que no hay solución factible.

**RF-31 [E3]** El sistema ofrece una versión heurística del caso conjunto que usa el voraz ponderado en lugar del óptimo.
- Aceptación: la solución es factible (costo total ≤ *B*) y se reporta la pérdida de reducción frente a la solución exacta.

**RF-32 [E3]** El sistema aplica una mejora por optimización heurística (búsqueda local o recocido simulado) sobre la solución del caso conjunto.
- Aceptación: la solución mejorada es factible y nunca es peor que la solución inicial.

**RF-33 [E3]** Si hay precedencias, el sistema calcula la duración del flujo como la ruta más larga en orden topológico.
- Aceptación: la duración coincide con el cálculo manual en instancias pequeñas.

**RF-34 [E3]** Para el caso DAG, el sistema ofrece enumeración exacta para *n* pequeño y una heurística que en cada paso acelera la etapa de la ruta crítica con mejor razón *d_i* / *c_i* que cabe en el presupuesto restante.
- Aceptación: la heurística es factible y existe al menos una instancia documentada donde no es óptima.

**RF-35 [E3]** El sistema genera una tabla comparativa de calidad de solución frente a tiempo de ejecución para cada método.
- Aceptación: la tabla incluye, para cada método, valor objetivo, costo total, tiempo de ejecución y si es exacto.

## 5. Requisitos no funcionales

**RNF-01** Complejidad de la DP de la Parte I: O(*n* · *B*) en tiempo y en memoria.

**RNF-02** Complejidad del voraz no ponderado: O(min(*n*, *r*) · *n* · *r*) en el peor caso.

**RNF-03** Reproducibilidad: dada la misma entrada y la misma semilla, la salida es idéntica.

**RNF-04** Trazabilidad: cada solución incluye el registro de decisiones (qué etapas o interacciones se eligieron y por qué).

**RNF-05** Las salidas se pueden exportar a JSON.

**RNF-06** Las pruebas automatizadas cubren cada requisito funcional con al menos un caso (ver `05-pruebas.md`).

## 6. Fuera de alcance

- Interfaz gráfica. La interacción es por línea de comandos o por biblioteca.
- Acelerar una etapa en varios niveles. Cada etapa tiene una sola opción de aceleración (a *d_i* con costo *c_i*), como en el documento original.
- Persistencia en base de datos.
