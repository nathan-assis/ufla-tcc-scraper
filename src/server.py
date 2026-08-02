from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .graph_builder import load_graph, to_json


GRAPH = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global GRAPH
    GRAPH = load_graph()
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


@app.get("/")
def health():
    return {"status": "ok"}