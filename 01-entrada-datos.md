# 01. Especificación de la entrada de datos

## 1. Propósito

Define el formato, el significado y las validaciones de la entrada del Subproyecto 3. Es la única fuente de verdad sobre qué datos recibe el sistema.

## 2. Entrada propuesta

La entrada tiene dos partes independientes que comparten el presupuesto *B*:

- **Etapas de la cadena** (Parte I): una lista de nodos, cada uno con tiempo de ejecución, costo de aceleración y duración acelerada.
- **Interacciones de auditoría** (Parte II): una lista de aristas, cada una con las categorías de riesgo que cubre y su costo de auditoría.

Se representa en JSON (ver `ejemplo_entrada.json`).

```json
{
  "presupuesto": 10,
  "etapas": [
    { "id": "E1", "tiempo_ejecucion": 5, "costo_aceleracion": 3, "duracion_acelerada": 2 }
  ],
  "precedencias": [],
  "auditoria": {
    "categorias": ["sesgo", "fuga_datos", "formato"],
    "interacciones": [
      { "id": "I1", "categorias": ["sesgo", "formato"], "costo_auditoria": 2 }
    ]
  }
}
```

## 3. Campos

### 3.1 Presupuesto

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `presupuesto` | entero | Sí | *B* ≥ 0. Es el *B* del documento original. |

### 3.2 Etapas (nodos)

| Campo | Tipo | Obligatorio | Regla | Equivalencia con el documento |
|---|---|---|---|---|
| `id` | cadena | Sí | Único dentro de la lista | Identificador de la etapa *i* |
| `tiempo_ejecucion` | entero | Sí | *t_i* ≥ 0 | *t_i* |
| `costo_aceleracion` | entero | Sí | *c_i* ≥ 0 | *c_i* |
| `duracion_acelerada` | entero | Sí | 0 ≤ `duracion_acelerada` ≤ `tiempo_ejecucion` | *t_i* − *d_i* |

**Campo derivado (no se captura):** la reducción *d_i* = `tiempo_ejecucion` − `duracion_acelerada`. El sistema la calcula al cargar la entrada. Esto cumple 0 ≤ *d_i* ≤ *t_i*.

### 3.3 Precedencias (opcional)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `precedencias` | lista de pares `[origen, destino]` | No | Si está vacía o ausente, las etapas forman una cadena en el orden de la lista (Parte I). Si no está vacía, el grafo debe ser acíclico y el caso pasa a la variante V3 (DAG). |

### 3.4 Auditoría (aristas)

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `categorias` | lista de cadenas | No | Universo de las *r* categorías. Si se omite, se deriva de la unión de las categorías de las interacciones. Si se declara, sirve para verificar la factibilidad. |
| `interacciones[].id` | cadena | Sí | Único |
| `interacciones[].categorias` | lista de cadenas | Sí | No vacía; cada elemento debe existir en `categorias` si esta lista se declaró |
| `interacciones[].costo_auditoria` | entero | Depende de la etapa | *a_j* ≥ 0. Obligatorio para la cobertura ponderada (V1) y el caso conjunto (V2). No se usa en la cobertura no ponderada. |

## 4. Validaciones de carga

El sistema rechaza la entrada con un error que indique el campo y el motivo si ocurre cualquiera de estos casos:

1. `presupuesto` no es entero o es negativo.
2. Dos etapas o dos interacciones tienen el mismo `id`.
3. Una etapa tiene `duracion_acelerada` < 0 o > `tiempo_ejecucion`.
4. Un valor numérico es negativo o no es entero.
5. Una interacción tiene `categorias` vacía.
6. Una categoría de una interacción no aparece en `categorias` (cuando esa lista está declarada).
7. Las precedencias contienen un ciclo, o referencian una etapa inexistente.
8. Falta `costo_auditoria` en una ejecución que lo requiere (V1 o V2).
9. **Factibilidad de la auditoría:** la unión de las categorías de todas las interacciones debe cubrir las *r* categorías. Esta comprobación se hace en O(n·r) antes de ejecutar cualquier algoritmo de cobertura.

## 5. Comparación con el planteamiento original y decisiones

Se identificaron los siguientes puntos donde la entrada propuesta difiere del documento original. Cada uno tiene una decisión tomada en este spec.

### 5.1 Duración acelerada frente a reducción *d_i*

El documento trabaja con *d_i* (la reducción). La entrada propone `duracion_acelerada`.

**Decisión:** se captura `duracion_acelerada` porque es el dato que se tiene, y se deriva *d_i*. La conversión es exacta y la validación 0 ≤ *d_i* ≤ *t_i* equivale a 0 ≤ `duracion_acelerada` ≤ `tiempo_ejecucion`.

### 5.2 Las aristas del grafo no son el grafo de la cadena

En el documento hay dos estructuras distintas:

- La **cadena de etapas** (Parte I) tiene orden de precedencia. Si el grafo que se describe tiene aristas que representan ese orden, son precedencias, no categorías.
- Las **interacciones con categorías** (Parte II) son conjuntos. Una interacción cubre un subconjunto de categorías.

Usar un mismo grafo con aristas para ambas cosas mezcla dos significados. Además, si una arista cubre más de dos categorías, el objeto deja de ser un grafo ordinario y pasa a ser un hipergrafo.

**Decisión:** las etapas y las interacciones se capturan como listas de registros, separadas. La representación gráfica queda solo como visualización opcional. Si el grafo de etapas tiene aristas de precedencia, se capturan en `precedencias`.

**Pregunta abierta para el usuario:** ¿las aristas del grafo representan interacciones (con categorías y costo) o precedencias entre etapas? ¿Y cada arista cubre exactamente dos categorías o puede cubrir más?

### 5.3 Estructura de la reducción de Cobertura de Vértices

En el documento, las categorías son las aristas de un grafo auxiliar y las interacciones son sus vértices. La entrada propone lo inverso: las interacciones son las aristas y las categorías son los nodos.

**Decisión:** ambas codificaciones describen Cobertura de Conjuntos y son válidas. La implementación usa el formato de registros de la sección 3.4, que coincide con la definición de Cobertura de Conjuntos. La reducción de la Proposición 4.3.1 se documenta en la etapa 2 en la dirección del documento original.

### 5.4 Costo de auditoría

El documento solo usa el costo de auditoría en la variante ponderada (V1) y en el caso conjunto (V2). La cobertura no ponderada no lo necesita.

**Decisión:** `costo_auditoria` es obligatorio solo cuando la ejecución lo requiere (validación 8).

### 5.5 Presupuesto compartido

En el documento el presupuesto *B* es uno solo en la variante V2. La entrada lo declara como un campo único.

**Decisión:** `presupuesto` es un solo campo. La Parte I lo usa completo y el caso conjunto lo reparte según la sección 4 de `03-diseno.md`.

## 6. Ejemplo válido

Ver `ejemplo_entrada.json`. Contiene tres etapas en cadena y cuatro interacciones sobre tres categorías.
