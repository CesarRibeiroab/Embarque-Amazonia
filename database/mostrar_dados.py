"""
Utilitário de leitura (somente leitura) para inspecionar o banco SQLite
Populado por database/init_db.py.
Uso: python database/mostrar_dados.py
"""

from datetime import date, datetime
import os
import sqlite3
import sys

DIAS_SEMANA = [
    (1, "Segunda-feira"),
    (2, "Terça-feira"),
    (4, "Quarta-feira"),
    (8, "Quinta-feira"),
    (16, "Sexta-feira"),
    (32, "Sábado"),
    (64, "Domingo"),
]


def decodificar_dias(mask: int) -> str:
    """Converte a máscara bitmask de dias de operação em nomes por extenso."""
    if not mask:
        return "Nenhum dia configurado"
    dias = [nome for bit, nome in DIAS_SEMANA if mask & bit]
    if mask == 127:
        return ", ".join(dias) + " (Diário)"
    return ", ".join(dias) if dias else "Máscara inválida"


def formatar_duracao(minutos: int) -> str:
    """Formata duração em minutos no padrão 'X d Y h Z min'."""
    dias = minutos // (24 * 60)
    horas = (minutos % (24 * 60)) // 60
    mins = minutos % 60
    partes = []
    if dias > 0:
        partes.append(f"{dias} d")
    if horas > 0:
        partes.append(f"{horas} h")
    if mins > 0 or not partes:
        partes.append(f"{mins} min")
    return " ".join(partes)


def formatar_tarifa(valor: float) -> str:
    """Formata valor em reais no padrão brasileiro."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def obter_data_referencia() -> date:
    """Obtém DATA_REFERENCIA opcional ou usa a data atual do sistema."""
    env_ref = os.getenv("DATA_REFERENCIA", "").strip()
    if env_ref:
        try:
            return datetime.strptime(env_ref, "%Y-%m-%d").date()
        except ValueError:
            pass
    return date.today()


def texto_recencia(data_str: str, ref: date) -> str:
    """Retorna 'atualizado hoje', 'atualizado há 1 dia' ou 'atualizado há N dias'."""
    try:
        d_at = datetime.strptime(data_str, "%Y-%m-%d").date()
        dias = max(0, (ref - d_at).days)
    except ValueError:
        return f"data {data_str}"
    if dias == 0:
        return "atualizado hoje"
    if dias == 1:
        return "atualizado há 1 dia"
    return f"atualizado há {dias} dias"


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "embarque.db")

    if not os.path.exists(db_path):
        print(f"Erro: banco '{db_path}' não encontrado.")
        print("Execute primeiro: python database/init_db.py")
        sys.exit(1)

    ref = obter_data_referencia()
    # Conexão estritamente somente leitura via URI
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()

    print(f"=== EMBARQUE AMAZÔNIA — DADOS DO BANCO (Referência: {ref.isoformat()}) ===\n")

    # 1. Localidades
    localidades = cur.execute(
        "SELECT id, nome, uf, tipo, COALESCE(codigo_iata, '-') FROM localidade ORDER BY id"
    ).fetchall()
    print(f"--- LOCALIDADES ({len(localidades)}) ---")
    for lid, nome, uf, tipo, iata in localidades:
        print(f"  [{lid}] {nome} ({uf}) | tipo: {tipo} | IATA: {iata}")

    # 2. Trechos com horários e recência
    trechos = cur.execute(
        """
        SELECT t.id, lo.nome, ld.nome, m.nome, COALESCE(o.nome_fantasia, o.razao_social),
               t.duracao_estimada_minutos, t.tarifa_base_reais, t.data_ultima_atualizacao,
               COALESCE(h.hora_partida, '--:--:--'), COALESCE(h.hora_chegada_estimada, '--:--:--'),
               COALESCE(h.dias_semana_mask, 127)
        FROM trecho t
        JOIN localidade lo ON t.origem_id = lo.id
        JOIN localidade ld ON t.destino_id = ld.id
        JOIN modal m ON t.modal_id = m.id
        JOIN operador o ON t.operador_id = o.id
        LEFT JOIN horario_operacao h ON h.trecho_id = t.id AND h.ativo = 1
        ORDER BY t.id
        """
    ).fetchall()
    print(f"\n--- TRECHOS ({len(trechos)}) ---")
    for tid, orig, dest, modal, op, dur, tar, data_at, hp, hc, mask in trechos:
        dias_txt = decodificar_dias(mask)
        rec_txt = texto_recencia(data_at, ref)
        print(
            f"  [T{tid:02d}] {orig} -> {dest} | {modal} ({op}) | "
            f"{formatar_duracao(dur)} | {formatar_tarifa(float(tar))} | "
            f"{hp[:5]}->{hc[:5]} | Dias: {dias_txt} | {rec_txt} ({data_at})"
        )

    # 3. Acomodações
    acomodacoes = cur.execute(
        """
        SELECT a.id, a.trecho_id, lo.nome, ld.nome, a.tipo, a.regime,
               a.valor_total_reais, COALESCE(a.descricao, '')
        FROM acomodacao_trecho a
        JOIN trecho t ON a.trecho_id = t.id
        JOIN localidade lo ON t.origem_id = lo.id
        JOIN localidade ld ON t.destino_id = ld.id
        ORDER BY a.id
        """
    ).fetchall()
    print(f"\n--- ACOMODAÇÕES ({len(acomodacoes)}) ---")
    for aid, tid, orig, dest, tipo, regime, valor, desc in acomodacoes:
        print(
            f"  [A{aid:02d}] Trecho T{tid:02d} ({orig} -> {dest}) | "
            f"tipo: {tipo} | regime: {regime} | {formatar_tarifa(float(valor))} | {desc}"
        )

    con.close()


if __name__ == "__main__":
    main()
