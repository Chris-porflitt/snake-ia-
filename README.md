# 🐍 Snake UCS – Agente de Búsqueda (10×10)

Un agente autónomo que juega **Snake** en un tablero de 10×10, recolectando hasta **35 manzanas** sin chocar con las paredes ni consigo mismo.  
Utiliza el algoritmo de **Búsqueda de Costo Uniforme (UCS)** para planificar rutas óptimas en términos de pasos.  

El programa mide y reporta tanto el tiempo total de ejecución como el tiempo dedicado a la planificación.

## Integrantes

 - Cristóbal Ribertt
 - Miguel Gómez
 - Christoper Porflitts

---

## Objetivos del Proyecto
- Jugar Snake en una tablero de **10×10** con una longitud inicial de al menos 3.
- Recolectar un **máximo de 35 manzanas** y finalizar con éxito al alcanzar esa cantidad.
- Utilizar un algoritmo de búsqueda (**UCS**).
- Medir el tiempo de resolución y de planificación.
- Entregar el código documentado junto con un **README claro y detallado**.

---

## Requisitos
- Python **3.9** o superior  
- Pygame

---

## Ejecución python snake.py

Cierra el juego con la tecla ESC o el botón de cerrar la ventana.
El HUD muestra el puntaje en todo momento. Al finalizar (ya sea por éxito o por perder), aparece un panel con métricas.

## Algoritmo de Búsqueda

Se utiliza Uniform Cost Search (UCS) sobre una tablero de 10×10, considerando un costo uniforme por cada movimiento.

Es óptimo en términos de número de pasos, dado que el costo es siempre el mismo.

El agente replantea la ruta en cada tick hacia la fruta, evitando las celdas ocupadas por su propio cuerpo (excepto la cabeza).

Fallback seguro: si no hay camino disponible (por ejemplo, si se encierra a sí misma), el agente intenta moverse a una celda vecina libre para evitar quedarse inmóvil.

Como los costos son unitarios, UCS y BFS encuentran rutas de la misma longitud. Sin embargo, UCS mantiene explícito el costo acumulado, lo que facilita su extensión a escenarios con costos no uniformes.

## ¿Qué pasa si no hay camino?

La serpiente utiliza una estrategia de respaldo que consiste en moverse a un vecino libre, evitando quedarse quieta. En muchos casos, esto ayuda a reabrir espacio.

## ¿Cómo se mide el tiempo de resolución?

Se utiliza time.perf_counter() desde el inicio de la partida hasta que se alcanza la manzana número 35 o se produce un game over. Este tiempo se muestra en pantalla al finalizar.

## ¿Qué es UCS y por qué usarlo en Snake 10×10?

Uniform Cost Search (UCS) expande primero el nodo con menor costo acumulado. Como cada movimiento tiene un costo fijo de 1, UCS garantiza la ruta más corta en número de pasos, al igual que BFS, pero con una representación clara del costo acumulado.

## Ventajas de UCS en este contexto:

Tablero pequeño y discreto (10×10): el espacio de estados es limitado y UCS puede manejarlo sin problemas.

Costo uniforme: el objetivo inmediato (alcanzar la fruta) se adapta naturalmente al modelo de costos constantes → UCS devuelve la ruta más corta.

Fácil de extender: si en el futuro se desea penalizar giros, pasillos o zonas peligrosas, UCS permite incorporar costos variables sin alterar el diseño base.

