# server.py
import os
from pygls.lsp.server import LanguageServer
from lsprotocol import types
from dotenv import load_dotenv
import logging
from agent import get_explanation, get_completion, get_tests, get_fix

load_dotenv()

LOG_PATH = r"C:\Users\chuch\Desktop\Code Assistant\server.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    force=True
)
log = logging.getLogger(__name__)
log.info("=== server.py importado ===")

server = LanguageServer("code-assistant", "v0.1")

# ─── Cache de explicaciones ───────────────────────────────────
_explanation_cache: dict[str, str] = {}


# ─── EVENTO: Usuario abrió un archivo ────────────────────────
@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(params: types.DidOpenTextDocumentParams):
    log.info("Archivo abierto: %s", params.text_document.uri)


# ─── EVENTO: Usuario modificó un archivo ─────────────────────
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: types.DidChangeTextDocumentParams):
    log.info("Archivo modificado: %s", params.text_document.uri)


# ─── FEATURE: Autocompletado — solo Ctrl+K Alt+C ─────────────
@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(trigger_characters=[]),
)
def completions(params: types.CompletionParams):
    log.info("Completion pedido (manual)")

    doc = server.workspace.get_text_document(params.text_document.uri)
    code = doc.source
    line = params.position.line
    char = params.position.character
    current_line = doc.lines[line][:char] if line < len(doc.lines) else ""

    try:
        suggestion = get_completion(code, current_line)
        log.info("Completion recibido")
    except Exception as e:
        log.error("Error en completion: %s", e)
        return types.CompletionList(is_incomplete=False, items=[])

    if not suggestion:
        return types.CompletionList(is_incomplete=False, items=[])

    return types.CompletionList(
        is_incomplete=False,
        items=[
            types.CompletionItem(
                label=suggestion[:60],
                kind=types.CompletionItemKind.Text,
                detail="Code Assistant ✨",
                insert_text=suggestion,
                insert_text_format=types.InsertTextFormat.PlainText,
            )
        ],
    )


@server.command("server.explain")
def cmd_explain(ls, *args):
    log.info("Args recibidos: %s", args)
    uri = args[0] if len(args) > 0 else ""
    code = args[1] if len(args) > 1 else ""
    log.info("CODE: %s", code[:100])

    try:
        if not code.strip():
            return {"error": "⚠️ Selecciona código primero"}
        explanation = get_explanation(code)
        return {"result": f"💡 Explicación:\n\n{explanation}"}
    except Exception as e:
        log.error(str(e))
        return {"error": str(e)}


@server.command("server.fixBug")
def cmd_fix(ls, *args):
    log.info("Args recibidos: %s", args)
    uri = args[0] if len(args) > 0 else ""
    code = args[1] if len(args) > 1 else ""
    log.info("CODE: %s", code[:100] if code else "vacío")

    try:
        if not code.strip():
            return {"error": "⚠️ Selecciona código primero"}
        fix = get_fix(code, "Revisa el código y corrige cualquier bug")
        return {"result": f"🔧 Fix sugerido:\n\n{fix}"}
    except Exception as e:
        log.error("Error en fix: %s", e)
        return {"error": str(e)}


@server.command("server.generateTests")
def cmd_tests(ls, *args):
    log.info("Args recibidos: %s", args)
    uri = args[0] if len(args) > 0 else ""
    code = args[1] if len(args) > 1 else ""
    log.info("CODE: %s", code[:100] if code else "vacío")

    try:
        if not code.strip():
            return {"error": "⚠️ Selecciona código primero"}
        tests = get_tests(code)
        return {"result": f"🧪 Tests generados:\n\n{tests}"}
    except Exception as e:
        log.error("Error generando tests: %s", e)
        return {"error": str(e)}


# ─── ARRANCAR EL SERVIDOR ────────────────────────────────────
if __name__ == "__main__":
    log.info("=== Servidor LSP arrancando ===")
    server.start_io()