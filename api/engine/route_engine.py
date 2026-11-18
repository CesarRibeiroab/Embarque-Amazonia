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
- Suporta busca direta por IDs de trechos (obter_rota_por_ids) com validação estrita
- Calcula horários e offsets acumulados de dia (partida_dia_offset, chegada_dia_offset, chegada_estimada_iso)
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import os
import sqlite3
from typing import List, Dict, Optional, Tuple, Any


class RotaNaoEncontradaException(Exception):
    """Exceção levantada quando uma rota não pode ser montada ou não opera na data."""
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


@dataclass
class Localidade:
    id: int
    nome: str
    uf: str
    polo_regional: bool = False


@dataclass
class Horario:
    hora_partida: str  # 'HH:MM:SS' ou 'HH:MM'
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
    hora_partida: Optional[str] = "00:00:00"
    hora_chegada: Optional[str] = "00:00:00"
    dias_semana_mask: int = 127  # Bitmask: Seg=1, Ter=2, Qua=4, Qui=8, Sex=16, Sab=32, Dom=64
    modal_categoria: str = ""
    frequencia_descricao: Optional[str] = None
    acomodacoes: List[Dict[str, Any]] = field(default_factory=list)
    telefone_contato: Optional[str] = None
    tem_horario: bool = True

    def __post_init__(self):
        # Se hora_partida for None, vazia ou se explicitamente marcado sem horário
        if self.hora_partida is None or self.hora_partida == "" or not self.tem_horario:
            self.tem_horario = False
            self.hora_partida = None
            self.hora_chegada = None

    @property
    def regime_hidrico_observacao(self) -> str:
        return self.observacao_regime

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
    data_viagem: Optional[str] = None
    hora_partida: Optional[str] = None
    chegada_estimada: Optional[str] = None
    chegada_dia_offset: Optional[int] = None
    chegada_estimada_iso: Optional[str] = None
    detalhes_trechos: List[Dict[str, Any]] = field(default_factory=list)

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


def parse_hora_minutos(hora_str: Optional[str]) -> Optional[int]:
    """Converte 'HH:MM:SS' ou 'HH:MM' em minutos desde 00:00. Retorna None se inválido."""
    if not hora_str:
        return None
    partes = str(hora_str).strip().split(":")
    if len(partes) < 2:
        return None
    try:
        h, m = int(partes[0]), int(partes[1])
        return h * 60 + m
    except ValueError:
        return None


def formatar_minutos_hh_mm(minutos: int) -> str:
    """Formata minutos dentro do dia (0..1439) em 'HH:MM'."""
    m_dia = minutos % 1440
    h = m_dia // 60
    m = m_dia % 60
    return f"{h:02d}:{m:02d}"


def calcular_intervalo_conexao(hora_chegada_str: str, hora_partida_prox_str: str) -> Optional[int]:
    """
    Calcula minutos entre a chegada de um trecho e a partida do próximo no mesmo dia.
    Retorna None se a conexão for impossível (partida anterior à chegada).
    Compatível com formatos 'HH:MM:SS' e 'HH:MM'.
    """
    try:
        t_ch = parse_hora_minutos(hora_chegada_str)
        t_pa = parse_hora_minutos(hora_partida_prox_str)
        if t_ch is None or t_pa is None:
            return 0
        diferenca_min = t_pa - t_ch
        if diferenca_min < 0:
            return None  # Conexão impossível no mesmo dia
        return diferenca_min
    except Exception:
        return 0


def obter_intervalo_entre_trechos(tr_anterior: Trecho, tr_proximo: Trecho) -> Tuple[Optional[int], bool]:
    """
    Função única para cálculo do intervalo de conexão (em minutos) entre dois trechos consecutivos.
    Retorna (intervalo_minutos, conexao_valida).
    Se a conexão for temporalmente impossível, retorna (None, False).
    """
    if tr_anterior.tempo_conexao_espera_minutos < 0:
        return None, False

    if (tr_anterior.tem_horario and tr_proximo.tem_horario and
            tr_anterior.hora_chegada not in (None, "", "00:00:00") and
            tr_proximo.hora_partida not in (None, "", "00:00:00")):
        intervalo = calcular_intervalo_conexao(tr_anterior.hora_chegada, tr_proximo.hora_partida)
        if intervalo is None:
            return None, False
        return intervalo, True
    else:
        return tr_anterior.tempo_conexao_espera_minutos, True


def montar_opcao_rota(
    seq_trechos: List[Trecho],
    localidades: Dict[int, Localidade],
    data_viagem: Optional[str] = None,
    data_referencia: Optional[date] = None
) -> Optional[OpcaoRota]:
    """
    Função compartilhada para construir um objeto OpcaoRota a partir de uma sequência de trechos.
    Calcula durações, tarifas, intervalos de conexão, horários acumulados, offsets e recência.
    Retorna None se a sequência violar regras de conexão temporal.
    """
    if not seq_trechos:
        return None

    origem_id = seq_trechos[0].origem_id
    destino_id = seq_trechos[-1].destino_id
    origem_nome = localidades[origem_id].nome if origem_id in localidades else str(origem_id)
    destino_nome = localidades[destino_id].nome if destino_id in localidades else str(destino_id)

    duracao_total = 0
    custo_total = 0.0
    pior_recencia = 0
    intervalos: List[Optional[int]] = []

    for i, tr in enumerate(seq_trechos):
        duracao_total += tr.duracao_minutos
        custo_total += tr.tarifa_reais
        dias_at = tr.dias_desde_atualizacao(data_referencia)
        if dias_at > pior_recencia:
            pior_recencia = dias_at

        if i < len(seq_trechos) - 1:
            intervalo, valido = obter_intervalo_entre_trechos(tr, seq_trechos[i + 1])
            if not valido or intervalo is None:
                return None
            duracao_total += intervalo
            intervalos.append(intervalo)
        else:
            intervalos.append(None)

    # Cálculo dos horários e offsets
    tem_horarios_validos = (
        seq_trechos[0].tem_horario and
        seq_trechos[0].hora_partida not in (None, "", "00:00:00")
    )

    detalhes_trechos: List[Dict[str, Any]] = []

    if tem_horarios_validos:
        partida_inicial_min = parse_hora_minutos(seq_trechos[0].hora_partida)
    else:
        partida_inicial_min = None

    if partida_inicial_min is not None:
        acumulado_min = partida_inicial_min
        for i, tr in enumerate(seq_trechos):
            p_min = acumulado_min
            p_offset = p_min // 1440
            p_hora = formatar_minutos_hh_mm(p_min)

            c_min = p_min + tr.duracao_minutos
            c_offset = c_min // 1440
            c_hora = formatar_minutos_hh_mm(c_min)

            interv = intervalos[i]
            if interv is not None:
                acumulado_min = c_min + interv

            detalhes_trechos.append({
                "trecho": tr,
                "hora_partida": p_hora,
                "hora_chegada_estimada": c_hora,
                "partida_dia_offset": p_offset,
                "chegada_dia_offset": c_offset,
                "intervalo_conexao_minutos": interv
            })

        rota_hora_partida = detalhes_trechos[0]["hora_partida"]
        rota_chegada_estimada = detalhes_trechos[-1]["hora_chegada_estimada"]
        rota_chegada_dia_offset = detalhes_trechos[-1]["chegada_dia_offset"]

        if data_viagem:
            try:
                dt_partida = datetime.strptime(data_viagem.strip(), "%Y-%m-%d")
                dt_chegada = dt_partida + timedelta(days=rota_chegada_dia_offset)
                rota_chegada_iso = f"{dt_chegada.strftime('%Y-%m-%d')}T{rota_chegada_estimada}"
            except Exception:
                rota_chegada_iso = None
        else:
            rota_chegada_iso = None
    else:
        for i, tr in enumerate(seq_trechos):
            detalhes_trechos.append({
                "trecho": tr,
                "hora_partida": None,
                "hora_chegada_estimada": None,
                "partida_dia_offset": None,
                "chegada_dia_offset": None,
                "intervalo_conexao_minutos": intervalos[i]
            })
        rota_hora_partida = None
        rota_chegada_estimada = None
        rota_chegada_dia_offset = None
        rota_chegada_iso = None

    num_transbordos = max(0, len(seq_trechos) - 1)
    trecho_ids_str = "-".join(f"t{t.id}" for t in seq_trechos)
    data_mais_antiga = min((t.data_ultima_atualizacao for t in seq_trechos), default="")

    return OpcaoRota(
        id=f"rota-{trecho_ids_str}",
        origem_nome=origem_nome,
        destino_nome=destino_nome,
        trechos=seq_trechos,
        duracao_total_minutos=duracao_total,
        custo_total_reais=round(custo_total, 2),
        numero_transbordos=num_transbordos,
        dias_max_desatualizacao=pior_recencia,
        data_atualizacao_iso=data_mais_antiga,
        selos=[],
        data_viagem=data_viagem,
        hora_partida=rota_hora_partida,
        chegada_estimada=rota_chegada_estimada,
        chegada_dia_offset=rota_chegada_dia_offset,
        chegada_estimada_iso=rota_chegada_iso,
        detalhes_trechos=detalhes_trechos
    )


class MotorRoteamentoMultimodal:
    def __init__(self):
        self.localidades: Dict[int, Localidade] = {}
        self.adjacencia: Dict[int, List[Trecho]] = {}
        self.trechos_por_id: Dict[int, Trecho] = {}

    def adicionar_localidade(self, loc: Localidade):
        self.localidades[loc.id] = loc
        if loc.id not in self.adjacencia:
            self.adjacencia[loc.id] = []

    def adicionar_trecho(self, trecho: Trecho):
        if trecho.origem_id not in self.adjacencia:
            self.adjacencia[trecho.origem_id] = []
        self.adjacencia[trecho.origem_id].append(trecho)
        self.trechos_por_id[trecho.id] = trecho

    def carregar_do_banco(self, db_path: str):
        """
        Carrega localidades, acomodações, horários e trechos diretamente do banco SQLite.
        A recarga é idempotente e limpa todas as estruturas em memória antes de recarregar.
        """
        self.localidades.clear()
        self.adjacencia.clear()
        self.trechos_por_id.clear()

        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # 1. Carregar localidades
        for row in cur.execute("SELECT id, nome, uf, e_polo_regional FROM localidade WHERE ativo = 1"):
            self.adicionar_localidade(Localidade(row[0], row[1], row[2], bool(row[3])))

        # 2. Carregar acomodações agrupadas por trecho
        acomodacoes_por_trecho: Dict[int, List[Dict[str, Any]]] = {}
        for row_ac in cur.execute("SELECT trecho_id, tipo, regime, valor_total_reais, descricao FROM acomodacao_trecho ORDER BY id ASC"):
            t_id = row_ac[0]
            if t_id not in acomodacoes_por_trecho:
                acomodacoes_por_trecho[t_id] = []
            acomodacoes_por_trecho[t_id].append({
                "tipo": row_ac[1],
                "regime": row_ac[2] or "fixo",
                "valor_total_reais": float(row_ac[3]),
                "descricao": row_ac[4] or ""
            })

        # 3. Carregar horários: primeiro horário ativo de cada trecho (menor hora_partida)
        primeiro_horario_por_trecho: Dict[int, Tuple[str, str, int, Optional[str]]] = {}
        for row_h in cur.execute("""
            SELECT trecho_id, hora_partida, hora_chegada_estimada, dias_semana_mask, frequencia_descricao
            FROM horario_operacao
            WHERE ativo = 1
            ORDER BY trecho_id, hora_partida ASC
        """):
            t_id = row_h[0]
            if t_id not in primeiro_horario_por_trecho:
                primeiro_horario_por_trecho[t_id] = (
                    row_h[1],
                    row_h[2],
                    row_h[3] if row_h[3] is not None else 127,
                    row_h[4]
                )

        # 4. Carregar trechos
        query = """
            SELECT t.id, t.origem_id, t.destino_id, o.nome_fantasia, m.codigo, m.nome,
                   t.duracao_estimada_minutos, t.tarifa_base_reais, t.data_ultima_atualizacao,
                   t.tempo_conexao_espera_minutos, t.terminal_origem_nome, t.terminal_destino_nome,
                   t.regime_hidrico_observacao, m.categoria, o.telefone_contato
            FROM trecho t
            JOIN operador o ON t.operador_id = o.id
            JOIN modal m ON t.modal_id = m.id
            WHERE t.ativo = 1
        """
        for r in cur.execute(query):
            t_id = r[0]
            horario_info = primeiro_horario_por_trecho.get(t_id)
            if horario_info:
                tem_horario = True
                h_partida = horario_info[0]
                h_chegada = horario_info[1]
                mask_dias = horario_info[2]
                freq_desc = horario_info[3]
            else:
                tem_horario = False
                h_partida = None
                h_chegada = None
                mask_dias = 127
                freq_desc = None

            tr = Trecho(
                id=t_id,
                origem_id=r[1],
                destino_id=r[2],
                operador_nome=r[3],
                modal_codigo=r[4],
                modal_nome=r[5],
                duracao_minutos=r[6],
                tarifa_reais=float(r[7]),
                data_ultima_atualizacao=r[8],
                tempo_conexao_espera_minutos=r[9],
                terminal_origem=r[10] or "",
                terminal_destino=r[11] or "",
                observacao_regime=r[12] or "",
                hora_partida=h_partida,
                hora_chegada=h_chegada,
                dias_semana_mask=mask_dias,
                modal_categoria=r[13] or "",
                frequencia_descricao=freq_desc,
                acomodacoes=acomodacoes_por_trecho.get(t_id, []),
                telefone_contato=r[14],
                tem_horario=tem_horario
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
            if modais_permitidos is not None and tr.modal_codigo not in modais_permitidos:
                continue

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

        if origem_id == destino_id:
            return []

        modais_permitidos = set(m.strip().lower() for m in modais_filtro if m.strip()) if modais_filtro else None

        bit_dia = None
        if data_viagem:
            try:
                dt_v = datetime.strptime(data_viagem.strip(), "%Y-%m-%d")
                bit_dia = 1 << dt_v.weekday()
            except Exception:
                bit_dia = None

        caminhos_brutos = self._dfs_caminhos(
            origem_id,
            destino_id,
            {origem_id},
            max_trechos=3,
            modais_permitidos=modais_permitidos,
            bit_dia=bit_dia
        )
        if not caminhos_brutos:
            return []

        opcoes: List[OpcaoRota] = []
        for seq_trechos in caminhos_brutos:
            opc = montar_opcao_rota(
                seq_trechos=seq_trechos,
                localidades=self.localidades,
                data_viagem=data_viagem,
                data_referencia=data_referencia
            )
            if opc is not None:
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

        # Selo 'Desatualizado' aplica-se sempre que passar de 30 dias
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

    def obter_rota_por_ids(
        self,
        ids: List[int],
        data_viagem: Optional[str] = None,
        data_referencia: Optional[date] = None
    ) -> OpcaoRota:
        """
        Retorna uma OpcaoRota com base nos IDs dos trechos fornecidos, aplicando validações estritas:
        - Existência de cada trecho na malha ativa
        - Encadeamento contínuo (destino do trecho i == origem do trecho i+1)
        - Ausência de ciclos (nenhuma localidade visitada mais de uma vez)
        - Conexão temporalmente possível
        - Operação no dia da semana especificado (quando data_viagem for informada)
        - Preservação de selos comparativos calculados a partir da busca de alternativas
        """
        if not ids or len(ids) > 3:
            raise RotaNaoEncontradaException("A rota deve conter entre 1 e 3 trechos.")

        seq_trechos: List[Trecho] = []
        for t_id in ids:
            if t_id not in self.trechos_por_id:
                raise RotaNaoEncontradaException(f"Trecho com ID {t_id} não encontrado ou inativo.")
            seq_trechos.append(self.trechos_por_id[t_id])

        # Encadeamento
        for i in range(len(seq_trechos) - 1):
            if seq_trechos[i].destino_id != seq_trechos[i + 1].origem_id:
                raise RotaNaoEncontradaException("Os trechos informados não se encadeiam continuamente.")

        # Sem localidades repetidas
        locs = [seq_trechos[0].origem_id] + [t.destino_id for t in seq_trechos]
        if len(locs) != len(set(locs)):
            raise RotaNaoEncontradaException("A rota não pode conter ciclos ou localidades repetidas.")

        # Validação temporal de conexão
        for i in range(len(seq_trechos) - 1):
            _, valida = obter_intervalo_entre_trechos(seq_trechos[i], seq_trechos[i + 1])
            if not valida:
                raise RotaNaoEncontradaException("Conexão temporalmente impossível entre os trechos.")

        # Validação de operação no dia da semana
        if data_viagem:
            try:
                dt_v = datetime.strptime(data_viagem.strip(), "%Y-%m-%d")
                bit_dia = 1 << dt_v.weekday()
            except ValueError:
                raise ValueError(f"Formato de data inválido: {data_viagem}")

            for tr in seq_trechos:
                if (tr.dias_semana_mask & bit_dia) == 0:
                    raise RotaNaoEncontradaException("A rota não opera na data informada.")

        # Monta OpcaoRota
        opcao = montar_opcao_rota(
            seq_trechos=seq_trechos,
            localidades=self.localidades,
            data_viagem=data_viagem,
            data_referencia=data_referencia
        )
        if opcao is None:
            raise RotaNaoEncontradaException("Não foi possível calcular a rota com os trechos informados.")

        # Atribuição dos mesmos selos da busca de alternativas
        origem_id = seq_trechos[0].origem_id
        destino_id = seq_trechos[-1].destino_id
        alternativas = self.calcular_rotas(
            origem_id=origem_id,
            destino_id=destino_id,
            criterio="menor_tempo",
            data_viagem=data_viagem,
            data_referencia=data_referencia,
            max_opcoes=0  # sem limite
        )
        match_alt = next((alt for alt in alternativas if alt.id == opcao.id), None)
        if match_alt is not None:
            opcao.selos = list(match_alt.selos)
        else:
            if opcao.dias_max_desatualizacao > 30:
                opcao.selos = ["Desatualizado"]
            else:
                opcao.selos = []

        return opcao
