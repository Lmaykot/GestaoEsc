from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import clientes, contratos, honorarios, parcelas, relatorio

app = FastAPI(title="GestaoEsc API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(contratos.router)
app.include_router(honorarios.router)
app.include_router(parcelas.router)
app.include_router(relatorio.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
