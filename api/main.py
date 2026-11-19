"""
Embarque Amazônia — Implementação da API REST (FastAPI)
Localizado em: api/main.py

Implementa os endpoints essenciais com suporte aos filtros de critérios, modais e data,
consulta direta de rotas por ID determinístico (/api/v1/rotas/{id}),
além de padronizar respostas de erro de acordo com ErroPadrao do openapi.yaml.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import os
import re
import sys
import unicodedata
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, status, Query
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Adiciona o diretório api ao path
sys.path.insert(0, os.path.dirname(__file__))

from engine.route_engine import MotorRoteamentoMultimodal, RotaNaoEncontradaException, OpcaoRota


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
    modal_codigo: str = ""
    modal_categoria: str = ""
    operador_nome: str
    terminal_origem_nome: str = ""
    terminal_destino_nome: str = ""
    duracao_minutos: int
    tarifa_reais: float
    data_ultima_atualizacao: str
    hora_partida: Optional[str] = None
    hora_chegada_estimada: Optional[str] = None
    partida_dia_offset: Optional[int] = None
    chegada_dia_offset: Optional[int] = None
    frequencia_descricao: Optional[str] = None
    dias_semana_mask: int = 127
    acomodacoes: List[Dict[str, Any]] = Field(default_factory=list)
    regime_hidrico_observacao: Optional[str] = None
    telefone_contato: Optional[str] = None
    intervalo_conexao_minutos: Optional[int] = None


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
    selo: List[str] = Field(default_factory=list)
    atualizado_em: str = ""
    data_atualizacao_iso: str = ""
    dias_desde_atualizacao: int = 0
    data_viagem: Optional[str] = None
    hora_partida: Optional[str] = None
    chegada_estimada: Optional[str] = None
    chegada_dia_offset: Optional[int] = None
    chegada_estimada_iso: Optional[str] = None
    trechos: List[TrechoResponse] = Field(default_factory=list)


class ConsultaRotasResponse(BaseModel):
    origem: str
    destino: str
    criterio_ordenacao: str
    total_opcoes: int
    rotas: List[OpcaoRotaResponse]


class ErroPadraoResponse(BaseModel):
    codigo: str
    mensagem: str


def serializar_opcao_rota(opcao: OpcaoRota, motor_inst: MotorRoteamentoMultimodal) -> OpcaoRotaResponse:
    """Função única de serialização de OpcaoRota para OpcaoRotaResponse."""
    trechos_resp: List[TrechoResponse] = []
    detalhes = opcao.detalhes_trechos if opcao.detalhes_trechos else [{"trecho": t} for t in opcao.trechos]

    for i, det in enumerate(detalhes):
        t = det.get("trecho") or opcao.trechos[i]
        orig_nome = motor_inst.localidades[t.origem_id].nome if t.origem_id in motor_inst.localidades else str(t.origem_id)
        dest_nome = motor_inst.localidades[t.destino_id].nome if t.destino_id in motor_inst.localidades else str(t.destino_id)

        trechos_resp.append(TrechoResponse(
            id=t.id,
            origem_nome=orig_nome,
            destino_nome=dest_nome,
            modal_nome=t.modal_nome,
            modal_codigo=t.modal_codigo,
            modal_categoria=t.modal_categoria,
            operador_nome=t.operador_nome,
            terminal_origem_nome=t.terminal_origem,
            terminal_destino_nome=t.terminal_destino,
            duracao_minutos=t.duracao_minutos,
            tarifa_reais=t.tarifa_reais,
            data_ultima_atualizacao=t.data_ultima_atualizacao,
            hora_partida=det.get("hora_partida"),
            hora_chegada_estimada=det.get("hora_chegada_estimada"),
            partida_dia_offset=det.get("partida_dia_offset"),
            chegada_dia_offset=det.get("chegada_dia_offset"),
            frequencia_descricao=t.frequencia_descricao,
            dias_semana_mask=t.dias_semana_mask,
            acomodacoes=t.acomodacoes or [],
            regime_hidrico_observacao=t.regime_hidrico_observacao,
            telefone_contato=t.telefone_contato,
            intervalo_conexao_minutos=det.get("intervalo_conexao_minutos")
        ))

    modais_list = list(dict.fromkeys(t.modal_nome for t in opcao.trechos))

    return OpcaoRotaResponse(
        id=opcao.id,
        origem_nome=opcao.origem_nome,
        destino_nome=opcao.destino_nome,
        modais=modais_list,
        preco_total=opcao.custo_total_reais,
        duracao_total_minutos=opcao.duracao_total_minutos,
        duracao_total_formatada=opcao.duracao_formatada,
        numero_trechos=len(opcao.trechos),
        numero_conexoes=opcao.numero_transbordos,
        selo=opcao.selos,
        atualizado_em=opcao.texto_recencia,
        data_atualizacao_iso=opcao.data_atualizacao_iso,
        dias_desde_atualizacao=opcao.dias_max_desatualizacao,
        data_viagem=opcao.data_viagem,
        hora_partida=opcao.hora_partida,
        chegada_estimada=opcao.chegada_estimada,
        chegada_dia_offset=opcao.chegada_dia_offset,
        chegada_estimada_iso=opcao.chegada_estimada_iso,
        trechos=trechos_resp
    )


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

    rotas_resp = [serializar_opcao_rota(r, motor) for r in rotas_calculadas]

    return ConsultaRotasResponse(
        origem=origem,
        destino=destino,
        criterio_ordenacao=crit_escolhido,
        total_opcoes=len(rotas_resp),
        rotas=rotas_resp
    )


PADRAO_ID_ROTA = re.compile(r"^rota-t\d+(-t\d+)*$")


@app.get(
    "/api/v1/rotas/{id}",
    response_model=OpcaoRotaResponse,
    responses={
        404: {"model": ErroPadraoResponse},
        422: {"model": ErroPadraoResponse},
        503: {"model": ErroPadraoResponse}
    },
    tags=["Passageiro - Roteamento"]
)
def obter_detalhe_rota(
    id: str,
    data: Optional[str] = Query(None, description="Data pretendida da viagem no formato ISO (YYYY-MM-DD)")
):
    """
    Recupera os detalhes completos de uma rota específica a partir de seu ID determinístico.
    Retorna a linha do tempo discriminando paradas, horários acumulados, tempos de conexão e dados cadastrais.
    """
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

    # 1. Validação do formato do ID
    if not id or not PADRAO_ID_ROTA.match(id):
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "PARAMETRO_INVALIDO",
                "mensagem": f"ID de rota '{id}' inválido. Formato esperado: rota-t{{id}} (ex: rota-t3-t4)."
            }
        )

    # 2. Validação da data ISO
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

    # 3. Extração dos IDs numéricos dos trechos
    trecho_ids = [int(num) for num in re.findall(r"\d+", id)]

    try:
        rota_opcao = motor.obter_rota_por_ids(trecho_ids, data_viagem=data)
    except RotaNaoEncontradaException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "codigo": "ROTA_NAO_ENCONTRADA",
                "mensagem": str(e.mensagem)
            }
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "PARAMETRO_INVALIDO",
                "mensagem": str(ve)
            }
        )

    return serializar_opcao_rota(rota_opcao, motor)
