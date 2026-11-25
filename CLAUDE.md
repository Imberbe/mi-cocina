# Mi cocina

App de cocina de Alejandro: menú semanal, recetas paso a paso y lista de la compra.
Pensada para bajar el colesterol y con poco presupuesto. Todo en español de España.

## Dónde vive

- `src/mi-cocina.html` — la fuente única. Es la página que se publica en Claude como artifact:
  https://claude.ai/artifact/UZvsVsYvxtQ9zkdEGfKv5Q (declara la capacidad `db`; al republicar, no pases `capabilities` y se conserva).
- `index.html`, `sw.js`, `manifest.webmanifest`, iconos — la app instalable de GitHub Pages
  (https://imberbe.github.io/mi-cocina/). `index.html` NO se edita a mano: se genera con `python3 tools/build.py`.
- `sugerencias.json` — historial de sugerencias revisadas, que la app del móvil lee para mostrar su estado.
- Notion: página del proyecto https://app.notion.com/p/422bf473ede6817ebb2cdf3ee4f6e0bd con la base de datos «Registro de Mi cocina» (data source `collection://422bf473-ede6-8178-b1ba-000bee0a8e94`). **Todo cambio en la app se apunta ahí**: Entrada, Fecha, Tipo (Petición, Función nueva, Recetas, Arreglo, Publicación, Automático, Decisión), Quién (Alejandro, Claude, Tarea del jueves) y Detalle.

## Cómo está hecha `src/mi-cocina.html`

- `ING` = alimentos: `{n, e (emoji) o svg, q (envase), p (precio aprox. €), s: "fruta"|"fresco"|"despensa"|"especias"}`.
- `PACK` = cuánto trae cada envase (`g`, `ml`, `n` o `f`). Todo alimento nuevo necesita su entrada en `PACK`.
- `R` = recetas: `{n, pool:"d"|"m" (desayuno | comida/cena), cat, t ("20 min"), r ("1 ración"|"2 raciones"), base (color del plato o null), em (1–3 emojis), ing:[[id, cantidad]] (incluidos aceite, sal y especias), basic? (solo extras opcionales), steps:[...], tip?}`.
  `cat` de desayuno: `dulce`|`salado`. De comida/cena: `leg`|`pes`|`car`|`hue`|`ver`|`pas`.
- `col:false` en una receta o un alimento = no recomendado con el colesterol alto: el menú «Bajo en colesterol» no lo usa y la receta muestra un aviso. Los alimentos de la lista `SALTY` (latas, aceitunas, embutido, quesos…) sacan la receta del menú «Bajo en sal»; añade ahí los alimentos salados nuevos.
- El menú automático tiene tres secciones de opciones que se combinan (`OPTS` y `GROUPS`): Salud (bajo en colesterol, bajo en sal, equilibrado), Tipo de alimentación (rico en proteína, completo, vegetariano) y Tiempo y bolsillo (rápido, cocinar poco, económico). Se eligen en un asistente de 5 pasos (`openWizard`/`renderWizard`): personas, las tres secciones y un resumen con Finalizar.
- Pestaña «🧺 Lo que tengo» (`renderCocina`): lista todos los platos según lo marcado en casa, en tres bloques (lo tienes todo / falta 1 / faltan 2), con filtros (`ck`) y orden por `PERISH` (primero lo que antes se estropea). Cada plato: «Al menú» (hoja `place`, elige día y comida) y «Apuntar lo que falta» (conjunto `extra`, guardado en `casa/despensa` como `extra` y mostrado en Compra). Al añadir alimentos frescos nuevos, ponlos en `PERISH` con peso 1–3.
- Compra tiene buscador (`shopQ`; si no encuentra el alimento, ofrece sugerirlo) y botón «Marcar lo de siempre» (`BASICS`). Las sugerencias están abajo del todo de Compra, plegadas (`sugBox`), con contador de pendientes o «Novedades» cuando la revisión del jueves resuelve alguna (vistas en `micocina.sugVistas`). «Ahora» enseña solo 3 ideas y un enlace a la pestaña.
- Ya NO hay «siempre en casa» (decisión de Alejandro): aceite, sal, ajo, especias y hierbas son alimentos de la sección `s:"especias"` («Especias y condimentos», 48; precios de Mercadona-Hacendado de nov. 2026 donde existen) y van en `ing` de cada receta con su cantidad ("1 cucharada", "1 pizca", "2 dientes"…). `basic` queda solo para extras opcionales y se muestra como «Además: …». El aceite de oliva sale de la cooperativa familiar (`p:0`). `STAPLES` se marcaron como «en casa» una sola vez al migrar; «Nueva semana: desmarcar todo» no desmarca las especias.

## Reglas para recetas nuevas

- **No se descarta ningún alimento por salud** (decisión de Alejandro): todo lo que se sugiera entra con recetas, para tener platos de todo tipo. Lo que no conviene con el colesterol alto (embutido, nata, mantequilla, queso curado, carne roja, fritos…) se marca `col:false`, y si el alimento lo permite se hace también una versión sana.
- Las recetas no tienen que ser bajas en colesterol (dicho por Alejandro): platos de todo tipo, también lasaña, carbonara, croquetas, fritos… Las que no convengan se marcan `col:false` (o lo hacen sus alimentos) y el menú «Bajo en colesterol» ya las excluye. Aceite de oliva con medida.
- Baratas, con ingredientes de supermercado español. Sin alcachofa (no le gusta). La pasta le encanta.
- Pasos cortos y concretos (3–6), con tiempos y temperaturas. Cantidades en `ing` con número delante para que se puedan escalar.
- **Mínimo 20 recetas por ingrediente** (petición de Alejandro, 25/11): todos los alimentos de `ING` aparecen en 20 recetas o más. Al añadir un alimento nuevo, crea las recetas que hagan falta para llegar a 20 (combinándolo con distintas carnes, pescados, verduras y especias). El bloque `/*A3-INICIO … A3-FIN*/` contiene las ~640 recetas de esa ampliación (claves `rN_M`).

## Proceso semanal de sugerencias (cada jueves, automático)

1. **Recoger** las sugerencias pendientes de dos sitios:
   - Base de datos del artifact: herramienta `ArtifactData`, `list` de la colección `sugerencias` en la URL del artifact. Son pendientes las de `estado: "pendiente"`.
   - GitHub: issues abiertos de este repositorio cuyo título empiece por "Sugerencia" (`gh api repos/Imberbe/mi-cocina/issues`). Cada línea `- alimento` del cuerpo es una sugerencia.
2. **Análisis de duplicidad**: normaliza (minúsculas, sin tildes, singular) y compara cada sugerencia con los nombres de `ING` y con las demás sugerencias. Sinónimos cuentan como duplicado (p. ej. "pechuga de pollo" = pollo).
   No se descarta nada por salud: lo que no convenga con el colesterol se añade igual con `col:false`. Solo es `descartado` lo que no sea un alimento.
3. **Añadir** cada alimento nuevo a `ING` y `PACK`, y crear recetas con él hasta que aparezca en **al menos 20** (al menos la mitad comidas o cenas), siguiendo las reglas.
4. **Probar** con Playwright a 400 px: sin errores de consola y que cada receta nueva se abre. Comprueba que todo `ing` existe en `ING`.
5. **Publicar**:
   - Claude: `Artifact` `read` de la URL y después `publish` con `url` y `file_path` = `src/mi-cocina.html`.
   - GitHub: `python3 tools/build.py`, actualiza `sugerencias.json`, commit y push a `main`.
6. **Cerrar el ciclo**:
   - En la base de datos, actualiza cada sugerencia con `estado` (`añadido` | `duplicado` | `descartado`) y `nota` corta (p. ej. "Añadido el 26/11 con 3 recetas: …" o "Ya estaba como Brócoli").
   - Añade lo mismo a `sugerencias.json` (`[{texto, estado, nota, fecha}]`).
   - Comenta y cierra cada issue de GitHub procesado.
7. Apunta la revisión en el registro de Notion (Quién «Tarea del jueves», Tipo «Automático»), y las recetas nuevas en otra entrada de Tipo «Recetas».
8. Si no hay sugerencias pendientes, no cambies la app: solo apunta en el registro que no había ninguna.
