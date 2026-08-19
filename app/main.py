from fastapi import FastAPI
from app.api.routes import auth_routes, case_routes # <-- adicione o case_routes aqui

app = FastAPI(
    title="RevEla Analyzer API",
    description="Backend Corporativo para análise de confiabilidade de sistemas elétricos.",
    version="1.0.0"
)

# Registra as rotas
app.include_router(auth_routes.router)
app.include_router(case_routes.router) # <-- Adicione esta linha!

@app.get("/")
def root():
    return {"message": "RevEla Analyzer API está operante!"}