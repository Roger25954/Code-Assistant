# 🤖 Code Assistant

Un asistente de código con IA integrado directamente en tu editor, similar a GitHub Copilot pero construido por ti, con control total sobre el modelo, las herramientas y el comportamiento.

---

## 🎯 Objetivo

Construir un **Language Server (LSP)** potenciado por IA que funcione en cualquier editor compatible (VS Code, Neovim, Zed, etc.) y provea:

- ✅ **Autocompletado inteligente** — sugerencias de código generadas por IA en tiempo real
- ✅ **Explicación de código** — al pasar el mouse sobre cualquier fragmento, la IA lo explica
- ✅ **Detección y corrección de bugs** — el agente identifica errores y sugiere fixes
- ✅ **Generación de código** — genera funciones, clases y módulos completos
- ✅ **Generación de tests** — crea casos de prueba automáticamente para tu código
- ✅ **Búsqueda de documentación** — consulta docs actualizadas en tiempo real via Tavily
- ✅ **Ejecución segura de código** — corre snippets en un sandbox aislado sin riesgo para tu OS

---

## 🏗️ Arquitectura

```
Tu Editor (VS Code u otro)
        │
        │  LSP Protocol (JSON-RPC)
        │
        ▼
┌─────────────────────────────────┐
│         server.py               │  ← Servidor LSP (pygls)
│  Maneja eventos del editor:     │
│  • textDocument/completion      │
│  • textDocument/hover           │
│  • textDocument/codeAction      │
│  • textDocument/diagnostic      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│          agent.py               │  ← Agente IA (loop agentico)
│  • Recibe contexto del código   │
│  • Decide qué tool usar         │
│  • Retorna respuesta al editor  │
└────────────┬────────────────────┘
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
  Gemini  Tavily  ai-code-sandbox
  (IA)   (búsqueda) (ejecución segura)
```

---

## 🛠️ Stack Tecnológico

### Backend (Python)
| Librería | Versión | Para qué sirve |
|---|---|---|
| `pygls` | 2.x | Implementa el protocolo LSP |
| `google-generativeai` | latest | Modelo de IA (Gemini) |
| `tavily-python` | latest | Búsqueda web optimizada para IA |
| `ai-code-sandbox` | latest | Ejecución segura de código via Docker |
| `python-dotenv` | latest | Manejo de variables de entorno |

### Cliente (TypeScript)
| Librería | Para qué sirve |
|---|---|
| `vscode-languageclient` | Conecta VS Code con el servidor LSP |

---

## 📁 Estructura del Proyecto

```
Code Assistant/                  ← Servidor LSP (Python)
├── server.py                    # Servidor LSP principal
├── agent.py                     # Loop agentico + integración Gemini
├── tools/
│   ├── __init__.py
│   ├── search.py                # Tool: búsqueda web (Tavily)
│   └── sandbox.py               # Tool: ejecución segura de código
├── .env                         # API Keys (nunca subir a git)
├── .gitignore
├── requirements.txt
└── server.log                   # Log del servidor (auto-generado)

code-assistant-client/           ← Extensión VS Code (TypeScript)
├── src/
│   └── extension.ts             # Cliente LSP — puente con VS Code
├── package.json
└── tsconfig.json
```

---

## ⚙️ Configuración

### 1. Clonar y configurar entorno

```bash
# Crear entorno Anaconda
conda create -n code-assistant python=3.11
conda activate code-assistant

# Instalar dependencias Python
cd "Code Assistant"
pip install pygls anthropic tavily-python ai-code-sandbox python-dotenv google-generativeai
```

### 2. Configurar API Keys

Crea un archivo `.env` en la carpeta `Code Assistant`:

```env
GEMINI_API_KEY=tu_key_aqui
TAVILY_API_KEY=tu_key_aqui
```

- **Gemini API Key** → [Google AI Studio](https://aistudio.google.com/apikey) (gratis)
- **Tavily API Key** → [Tavily](https://tavily.com) (gratis hasta 1,000 búsquedas/mes)

### 3. Instalar la extensión de VS Code

```bash
cd code-assistant-client
npm install
npm run compile
npx vsce package
code --install-extension code-assistant-client-0.0.1.vsix
```

---

## 🚀 Uso

Una vez instalada la extensión, el servidor LSP arranca automáticamente cuando abres cualquier archivo `.py` en VS Code.

| Feature | Cómo usarlo |
|---|---|
| Autocompletado | Escribe código normalmente, las sugerencias aparecen automáticamente |
| Explicación | Pasa el mouse sobre cualquier función o variable |
| Fix bug | `Ctrl+.` sobre un error para ver sugerencias de la IA |
| Generar tests | Click derecho → Code Actions → "Generate Tests" |
| Buscar docs | La IA consulta Tavily automáticamente cuando necesita información |

---

## 🔒 Seguridad

El código que genera o ejecuta el agente corre dentro de un **contenedor Docker aislado** via `ai-code-sandbox`. Esto garantiza que:

- Ningún código malicioso puede afectar tu sistema operativo
- El sandbox no tiene acceso a tu filesystem ni a tu red
- Cada ejecución corre en un contenedor limpio que se destruye al terminar

> ⚠️ Requiere Docker Desktop instalado para la funcionalidad de ejecución de código.

---

## 🗺️ Roadmap

- [x] Servidor LSP base con pygls
- [x] Extensión VS Code conectada
- [x] Autocompletado estático funcionando
- [x] Hover funcionando
- [ ] Integración con Gemini
- [ ] Tool: búsqueda web (Tavily)
- [ ] Tool: ejecución segura (ai-code-sandbox)
- [ ] Code Actions (fix bug, generate tests)
- [ ] Diagnósticos en tiempo real
- [ ] Soporte para más lenguajes (JS, TS, Java)
- [ ] Publicación en VS Code Marketplace

---

## 🤝 Entorno de Desarrollo

Para desarrollar y probar cambios sin reinstalar la extensión:

```bash
# 1. Abre code-assistant-client en VS Code
# 2. Presiona F5 — abre una ventana "Extension Development Host"
# 3. En esa ventana abre cualquier archivo .py
# 4. El servidor LSP arranca automáticamente
# 5. Revisa server.log para debuggear
powershell Get-Content "C:\Users\chuch\Desktop\Code Assistant\server.log" -Wait
```

---

## 📝 Notas

- El servidor LSP se comunica con VS Code via `stdin/stdout` — es normal que no muestre output en terminal
- Todos los logs van a `server.log` en la carpeta del proyecto
- Las API Keys **nunca** deben subirse a GitHub — están protegidas por `.gitignore`
- El entorno `code-assistant` de Anaconda debe estar activo para que el servidor funcione correctamente