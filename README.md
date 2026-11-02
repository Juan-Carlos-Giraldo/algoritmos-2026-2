# Spec: Subproyecto 3, ruta crítica con aceleración bajo presupuesto y cobertura mínima de auditoría

Este spec sigue el flujo de desarrollo guiado por especificación: primero se define qué debe hacer el sistema, luego cómo, y al final las tareas y pruebas. Cada documento se apoya en el anterior.

## Documentos

| Archivo | Contenido | Fase |
|---|---|---|
| `01-entrada-datos.md` | Formato de entrada, validaciones y decisiones frente al planteamiento original | Especificación |
| `02-requisitos.md` | Requisitos funcionales y no funcionales con criterios de aceptación | Especificación |
| `03-diseno.md` | Modelo de datos, módulos, algoritmos y CLI | Diseño |
| `04-tareas.md` | Tareas por etapa, dependencias y trazabilidad | Plan |
| `05-pruebas.md` | Casos de prueba y criterios de aceptación del proyecto | Verificación |
| `ETAPA-1.md` | Implementación, algoritmo y análisis de eficiencia de la Etapa 1 | Documentación |
| `ejemplo_entrada.json` | Entrada válida de referencia | Datos |
| `subproyecto3/` | Implementación ejecutable de la Etapa 1 | Código |
| `tests/` | Pruebas automatizadas de la Etapa 1 | Verificación |

## Flujo

1. Revisar `01-entrada-datos.md` y confirmar las preguntas abiertas de la sección 5.
2. Congelar `02-requisitos.md`. Cualquier cambio de alcance se registra aquí antes de tocar el código.
3. Implementar según `03-diseno.md`.
4. Ejecutar las tareas de `04-tareas.md` por etapa, cerrando cada etapa con su criterio.
5. Verificar con `05-pruebas.md` antes de dar el proyecto por terminado.

## Usar la Etapa 1

Se necesita Python 3.10 o posterior. Desde la carpeta del proyecto, ejecuta:

```powershell
python -m subproyecto3 validar ejemplo_entrada.json
python -m subproyecto3 cadena ejemplo_entrada.json
```

Si Windows no reconoce `python`, ejecuta los mismos comandos anteponiendo
`& 'RUTA\A\python.exe' -m`; por ejemplo, en este entorno:
`& 'C:\Users\jucar\AppData\Local\Programs\Python\Python312\python.exe' -m subproyecto3 generar-ejemplos`.

El comando `cadena` imprime en la terminal la solución y la tabla DP completa.
Para comprobar la solución con fuerza bruta en entradas pequeñas:

```powershell
python -m subproyecto3 cadena ejemplo_entrada.json --comparar-fuerza-bruta
```

Para guardar la respuesta JSON de una entrada en una carpeta:

```powershell
python -m subproyecto3 cadena ejemplo_entrada.json --salida salidas
```

### Generar ejemplos y el informe HTML

Este comando crea entradas con 3, 10 y 25 etapas, ejecuta la DP para cada una y
guarda todas las entradas y respuestas junto con un informe legible en HTML:

```powershell
python -m subproyecto3 generar-ejemplos
```

Los archivos quedan en `salidas/`: tres `ejemplo_*.json`, tres
`resultado_*.json` (incluyen la tabla DP completa) y `informe.html`. Abre
`salidas/informe.html` en un navegador para ver un resumen y, si lo deseas,
expandir la tabla de cada ejemplo. Puedes cambiar la carpeta:

```powershell
python -m subproyecto3 generar-ejemplos --salida resultados_demo
```

Para ejecutar las pruebas automatizadas:

```powershell
python -m pytest -q
```

## Etapas de desarrollo

1. **Etapa 1:** aceleración de la cadena, análoga a la mochila (Parte I).
2. **Etapa 2:** cobertura mínima de auditoría con algoritmos voraces (Parte II).
3. **Etapa 3:** combinación de ambas partes con optimización heurística, más la variante de DAG.

## Preguntas abiertas

Estas respuestas cambian la entrada o el diseño. Hasta tenerlas, el spec asume lo indicado.

1. Las aristas del grafo, ¿representan interacciones de auditoría o precedencias entre etapas? *Supuesto actual: interacciones y etapas en listas separadas, con precedencias opcionales.*
2. ¿Cada interacción cubre exactamente dos categorías o puede cubrir más? *Supuesto actual: cualquier número, con la representación de conjunto.*
3. ¿El presupuesto *B* es el mismo para acelerar y para auditar, o son presupuestos separados? *Supuesto actual: uno solo compartido, como en la variante V2.*
