# Etapa 1: aceleración de la cadena

## Objetivo y alcance

La Etapa 1 resuelve la Parte I del proyecto: seleccionar qué etapas acelerar
para maximizar la reducción total del tiempo, sin exceder el presupuesto. Cada
etapa tiene una sola opción de aceleración (0/1): se acelera completa o no se
acelera.

La solución exacta se calcula mediante programación dinámica para Mochila 0/1.
La salida contiene las etapas elegidas, la reducción máxima, la duración final
y la tabla completa que permite consultar todos los presupuestos.

Esta etapa trata las etapas como una cadena en el orden de la lista. Aunque el
cargador valida precedencias acíclicas, el algoritmo de ruta crítica para DAG
pertenece a la Etapa 3 y no se aplica aquí.

## Trabajo implementado

### Modelos

En `subproyecto3/models.py` se definieron:

- `Etapa`: identificador, tiempo de ejecución, costo de aceleración y duración
  acelerada. La reducción se deriva con
  `reduccion = tiempo_ejecucion - duracion_acelerada`.
- `Interaccion`: identificador, conjunto de categorías y costo de auditoría
  opcional, para mantener el modelo común de entrada.
- `Entrada`: presupuesto, etapas, precedencias, categorías e interacciones.
- `Solucion`: estructura general para resultados del proyecto, con serialización
  a diccionario.

### Carga y validación

`subproyecto3/cargador_validador.py` lee el JSON UTF-8 y reporta errores con el
campo afectado y el motivo. Valida, entre otras cosas:

- presupuesto, tiempos, costos y duraciones como enteros no negativos (los
  booleanos no cuentan como enteros);
- identificadores únicos de etapas e interacciones;
- duración acelerada menor o igual que el tiempo de ejecución;
- referencias válidas y ausencia de ciclos en las precedencias;
- estructura de categorías e interacciones y cobertura del universo declarado;
- costo de auditoría cuando una llamada solicita expresamente que sea
  obligatorio.

La función `cargar_entrada` no exige costos de auditoría para resolver la cadena.
La auditoría y sus algoritmos de cobertura no forman parte del objetivo de esta
etapa.

### Programación dinámica y solución

`subproyecto3/cadena_dp.py` implementa:

- la tabla DP completa;
- la reconstrucción de las etapas elegidas desde la última fila;
- la consulta de la mejor reducción para un presupuesto;
- el cálculo de la duración total;
- una búsqueda exhaustiva de subconjuntos, usada para verificar instancias
  pequeñas.

### Interfaz, ejemplos y documentación visual

El módulo ejecutable `subproyecto3` ofrece estos comandos:

```powershell
python -m subproyecto3 validar ejemplo_entrada.json
python -m subproyecto3 cadena ejemplo_entrada.json
python -m subproyecto3 cadena ejemplo_entrada.json --comparar-fuerza-bruta
python -m subproyecto3 cadena ejemplo_entrada.json --salida salidas
python -m subproyecto3 generar-ejemplos
```

`generar-ejemplos` crea instancias de 3, 10 y 25 etapas, ejecuta el algoritmo y
escribe las entradas y resultados JSON junto con `salidas/informe.html`. El
informe presenta los resultados y permite expandir la tabla y los pasos de la
reconstrucción. En la tabla, el recorrido de reconstrucción aparece resaltado:
verde para una etapa acelerada, amarillo para una etapa no acelerada y azul
para el estado inicial.

Los archivos de ejemplo generados se encuentran en `salidas/`. La salida de
cada ejecución de `cadena` se imprime en la terminal y se puede persistir como
JSON mediante `--salida`.

## Modelo matemático

Para cada etapa \(i\):

- \(t_i\): tiempo original;
- \(c_i\): costo de acelerarla;
- \(t_i^a\): duración después de acelerarla;
- \(d_i = t_i - t_i^a\): reducción obtenida;
- \(B\): presupuesto máximo;
- \(n\): número de etapas.

Se busca un subconjunto \(S\) que maximice

\[
\sum_{i \in S} d_i
\]

sujeto a

\[
\sum_{i \in S} c_i \le B.
\]

La duración resultante de la cadena es

\[
\sum_{i=1}^{n} t_i - \sum_{i \in S} d_i.
\]

## Programación dinámica 0/1

### Estado y recurrencia

Sea \(DP[i][b]\) la reducción máxima usando solo las primeras \(i\) etapas y un
presupuesto de como máximo \(b\).

Caso base:

\[
DP[0][b] = 0 \quad \text{para } 0 \le b \le B.
\]

Para la etapa \(i\), con costo \(c_i\) y reducción \(d_i\):

\[
DP[i][b] =
\begin{cases}
DP[i-1][b], & c_i > b,\\
\max(DP[i-1][b],\; DP[i-1][b-c_i]+d_i), & c_i \le b.
\end{cases}
\]

El primer término representa no acelerar la etapa; el segundo, acelerarla.
Siempre se consulta la fila anterior, por lo que la etapa no puede seleccionarse
más de una vez.

### Pseudocódigo

```text
crear DP[0..n][0..B] inicializada en 0

para i desde 1 hasta n:
    etapa = etapas[i - 1]
    para b desde 0 hasta B:
        DP[i][b] = DP[i - 1][b]
        si etapa.costo_aceleracion <= b:
            con_etapa = DP[i - 1][b - etapa.costo_aceleracion]
                        + etapa.reduccion
            DP[i][b] = max(DP[i][b], con_etapa)

devolver DP
```

La respuesta óptima es `DP[n][B]`.

### Reconstrucción del conjunto

La reconstrucción empieza en \((i,b)=(n,B)\) y avanza hacia arriba:

1. Si `DP[i][b] != DP[i - 1][b]`, la etapa \(i\) fue acelerada y se actualiza
   \(b \leftarrow b-c_i\).
2. Si los valores son iguales, no se acelera la etapa y \(b\) no cambia.
3. Se continúa con la fila \(i-1\) hasta llegar a la fila cero.

Las etapas se invierten al final para conservar el orden original. Si ambas
alternativas empatan, la implementación conserva la alternativa de no acelerar,
ya que solo selecciona al encontrar una mejora estricta en la celda.

## Análisis de eficiencia

### Función de eficiencia

El algoritmo llena una matriz de \((n+1)(B+1)\) celdas. Para cada una de las
\(n(B+1)\) celdas correspondientes a etapas, ejecuta un número constante de
operaciones: copia el valor de la fila anterior y, cuando cabe en el
presupuesto, compara el valor de incluir la etapa.

Una función de eficiencia que cuenta el trabajo de la tabla es:

\[
T(n,B) = \Theta\big((n+1)(B+1)\big).
\]

Para \(n \ge 1\) y \(B \ge 1\), esto se simplifica a:

\[
T(n,B) = \Theta(nB),
\qquad
T(n,B) = O(nB).
\]

La cota \(\Theta\) es ajustada porque se inicializa la matriz y se visitan sus
celdas en cada ejecución, incluso cuando una etapa no cabe en cierto
presupuesto.

### Memoria

Se conserva la tabla completa de \((n+1)(B+1)\) enteros para permitir la
reconstrucción y consultar la última fila:

\[
M(n,B) = \Theta\big((n+1)(B+1)\big) = O(nB)
\]

para \(n,B \ge 1\). La reconstrucción usa \(O(n)\) identificadores y la fila
final ocupa \(O(B)\); ambos costos quedan dominados por la tabla.

### Reconstrucción y consulta

- Reconstruir las etapas y producir la fila final cuesta
  \(O(n+B)\) tiempo adicional y \(O(n+B)\) memoria adicional cuando la tabla ya
  está disponible.
- `mejor_reduccion_por_presupuesto(b)` valida \(b\), calcula la tabla completa
  y devuelve su celda final. Por tanto, en la implementación actual, cada
  llamada cuesta \(O(nB)\) tiempo y \(O(nB)\) memoria; si se consulta directamente
  una fila final ya calculada, una consulta individual cuesta \(O(1)\).

### Naturaleza pseudo-polinomial

El tiempo depende del valor numérico \(B\), no de la cantidad de bits necesaria
para codificar \(B\). Si el presupuesto se representa en binario, su longitud
es \(\Theta(\log B)\), mientras que la DP crece linealmente con \(B\). Por eso
la solución es pseudo-polinomial, no necesariamente polinomial respecto al
tamaño binario de la entrada.

La implementación almacena la tabla completa para facilitar explicación,
reconstrucción y consulta. Una versión que solo necesitara el valor óptimo
podría reducir memoria usando una fila, pero ya no conservaría directamente
toda la información requerida para esta salida.

### Fuerza bruta de verificación

`brute_force_best` enumera los \(2^n\) subconjuntos y, para cada uno, recorre
hasta \(n\) etapas para sumar costos y reducciones. Su tiempo es

\[
T_{\text{fuerza bruta}}(n) = \Theta(n2^n) = O(n2^n).
\]

El espacio auxiliar es \(O(n)\) para acumular el subconjunto candidato. Este
método es útil como oráculo de prueba para \(n\) pequeño, no como solución para
entradas grandes.

## Verificación realizada

Las pruebas de `tests/test_stage1.py` comprueban la carga del ejemplo de
referencia, la derivación de reducciones, el resultado y duración de la DP, la
consulta de la fila final, una entrada inválida, la coincidencia entre DP y
fuerza bruta y la generación de entradas, resultados e informe HTML.

Ejecución de pruebas utilizada:

```powershell
python -m pytest -q
```

El conjunto actual termina con **6 pruebas pasadas**.
