from fastapi import FastAPI
from app.api.routes import auth_routes, case_routes, import_routes # <-- adicione o case_routes aqui
from app.api.routes import analysis_global_routes, analysis_case_routes, analysis_compare_routes
app = FastAPI(
    title="RevEla Analyzer API",
    description="Backend Corporativo para análise de confiabilidade de sistemas elétricos.",
    version="1.0.0"
)

# Registra as rotas
app.include_router(auth_routes.router)
app.include_router(case_routes.router) 
app.include_router(import_routes.router)
app.include_router(analysis_global_routes.router)
app.include_router(analysis_case_routes.router)
app.include_router(analysis_compare_routes.router)


@app.get("/")
def root():
    return {"message": "RevEla Analyzer API está operante!"}