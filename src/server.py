from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .generation import generation
from .index import index
from .retrieval import retrieval
from .types import ChatRequest
from .utils.graph_builder import to_json
from .utils.embedder import get_embedding_model


GRAPH = None
MODEL = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global GRAPH, MODEL

    MODEL = get_embedding_model()
    GRAPH = index(MODEL)
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/graph")
def get_graph():
    return to_json(GRAPH)


@app.post("/chat")
def chat(request: ChatRequest):
    subgraph = retrieval(request.message, MODEL)
    response = generation(request.message, subgraph)
    return {
        "message": response,
        "graph": to_json(subgraph),
    }


@app.get("/")
def health():
    return {"status": "ok"}