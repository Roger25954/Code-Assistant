# server.py
import os
from pygls.lsp.server import LanguageServer
from lsprotocol import types
from dotenv import load_dotenv
import logging

load_dotenv()

# Ruta absoluta — siempre sabe dónde escribir
LOG_PATH = r"C:\Users\chuch\Desktop\Code Assistant\server.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    force=True
)
log = logging.getLogger(__name__)
log.info("=== server.py importado ===")  # ← se ejecuta al importar

server = LanguageServer("code-assistant", "v0.1")


@server.feature(types.INITIALIZE)
def initialize(params: types.InitializeParams):
    log.info("Cliente conectado: %s", params.client_info)


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(params: types.DidOpenTextDocumentParams):
    log.info("Archivo abierto: %s", params.text_document.uri)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: types.DidChangeTextDocumentParams):
    log.info("Archivo modificado: %s", params.text_document.uri)


@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(trigger_characters=[".", " ", "("]),
)
def completions(params: types.CompletionParams):
    log.info("Completion pedido en: %s", params.position)
    return types.CompletionList(
        is_incomplete=False,
        items=[
            types.CompletionItem(
                label="print()",
                kind=types.CompletionItemKind.Function,
                detail="Imprimir en consola",
                insert_text="print($1)",
                insert_text_format=types.InsertTextFormat.Snippet,
            ),
            types.CompletionItem(
                label="def función()",
                kind=types.CompletionItemKind.Snippet,
                detail="Definir una función",
                insert_text="def ${1:nombre}(${2:params}):\n    ${3:pass}",
                insert_text_format=types.InsertTextFormat.Snippet,
            ),
        ],
    )


@server.feature(types.TEXT_DOCUMENT_HOVER)
def hover(params: types.HoverParams):
    log.info("Hover pedido")
    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value="🤖 **Code Assistant** listo — Gemini se conecta aquí pronto",
        )
    )


if __name__ == "__main__":
    log.info("=== Servidor LSP arrancando ===")
    server.start_io()