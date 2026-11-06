"""
Embarque Amazônia — Implementação de Referência da API REST (FastAPI)
Localizado em: api/main.py

Endpoints:
  - GET /api/v1/localidades: Listagem com filtro por busca textual
  - GET /api/v1/rotas: Busca multimodal consumindo o motor em grafo com ordenação
"""

import os
import sys
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# Adiciona o diretório api ao path
sys.path.insert(0, os.path.dirname(__file__))

from engine.route_engine import MotorRoteamentoMultimodal

app = FastAPI(
    title="Embarque Amazônia — REST API",
    description="API de Roteamento Multimodal e Gestão de Malha de Transportes para a Amazônia Legal",
    version="1.0.0"
)

# Caminho para a base relacional
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "embarque.db"))

# Inicializa o motor de rotas
motor = MotorRoteamentoMultimodal()


@app.on_event("startup")
def startup_event():
    if os.path.exists(DB_PATH):
        motor.carregar_do_banco(DB_PATH)


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
    trechos: List[TrechoResponse]


class ConsultaRotasResponse(BaseModel):
    origem: str
    destino: str
    criterio_ordenacao: str
    total_opcoes: int
    rotas: List[OpcaoRotaResponse]


@app.get("/api/v1/localidades", response_model=List[LocalidadeResponse], tags=["Passageiro - Localidades"])
def listar_localidades(busca: Optional[str] = Query(None, description="Termo para autocompletar nome da localidade")):
    if not motor.localidades and os.path.exists(DB_PATH):
        motor.carregar_do_banco(DB_PATH)

    res = []
    for loc in motor.localidades.values():
        if busca:
            if busca.lower() in loc.nome.lower():
                res.append(LocalidadeResponse(id=loc.id, nome=loc.nome, uf=loc.uf, e_polo_regional=loc.polo_regional))
        else:
            res.append(LocalidadeResponse(id=loc.id, nome=loc.nome, uf=loc.uf, e_polo_regional=loc.polo_regional))
    return res


@app.get("/api/v1/rotas", response_model=ConsultaRotasResponse, tags=["Passageiro - Roteamento"])
def buscar_rotas(
    origem: str = Query(..., description="Nome da localidade de origem"),
    destino: str = Query(..., description="Nome da localidade de destino"),
    data: Optional[str] = Query(None, description="Data pretendida da viagem (YYYY-MM-DD)"),
    criterio: Optional[str] = Query("menor_tempo", description="menor_tempo | menor_custo | mais_confiavel"),
    modais: Optional[str] = Query(None, description="Modais permitidos separados por vírgula")
):
    if not motor.localidades and os.path.exists(DB_PATH):
        motor.carregar_do_banco(DB_PATH)

    # Localizar IDs das localidades pelo nome
    origem_id = None
    destino_id = None
    for loc_id, loc in motor.localidades.items():
        if loc.nome.lower() == origem.strip().lower():
            origem_id = loc_id
        if loc.nome.lower() == destino.strip().lower():
            destino_id = loc_id

    if not origem_id or not destino_id:
        raise HTTPException(status_code=404, detail="Origem ou destino não localizados na malha de transporte.")

    rotas_calculadas = motor.calcular_rotas(origem_id=origem_id, destino_id=destino_id, criterio=criterio)

    if not rotas_calculadas:
        raise HTTPException(status_code=404, detail="Nenhuma rota viável encontrada entre a origem e o destino.")

    # Mapear para o formato exato exigido no Card 7 do Trello
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
            trechos=trechos_resp
        ))

    return ConsultaRotasResponse(
        origem=origem,
        destino=destino,
        criterio_ordenacao=criterio,
        total_opcoes=len(rotas_resp),
        rotas=rotas_resp
    )
