# 🤖 Code Assistant

Un asistente de código con IA integrado directamente en VS Code, similar a GitHub Copilot pero construido por ti, con control total sobre los modelos, las herramientas y el comportamiento. Sin suscripciones — usa APIs gratuitas.

---

## 🎯 Objetivo

Construir un **Language Server (LSP)** potenciado por IA que funcione en VS Code y provea:

- ✅ **Autocompletado inteligente** — sugerencias de código bajo demanda con `Ctrl+K → Alt+C`
- ✅ **Explicación de código** — entiende cualquier fragmento con `Ctrl+K → Alt+E`
- ✅ **Fix de bugs** — el agente identifica y corrige errores con `Ctrl+K → Alt+F`
- ✅ **Generación de tests** — crea casos de prueba automáticamente con `Ctrl+K → Alt+T`
- 🔜 **Búsqueda de documentación** — via Tavily (próximamente)
- 🔜 **Ejecución segura de código** — sandbox Docker (próximamente)

---

## 🏗️ Arquitectura

```
VS Code (cualquier archivo .py)
        │
        │  LSP Protocol (JSON-RPC via stdin/stdout)
        │
        ▼
┌─────────────────────────────────────┐
│             server.py               │  ← Servidor LSP (pygls)
│  Maneja eventos del editor:         │
│  • textDocument/completion          │
│  • textDocument/hover               │
│  • textDocument/codeAction          │
│  • workspace/executeCommand         │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│             agent.py                │  ← Router de modelos
│  • Autocompletado  → Groq           │
│  • Explicaciones   → Gemini         │
│  • Fix bugs        → Groq           │
│  • Generar tests   → Groq           │
└──────┬──────────────┬───────────────┘
       │              │
       ▼              ▼
  Groq API       Gemini API
  (Llama 3.3)   (gemini-2.5-flash)
  ultra rápido   contexto largo
```

---

## 🛠️ Stack Tecnológico

### Por qué estas tecnologías

**LSP (Language Server Protocol)** — estándar de Microsoft que permite que un servidor de lenguaje funcione en cualquier editor. VS Code, Neovim, Zed, Sublime — todos lo soportan. Construyes el servidor una vez y funciona en todos.

**pygls** — librería Python que implementa el protocolo LSP. Sin ella tendrías que programar toda la comunicación JSON-RPC manualmente.

**Groq** — proveedor de inferencia ultrarrápido. Usa `llama-3.3-70b-versatile` para tareas de código porque es directo, rápido y sin overhead de razonamiento.

**Gemini** — usado para explicaciones porque tiene contexto de 1M tokens (puede leer archivos enormes) y razona mejor en lenguaje natural.

### Backend (Python)
| Librería | Para qué sirve |
|---|---|
| `pygls` | Implementa el protocolo LSP |
| `google-genai` | SDK de Gemini (explicaciones) |
| `groq` | SDK de Groq (código, tests, fixes) |
| `python-dotenv` | Manejo de variables de entorno |

### Cliente (TypeScript)
| Librería | Para qué sirve |
|---|---|
| `vscode-languageclient` | Conecta VS Code con el servidor LSP |

---

## 📁 Estructura del Proyecto

```
Code Assistant/                  ← Servidor LSP (Python)
├── server.py                    # Servidor LSP — maneja eventos del editor
├── agent.py                     # Router de modelos — decide qué IA usar
├── test_agent.py                # Script para probar el agente sin VS Code
├── .env                         # API Keys (nunca subir a git)
├── .gitignore
├── requirements.txt
└── server.log                   # Log del servidor (auto-generado)

code-assistant-client/           ← Extensión VS Code (TypeScript)
├── src/
│   └── extension.ts             # Cliente LSP + registro de comandos y atajos
├── package.json                 # Declaración de comandos y keybindings
└── tsconfig.json
```

---

## ⚙️ Instalación

### Requisitos previos
- Python 3.11+ o Anaconda
- Node.js 18+
- VS Code

### 1. Configurar entorno Python

```bash
# Con Anaconda (recomendado)
conda create -n code-assistant python=3.11
conda activate code-assistant

# Instalar dependencias
cd "Code Assistant"
pip install pygls google-genai groq python-dotenv
```

### 2. Configurar API Keys

Crea un archivo `.env` en la carpeta `Code Assistant`:

```env
GEMINI_API_KEY=tu_key_aqui
GROQ_API_KEY=tu_key_aqui
```

Dónde conseguir las keys (todas gratuitas):
- **Gemini** → [Google AI Studio](https://aistudio.google.com/apikey) — sin tarjeta de crédito
- **Groq** → [console.groq.com](https://console.groq.com) — sin tarjeta de crédito

### 3. Configurar las rutas en extension.ts

En `code-assistant-client/src/extension.ts` actualiza las rutas según tu sistema:

```typescript
const serverOptions: ServerOptions = {
    command: 'RUTA_A_TU_PYTHON',
    // Ejemplos:
    // Windows Anaconda: C:\\Users\\TU_USUARIO\\anaconda3\\envs\\code-assistant\\python.exe
    // Mac/Linux:        /home/TU_USUARIO/anaconda3/envs/code-assistant/bin/python
    // Sin Anaconda:     python3

    args: ['RUTA_COMPLETA_A/Code Assistant/server.py']
    // Usa la ruta absoluta donde clonaste el proyecto
};
```

> **Tip:** En Windows usa doble backslash `\\` en las rutas, o usa forward slash `/`.

### 4. Instalar la extensión en VS Code

```bash
cd code-assistant-client
npm install
npm run compile
npx vsce package
code --install-extension code-assistant-client-0.0.1.vsix
```

---

## 🧪 Probar el agente sin VS Code

Antes de usar el agente dentro del editor, puedes verificar que los modelos responden correctamente corriendo `test_agent.py` directamente desde la terminal. Esto es útil para debuggear problemas de API keys, modelos o respuestas inesperadas sin tener que abrir VS Code.

```python
# test_agent.py
from agent import get_explanation, get_tests

code = """
def suma(a, b):
    return a + b
"""

print("=== EXPLICACIÓN ===")
print(get_explanation(code))

print("\n=== TESTS ===")
print(get_tests(code))
```

Para correrlo:

```bash
conda activate code-assistant
cd "Code Assistant"
python test_agent.py
```

Si todo está bien verás algo como:

```
=== EXPLICACIÓN ===
Esta función toma dos parámetros `a` y `b` y retorna su suma.
Es una función simple de adición que funciona con números enteros y flotantes.

=== TESTS ===
import pytest
from tu_modulo import suma

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (1.5, 2.5, 4.0),
])
def test_suma(a, b, expected):
    assert suma(a, b) == expected
```

Puedes modificar `test_agent.py` para probar cualquier función — simplemente cambia el valor de `code` y agrega las funciones del agente que quieras probar (`get_completion`, `get_fix`, etc.).

---

## ⌨️ Atajos de teclado

Todos los atajos son **manuales** — el asistente solo actúa cuando tú lo pides. Cero requests automáticos, cero consumo innecesario de cuota.

| Atajo | Acción | Modelo usado |
|---|---|---|
| `Ctrl+K → Alt+C` | Autocompletar código | Groq (Llama 3.3) |
| `Ctrl+K → Alt+E` | Explicar código seleccionado | Gemini Flash |
| `Ctrl+K → Alt+F` | Fix de bugs | Groq (Llama 3.3) |
| `Ctrl+K → Alt+T` | Generar tests | Groq (Llama 3.3) |

> **Tip:** Selecciona solo la función o bloque que te interesa antes de usar los atajos — así el modelo tiene contexto preciso y la respuesta es mejor.

---

## 🚀 Cómo usar cada feature

### ✨ Autocompletar — `Ctrl+K → Alt+C`

Completa la línea o bloque que estás escribiendo. El modelo recibe todo el archivo como contexto para que la sugerencia sea coherente con tu código.

```python
# Escribes esto y presionas Ctrl+K → Alt+C
def calcular_promedio(numeros):
    # el agente completa el resto
```

---

### 💡 Explicar código — `Ctrl+K → Alt+E`

Selecciona cualquier fragmento — una línea, una función, o todo el archivo — y el agente lo explica en español.

```python
# Selecciona esto y presiona Ctrl+K → Alt+E
resultado = sorted(datos, key=lambda x: x['fecha'], reverse=True)
```

Las explicaciones se guardan en **caché** — si explicas el mismo fragmento dos veces, la segunda vez no gasta ningún request.

---

### 🔧 Fix bug — `Ctrl+K → Alt+F`

Selecciona el código con el bug y el agente lo analiza, identifica el problema y retorna el código corregido.

```python
# Selecciona esto y presiona Ctrl+K → Alt+F
def dividir(a, b):
    return a / b  # bug: no maneja división por cero
```

---

### 🧪 Generar tests — `Ctrl+K → Alt+T`

Selecciona una función o clase y el agente genera casos de prueba completos con **pytest**, incluyendo casos normales, edge cases y casos negativos.

```python
# Selecciona esto y presiona Ctrl+K → Alt+T
def suma(a, b):
    return a + b
```

El agente genera tests listos para correr:

```python
import pytest
from tu_modulo import suma

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (1.5, 2.5, 4.0),
    (100, -50, 50),
    (-10, -20, -30)
])
def test_suma(a, b, expected):
    assert suma(a, b) == expected
```

> **Tip:** Reemplaza `tu_modulo` con el nombre real del archivo donde está tu función.

---

## 🔒 Seguridad y consumo de API

### Diseño manual — cero requests automáticos

A diferencia de GitHub Copilot que genera sugerencias constantemente, Code Assistant solo llama a la API cuando tú presionas un atajo. Esto significa que no gastas cuota mientras escribes y los límites gratuitos duran mucho más.

### Cache de explicaciones

Las explicaciones se guardan en memoria durante la sesión. Si explicas el mismo fragmento dos veces, la segunda vez es instantánea y gratis.

### Límites gratuitos
| Servicio | Límite gratuito | Qué pasa si lo superas |
|---|---|---|
| Groq | 100,000 tokens/día | Solo deja de funcionar, nunca cobra |
| Gemini | 1,500 requests/día | Solo deja de funcionar, nunca cobra |

Ninguno de los servicios te cobrará automáticamente — todos simplemente retornan error 429 cuando llegas al límite.

---

## 🗺️ Roadmap

- [x] Servidor LSP base con pygls
- [x] Extensión VS Code conectada y funcionando
- [x] Autocompletado con Groq (manual trigger)
- [x] Explicación de código con Gemini (manual trigger)
- [x] Fix de bugs con Groq
- [x] Generación de tests con Groq
- [x] Cache de explicaciones para no repetir requests
- [x] Atajos de teclado personalizados (chords)
- [x] Script de prueba del agente (test_agent.py)
- [ ] Tool: búsqueda web (Tavily)
- [ ] Tool: ejecución segura (ai-code-sandbox)
- [ ] Diagnósticos en tiempo real
- [ ] Soporte para más lenguajes (JS, TS, Java)

---

## 🐛 Debugging

El servidor LSP escribe logs en `server.log` dentro de la carpeta del proyecto. Para verlos en tiempo real:

```bash
# Windows
powershell Get-Content ".\server.log" -Wait

# Mac/Linux
tail -f server.log
```

El servidor no muestra output en terminal — eso es normal. Se comunica con VS Code via `stdin/stdout`. Si algo no funciona, el log es el primer lugar donde buscar.

Si el problema es con los modelos o las API keys, corre `test_agent.py` primero — es más fácil debuggear desde la terminal que desde VS Code.

---

## 🤝 Desarrollo local

Para probar cambios sin reinstalar la extensión:

```
1. Abre la carpeta code-assistant-client en VS Code
2. Presiona F5 — abre una ventana "Extension Development Host"
3. En esa ventana abre cualquier archivo .py
4. El servidor LSP arranca automáticamente
5. Revisa server.log para ver qué está pasando
```

Cualquier cambio en `server.py` o `agent.py` se refleja al reiniciar la ventana de desarrollo (cierra y vuelve a presionar F5). No necesitas recompilar la extensión TypeScript a menos que modifiques `extension.ts` o `package.json`.

---

## 📝 Notas importantes

- El archivo `.env` **nunca** debe subirse a GitHub — está protegido por `.gitignore`
- El entorno Anaconda `code-assistant` debe estar activo para que el servidor funcione
- `server.log` se genera automáticamente y tampoco debe subirse a git
- Los modelos pueden cambiar de nombre con el tiempo — si algo deja de funcionar revisa la documentación de [Groq](https://console.groq.com/docs/models) y [Google AI Studio](https://aistudio.google.com)