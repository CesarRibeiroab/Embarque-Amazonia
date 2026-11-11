"""
Embarque Amazônia — Motor de Roteamento Multimodal de Referência
Módulo oficial da API (Localizado em api/engine/route_engine.py)

Capacidades:
- Lê diretamente do banco de dados relacional (SQLite / PostgreSQL) ou opera em memória
- Previne duplicação de arestas agrupando múltiplos horários por trecho
- Suporta filtragem por modais permitidos
- Calcula rotas multimodais em grafo com no máximo 3 trechos
- Valida conexões temporais reais (rejeita conexão se hora de partida subsequente for anterior à chegada)
- Calcula o tempo de conexão a partir da diferença real entre horários ou do intervalo cadastrado
- Avalia a recência dos dados (data_ultima_atualizacao) para o critério 'Mais confiável'
- Atribui os selos oficiais: 'Menor custo', 'Menor tempo', 'Mais confiável' e 'Desatualizado' (> 30 dias)
- Permite ordenação por 'menor_tempo', 'menor_custo' e 'mais_confiavel'
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import os
import sqlite3
from typing import List, Dict, Optional, Tuple


@dataclass
class Localidade:
    id: int
    nome: str
    uf: str
    polo_regional: bool = False


@dataclass
class Horario:
    hora_partida: str  # 'HH:MM:SS'
    hora_chegada_estimada: Optional[str] = None


@dataclass
class Trecho:
    id: int
    origem_id: int
    destino_id: int
    operador_nome: str
    modal_codigo: str
    modal_nome: str
    duracao_minutos: int
    tarifa_reais: float
    data_ultima_atualizacao: str  # 'YYYY-MM-DD'
    tempo_conexao_espera_minutos: int = 0
    terminal_origem: str = ""
    terminal_destino: str = ""
    observacao_regime: str = ""
    hora_partida: str = "00:00:00"
    hora_chegada: str = "00:00:00"
    dias_semana_mask: int = 127  # Bitmask: Seg=1, Ter=2, Qua=4, Qui=8, Sex=16, Sab=32, Dom=64

    def dias_desde_atualizacao(self, data_ref: Optional[date] = None) -> int:
        try:
            d_at = datetime.strptime(self.data_ultima_atualizacao, "%Y-%m-%d").date()
            ref = data_ref
            if ref is None:
                env_ref = os.getenv("DATA_REFERENCIA")
                if env_ref and env_ref.strip():
                    try:
                        ref = datetime.strptime(env_ref.strip(), "%Y-%m-%d").date()
                    except Exception:
                        ref = date.today()
                else:
                    ref = date.today()
            return max(0, (ref - d_at).days)
        except Exception:
            return 0


@dataclass
class OpcaoRota:
    id: str
    origem_nome: str
    destino_nome: str
    trechos: List[Trecho]
    duracao_total_minutos: int
    custo_total_reais: float
    numero_transbordos: int
    dias_max_desatualizacao: int
    data_atualizacao_iso: str = ""
    selos: List[str] = field(default_factory=list)

    @property
    def duracao_formatada(self) -> str:
        dias = self.duracao_total_minutos // (24 * 60)
        horas = (self.duracao_total_minutos % (24 * 60)) // 60
        mins = self.duracao_total_minutos % 60
        partes = []
        if dias > 0:
            partes.append(f"{dias} d")
        if horas > 0:
            partes.append(f"{horas} h")
        if mins > 0 or not partes:
            partes.append(f"{mins} min")
        return " ".join(partes)

    @property
    def texto_recencia(self) -> str:
        if self.dias_max_desatualizacao == 0:
            return "Atualizado hoje"
        if self.dias_max_desatualizacao == 1:
            return "Atualizado há 1 dia"
        return f"Atualizado há {self.dias_max_desatualizacao} dias"


def calcular_intervalo_conexao(hora_chegada_str: str, hora_partida_prox_str: str) -> Optional[int]:
    """
    Calcula minutos entre a chegada de um trecho e a partida do próximo no mesmo dia.
    Retorna None se a conexão for impossível (partida anterior à chegada).
    """
    try:
        fmt = "%H:%M:%S"
        t_ch = datetime.strptime(hora_chegada_str, fmt)
        t_pa = datetime.strptime(hora_partida_prox_str, fmt)
        diferenca_min = int((t_pa - t_ch).total_seconds() / 60)
        if diferenca_min < 0:
            return None  # Conexão impossível
        return diferenca_min
    except Exception:
        return 0


class MotorRoteamentoMultimodal:
    def __init__(self):
        self.localidades: Dict[int, Localidade] = {}
        self.adjacencia: Dict[int, List[Trecho]] = {}

    def adicionar_localidade(self, loc: Localidade):
        self.localidades[loc.id] = loc
        if loc.id not in self.adjacencia:
            self.adjacencia[loc.id] = []

    def adicionar_trecho(self, trecho: Trecho):
        if trecho.origem_id not in self.adjacencia:
            self.adjacencia[trecho.origem_id] = []
        self.adjacencia[trecho.origem_id].append(trecho)

    def carregar_do_banco(self, db_path: str):
        """
        Carrega localidades e trechos diretamente do banco SQLite de forma idempotente.
        Limpa estruturas em memória antes de recarregar.
        """
        self.localidades.clear()
        self.adjacencia.clear()

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Carregar localidades
        for row in cur.execute("SELECT id, nome, uf, e_polo_regional FROM localidade WHERE ativo = 1"):
            self.adicionar_localidade(Localidade(row[0], row[1], row[2], bool(row[3])))

        # Carregar trechos agrupados (evitando multiplicação por múltiplos horários)
        query = """
            SELECT t.id, t.origem_id, t.destino_id, o.nome_fantasia, m.codigo, m.nome,
                   t.duracao_estimada_minutos, t.tarifa_base_reais, t.data_ultima_atualizacao,
                   t.tempo_conexao_espera_minutos, t.terminal_origem_nome, t.terminal_destino_nome,
                   t.regime_hidrico_observacao,
                   COALESCE((SELECT hora_partida FROM horario_operacao WHERE trecho_id = t.id AND ativo = 1 ORDER BY hora_partida ASC LIMIT 1), '00:00:00') AS h_partida,
                   COALESCE((SELECT hora_chegada_estimada FROM horario_operacao WHERE trecho_id = t.id AND ativo = 1 ORDER BY hora_partida ASC LIMIT 1), '00:00:00') AS h_chegada,
                   COALESCE((SELECT dias_semana_mask FROM horario_operacao WHERE trecho_id = t.id AND ativo = 1 ORDER BY hora_partida ASC LIMIT 1), 127) AS mask_dias
            FROM trecho t
            JOIN operador o ON t.operador_id = o.id
            JOIN modal m ON t.modal_id = m.id
            WHERE t.ativo = 1
        """
        for r in cur.execute(query):
            tr = Trecho(
                id=r[0], origem_id=r[1], destino_id=r[2], operador_nome=r[3], modal_codigo=r[4],
                modal_nome=r[5], duracao_minutos=r[6], tarifa_reais=float(r[7]),
                data_ultima_atualizacao=r[8], tempo_conexao_espera_minutos=r[9],
                terminal_origem=r[10] or "", terminal_destino=r[11] or "",
                observacao_regime=r[12] or "", hora_partida=r[13], hora_chegada=r[14],
                dias_semana_mask=r[15]
            )
            self.adicionar_trecho(tr)

        con.close()

    def _dfs_caminhos(self, atual: int, destino: int, visitados: set, max_trechos: int = 3, modais_permitidos: Optional[set] = None, bit_dia: Optional[int] = None) -> List[List[Trecho]]:
        if atual == destino:
            return [[]]
        if len(visitados) >= max_trechos + 1:
            return []

        caminhos = []
        for tr in self.adjacencia.get(atual, []):
            # Se houver filtro de modais, descarta trechos fora do filtro
            if modais_permitidos is not None and tr.modal_codigo not in modais_permitidos:
                continue

            # Se houver data especificada, valida operação no dia da semana (bitmask)
            if bit_dia is not None and (tr.dias_semana_mask & bit_dia) == 0:
                continue

            prox = tr.destino_id
            if prox not in visitados:
                visitados.add(prox)
                sub_caminhos = self._dfs_caminhos(prox, destino, visitados, max_trechos, modais_permitidos, bit_dia)
                for sc in sub_caminhos:
                    if len(sc) + 1 <= max_trechos:
                        caminhos.append([tr] + sc)
                visitados.remove(prox)
        return caminhos

    def calcular_rotas(
        self,
        origem_id: int,
        destino_id: int,
        criterio: str = "menor_tempo",
        modais_filtro: Optional[List[str]] = None,
        data_viagem: Optional[str] = None,
        data_referencia: Optional[date] = None,
        max_opcoes: int = 5
    ) -> List[OpcaoRota]:
        if origem_id not in self.localidades or destino_id not in self.localidades:
            return []

        # Rejeita busca onde a origem é igual ao destino
        if origem_id == destino_id:
            return []

        modais_permitidos = set(m.strip().lower() for m in modais_filtro if m.strip()) if modais_filtro else None

        # Processar máscara do dia da semana a partir de data_viagem (YYYY-MM-DD)
        bit_dia = None
        if data_viagem:
            try:
                dt_v = datetime.strptime(data_viagem.strip(), "%Y-%m-%d")
                bit_dia = 1 << dt_v.weekday()  # Seg(0)=1, Ter(1)=2, Qua(2)=4, Qui(3)=8, Sex(4)=16, Sab(5)=32, Dom(6)=64
            except Exception:
                bit_dia = None

        caminhos_brutos = self._dfs_caminhos(origem_id, destino_id, {origem_id}, max_trechos=3, modais_permitidos=modais_permitidos, bit_dia=bit_dia)
        if not caminhos_brutos:
            return []

        opcoes: List[OpcaoRota] = []
        for idx, seq_trechos in enumerate(caminhos_brutos):
            duracao_total = 0
            custo_total = 0.0
            pior_recencia = 0
            conexao_invalida = False

            for i, tr in enumerate(seq_trechos):
                # Descartar trechos marcados com erro de conexão
                if tr.tempo_conexao_espera_minutos < 0:
                    conexao_invalida = True
                    break

                duracao_total += tr.duracao_minutos
                custo_total += tr.tarifa_reais
                dias_at = tr.dias_desde_atualizacao(data_referencia)
                if dias_at > pior_recencia:
                    pior_recencia = dias_at

                # Validação de conexão entre trecho i e i+1
                if i < len(seq_trechos) - 1:
                    prox_tr = seq_trechos[i + 1]
                    # Se ambos possuem horários estruturados, calcula intervalo real
                    if tr.hora_chegada != "00:00:00" and prox_tr.hora_partida != "00:00:00":
                        intervalo = calcular_intervalo_conexao(tr.hora_chegada, prox_tr.hora_partida)
                        if intervalo is None:
                            conexao_invalida = True
                            break
                        duracao_total += intervalo
                    else:
                        duracao_total += tr.tempo_conexao_espera_minutos

            if conexao_invalida:
                continue

            num_transbordos = max(0, len(seq_trechos) - 1)
            trecho_ids_str = "-".join(f"t{t.id}" for t in seq_trechos)
            data_mais_antiga = min((t.data_ultima_atualizacao for t in seq_trechos), default="")

            opc = OpcaoRota(
                id=f"rota-{trecho_ids_str}",
                origem_nome=self.localidades[origem_id].nome,
                destino_nome=self.localidades[destino_id].nome,
                trechos=seq_trechos,
                duracao_total_minutos=duracao_total,
                custo_total_reais=round(custo_total, 2),
                numero_transbordos=num_transbordos,
                dias_max_desatualizacao=pior_recencia,
                data_atualizacao_iso=data_mais_antiga,
                selos=[]
            )
            opcoes.append(opc)

        if not opcoes:
            return []

        # Atribuir selos comparativos apenas quando há 2 ou mais opções
        if len(opcoes) >= 2:
            min_tempo = min(o.duracao_total_minutos for o in opcoes)
            min_custo = min(o.custo_total_reais for o in opcoes)
            mais_recente = min(o.dias_max_desatualizacao for o in opcoes)

            for o in opcoes:
                if o.duracao_total_minutos == min_tempo:
                    o.selos.append("Menor tempo")
                if o.custo_total_reais == min_custo:
                    o.selos.append("Menor custo")
                if o.dias_max_desatualizacao == mais_recente:
                    o.selos.append("Mais confiável")

        # Selo 'Desatualizado' aplica-se sempre que passar de 30 dias, inclusive opção única
        for o in opcoes:
            if o.dias_max_desatualizacao > 30:
                o.selos.append("Desatualizado")

        # Ordenação
        if criterio == "menor_custo":
            opcoes.sort(key=lambda x: (x.custo_total_reais, x.duracao_total_minutos))
        elif criterio == "mais_confiavel":
            opcoes.sort(key=lambda x: (x.dias_max_desatualizacao, x.duracao_total_minutos))
        else:  # menor_tempo
            opcoes.sort(key=lambda x: (x.duracao_total_minutos, x.custo_total_reais))

        if max_opcoes and max_opcoes > 0:
            opcoes = opcoes[:max_opcoes]

        return opcoes
