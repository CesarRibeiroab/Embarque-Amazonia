"""
Embarque Amazônia — Implementação da API REST (FastAPI)
Localizado em: api/main.py

Implementa os endpoints essenciais com suporte aos filtros de critérios, modais e data,
além de padronizar respostas de erro de acordo com ErroPadrao do openapi.yaml.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys
import unicodedata
from typing import List, Optional
from fastapi import FastAPI, Request, status, Query
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Adiciona o diretório api ao path
sys.path.insert(0, os.path.dirname(__file__))

from engine.route_engine import MotorRoteamentoMultimodal


def normalizar_texto(texto: Optional[str]) -> str:
    """Normaliza texto removendo acentos e convertendo para minúsculas."""
    if not texto:
        return ""
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').strip().lower()


# Caminho dinâmico para a base relacional
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "embarque.db"))

# Inicializa o motor de rotas
motor = MotorRoteamentoMultimodal()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação carregando a base se existente."""
    if os.path.exists(DB_PATH):
        motor.carregar_do_banco(DB_PATH)
    yield


app = FastAPI(
    title="Embarque Amazônia — REST API",
    description="API de Roteamento Multimodal e Gestão de Malha de Transportes para a Amazônia Legal",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração de CORS (libera porta padrão do Vite e origens configuradas)
cors_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LocalidadeResponse(BaseModel):
    id: int
    nome: str
    uf: str
    e_polo_regional: bool


class TrechoResponse(BaseModel):
    id: int
    origem_nome: str
    destino_nome: str
    modal_nome: str
    operador_nome: str
    terminal_origem_nome: str
    terminal_destino_nome: str
    duracao_minutos: int
    tarifa_reais: float
    data_ultima_atualizacao: str


class OpcaoRotaResponse(BaseModel):
    id: str
    origem_nome: str
    destino_nome: str
    modais: List[str]
    preco_total: float
    duracao_total_minutos: int
    duracao_total_formatada: str
    numero_trechos: int
    numero_conexoes: int
    selo: List[str]
    atualizado_em: str
    data_atualizacao_iso: str
    dias_desde_atualizacao: int
    trechos: List[TrechoResponse]


class ConsultaRotasResponse(BaseModel):
    origem: str
    destino: str
    criterio_ordenacao: str
    total_opcoes: int
    rotas: List[OpcaoRotaResponse]


class ErroPadraoResponse(BaseModel):
    codigo: str
    mensagem: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Padroniza erros 422 de parâmetros ausentes ou malformados nas rotas /api/v1/*."""
    if not request.url.path.startswith("/api/v1/"):
        return await request_validation_exception_handler(request, exc)

    erros = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "query")
        msg = err.get("msg", "Parâmetro inválido")
        erros.append(f"{loc}: {msg}" if loc else msg)
    detalhe = "; ".join(erros) if erros else "Parâmetros obrigatórios ausentes ou inválidos."
    return JSONResponse(
        status_code=422,
        content={
            "codigo": "PARAMETRO_INVALIDO",
            "mensagem": f"Parâmetro inválido ou ausente: {detalhe}"
        }
    )


@app.get("/api/v1/localidades", response_model=List[LocalidadeResponse], responses={503: {"model": ErroPadraoResponse}}, tags=["Passageiro - Localidades"])
def listar_localidades(busca: Optional[str] = Query(None, description="Termo para autocompletar nome da localidade")):
    if not os.path.exists(DB_PATH):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "codigo": "BANCO_INDISPONIVEL",
                "mensagem": "Base de dados relacional indisponível ou não inicializada. Execute python database/init_db.py."
            }
        )

    if not motor.localidades:
        motor.carregar_do_banco(DB_PATH)

    res = []
    termo_busca = normalizar_texto(busca) if busca else None
    for loc in motor.localidades.values():
        if termo_busca:
            if termo_busca in normalizar_texto(loc.nome):
                res.append(LocalidadeResponse(id=loc.id, nome=loc.nome, uf=loc.uf, e_polo_regional=loc.polo_regional))
        else:
            res.append(LocalidadeResponse(id=loc.id, nome=loc.nome, uf=loc.uf, e_polo_regional=loc.polo_regional))
    return res


@app.get("/api/v1/rotas", response_model=ConsultaRotasResponse, responses={404: {"model": ErroPadraoResponse}, 422: {"model": ErroPadraoResponse}, 503: {"model": ErroPadraoResponse}}, tags=["Passageiro - Roteamento"])
def buscar_rotas(
    origem: str = Query(..., min_length=1, description="Nome da localidade de origem (ex. Belém)"),
    destino: str = Query(..., min_length=1, description="Nome da localidade de destino (ex. Manaus)"),
    data: Optional[str] = Query(None, description="Data pretendida da viagem no formato ISO (YYYY-MM-DD)"),
    criterio: Optional[str] = Query("menor_tempo", description="menor_tempo | menor_custo | mais_confiavel"),
    modais: Optional[str] = Query(None, description="Modais permitidos separados por vírgula (ex: aviao_regional,barco_regional)")
):
    if not os.path.exists(DB_PATH):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "codigo": "BANCO_INDISPONIVEL",
                "mensagem": "Base de dados relacional indisponível ou não inicializada. Execute python database/init_db.py."
            }
        )

    if not motor.localidades:
        motor.carregar_do_banco(DB_PATH)

    # 1. Validação: Origem e Destino preenchidos e distintos
    origem_norm = normalizar_texto(origem)
    destino_norm = normalizar_texto(destino)
    if not origem_norm or not destino_norm:
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "PARAMETRO_INVALIDO",
                "mensagem": "Origem e destino são obrigatórios."
            }
        )
    if origem_norm == destino_norm:
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "PARAMETRO_INVALIDO",
                "mensagem": "Origem e destino não podem ser a mesma localidade."
            }
        )

    # 2. Validação: Critério válido
    criterios_validos = {"menor_tempo", "menor_custo", "mais_confiavel"}
    crit_escolhido = criterio.strip().lower() if criterio else "menor_tempo"
    if crit_escolhido not in criterios_validos:
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "PARAMETRO_INVALIDO",
                "mensagem": f"Critério '{criterio}' inválido. Valores permitidos: {', '.join(sorted(criterios_validos))}."
            }
        )

    # 3. Validação: Formato de data ISO
    if data:
        try:
            datetime.strptime(data.strip(), "%Y-%m-%d")
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={
                    "codigo": "PARAMETRO_INVALIDO",
                    "mensagem": f"Formato de data '{data}' inválido. Utilize o padrão ISO YYYY-MM-DD (ex: 2026-11-20)."
                }
            )

    # 4. Localizar IDs das localidades
    origem_id = None
    destino_id = None
    for loc_id, loc in motor.localidades.items():
        loc_norm = normalizar_texto(loc.nome)
        if loc_norm == origem_norm:
            origem_id = loc_id
        if loc_norm == destino_norm:
            destino_id = loc_id

    if not origem_id or not destino_id:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"codigo": "LOCALIDADE_NAO_ENCONTRADA", "mensagem": "Origem ou destino não localizados na malha de transporte."}
        )

    # Processar filtro de modais se fornecido
    modais_lista = [m.strip().lower() for m in modais.split(",") if m.strip()] if modais else []
    modais_filtro = modais_lista or None

    rotas_calculadas = motor.calcular_rotas(
        origem_id=origem_id,
        destino_id=destino_id,
        criterio=crit_escolhido,
        modais_filtro=modais_filtro,
        data_viagem=data
    )

    # Se não houver rotas viáveis, retorna 200 OK com lista vazia (conforme tela P10a 'sem resultados')
    if not rotas_calculadas:
        return ConsultaRotasResponse(
            origem=origem,
            destino=destino,
            criterio_ordenacao=crit_escolhido,
            total_opcoes=0,
            rotas=[]
        )

    # Mapear para a estrutura do contrato OpenAPI
    rotas_resp = []
    for r in rotas_calculadas:
        modais_list = list(dict.fromkeys(t.modal_nome for t in r.trechos))
        trechos_resp = [
            TrechoResponse(
                id=t.id,
                origem_nome=motor.localidades[t.origem_id].nome,
                destino_nome=motor.localidades[t.destino_id].nome,
                modal_nome=t.modal_nome,
                operador_nome=t.operador_nome,
                terminal_origem_nome=t.terminal_origem,
                terminal_destino_nome=t.terminal_destino,
                duracao_minutos=t.duracao_minutos,
                tarifa_reais=t.tarifa_reais,
                data_ultima_atualizacao=t.data_ultima_atualizacao
            ) for t in r.trechos
        ]

        rotas_resp.append(OpcaoRotaResponse(
            id=r.id,
            origem_nome=r.origem_nome,
            destino_nome=r.destino_nome,
            modais=modais_list,
            preco_total=r.custo_total_reais,
            duracao_total_minutos=r.duracao_total_minutos,
            duracao_total_formatada=r.duracao_formatada,
            numero_trechos=len(r.trechos),
            numero_conexoes=r.numero_transbordos,
            selo=r.selos,
            atualizado_em=r.texto_recencia,
            data_atualizacao_iso=r.data_atualizacao_iso,
            dias_desde_atualizacao=r.dias_max_desatualizacao,
            trechos=trechos_resp
        ))

    return ConsultaRotasResponse(
        origem=origem,
        destino=destino,
        criterio_ordenacao=crit_escolhido,
        total_opcoes=len(rotas_resp),
        rotas=rotas_resp
    )
