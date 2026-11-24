# Mi cocina

App de cocina de Alejandro: menú semanal, recetas paso a paso y lista de la compra.
Pensada para bajar el colesterol y con poco presupuesto. Todo en español de España.

## Dónde vive

- `src/mi-cocina.html` — la fuente única. Es la página que se publica en Claude como artifact:
  https://claude.ai/artifact/UZvsVsYvxtQ9zkdEGfKv5Q (declara la capacidad `db`; al republicar, no pases `capabilities` y se conserva).
- `index.html`, `sw.js`, `manifest.webmanifest`, iconos — la app instalable de GitHub Pages
  (https://imberbe.github.io/mi-cocina/). `index.html` NO se edita a mano: se genera con `python3 tools/build.py`.
- `sugerencias.json` — historial de sugerencias revisadas, que la app del móvil lee para mostrar su estado.

## Cómo está hecha `src/mi-cocina.html`

- `ING` = alimentos: `{n, e (emoji) o svg, q (envase), p (precio aprox. €), s: "fruta"|"fresco"|"despensa"}`.
- `PACK` = cuánto trae cada envase (`g`, `ml`, `n` o `f`). Todo alimento nuevo necesita su entrada en `PACK`.
- `R` = recetas: `{n, pool:"d"|"m" (desayuno | comida/cena), cat, t ("20 min"), r ("1 ración"|"2 raciones"), base (color del plato o null), em (1–3 emojis), ing:[[id, cantidad]], basic (lo que siempre hay en casa), steps:[...], tip?}`.
  `cat` de desayuno: `dulce`|`salado`. De comida/cena: `leg`|`pes`|`car`|`hue`|`ver`|`pas`.
- Siempre en casa (no van en `ing`): aceite de oliva (de la cooperativa familiar), sal, ajo, pimentón, comino, laurel, orégano, perejil, canela, vinagre.

## Reglas para recetas nuevas

- Buenas para el colesterol: nada de embutido, nata, mantequilla, queso curado, carne roja grasa ni fritos. Aceite de oliva con medida.
- Baratas, con ingredientes de supermercado español. Sin alcachofa (no le gusta). La pasta le encanta.
- Pasos cortos y concretos (3–6), con tiempos y temperaturas. Cantidades en `ing` con número delante para que se puedan escalar.

## Proceso semanal de sugerencias (cada jueves, automático)

1. **Recoger** las sugerencias pendientes de dos sitios:
   - Base de datos del artifact: herramienta `ArtifactData`, `list` de la colección `sugerencias` en la URL del artifact. Son pendientes las de `estado: "pendiente"`.
   - GitHub: issues abiertos de este repositorio cuyo título empiece por "Sugerencia" (`gh api repos/Imberbe/mi-cocina/issues`). Cada línea `- alimento` del cuerpo es una sugerencia.
2. **Análisis de duplicidad**: normaliza (minúsculas, sin tildes, singular) y compara cada sugerencia con los nombres de `ING` y con las demás sugerencias. Sinónimos cuentan como duplicado (p. ej. "pechuga de pollo" = pollo).
   No añadas lo que choque con las reglas de salud (embutido, nata…): márcalo `descartado` con el motivo.
3. **Añadir** cada alimento nuevo a `ING` y `PACK`, y crear **2 o 3 recetas nuevas** con él (al menos una comida o cena), siguiendo las reglas.
4. **Probar** con Playwright a 400 px: sin errores de consola y que cada receta nueva se abre. Comprueba que todo `ing` existe en `ING`.
5. **Publicar**:
   - Claude: `Artifact` `read` de la URL y después `publish` con `url` y `file_path` = `src/mi-cocina.html`.
   - GitHub: `python3 tools/build.py`, actualiza `sugerencias.json`, commit y push a `main`.
6. **Cerrar el ciclo**:
   - En la base de datos, actualiza cada sugerencia con `estado` (`añadido` | `duplicado` | `descartado`) y `nota` corta (p. ej. "Añadido el 26/11 con 3 recetas: …" o "Ya estaba como Brócoli").
   - Añade lo mismo a `sugerencias.json` (`[{texto, estado, nota, fecha}]`).
   - Comenta y cierra cada issue de GitHub procesado.
7. Si no hay sugerencias pendientes, no cambies nada.
