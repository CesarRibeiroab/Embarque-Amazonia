"""
Testes de Integração da API FastAPI (Endpoints REST)
Valida GET /api/v1/localidades, GET /api/v1/rotas, filtros de modais e formato de erro ErroPadrao
"""

import os
import sys
import unittest
from unittest.mock import patch

# Adicionar pasta api ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
import main
from main import app, DB_PATH, motor


class TesteFastAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        if os.path.exists(DB_PATH):
            motor.carregar_do_banco(DB_PATH)

    def test_01_listar_localidades_endpoint(self):
        response = self.client.get("/api/v1/localidades")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 7)
        nomes = [loc["nome"] for loc in data]
        self.assertIn("Belém", nomes)
        self.assertIn("Manaus", nomes)

    def test_02_buscar_rotas_belem_manaus(self):
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&criterio=menor_tempo")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["origem"], "Belém")
        self.assertEqual(data["destino"], "Manaus")
        self.assertEqual(data["total_opcoes"], 3)

        # Ordem estrita dos campos conforme especificação
        primeira_rota = data["rotas"][0]
        expected_fields = ["id", "origem_nome", "destino_nome", "modais", "preco_total", "duracao_total_minutos",
                           "duracao_total_formatada", "numero_trechos", "numero_conexoes", "selo", "atualizado_em", "trechos"]
        for f in expected_fields:
            self.assertIn(f, primeira_rota)

        # Validar Opção B por menor tempo
        self.assertEqual(primeira_rota["duracao_total_minutos"], 135)
        self.assertIn("Menor tempo", primeira_rota["selo"])
        self.assertIn("Mais confiável", primeira_rota["selo"])

    def test_03_buscar_rotas_com_filtro_modais(self):
        # Filtrando estritamente para apenas aviação regional
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&modais=aviao_regional")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Deve retornar apenas o voo direto da Azul (1 opção) e nenhum barco
        self.assertEqual(data["total_opcoes"], 1)
        self.assertEqual(data["rotas"][0]["modais"], ["Avião regional"])

    def test_04_buscar_rotas_sem_resultados_tela_p10a(self):
        # Origem e destino existem na malha, mas não há conexão direta ou indireta viável
        response = self.client.get("/api/v1/rotas?origem=Cametá&destino=Alenquer")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["origem"], "Cametá")
        self.assertEqual(data["destino"], "Alenquer")
        self.assertEqual(data["total_opcoes"], 0)
        self.assertEqual(data["rotas"], [])

    def test_05_localidade_inexistente_erro_padrao_404(self):
        # Localidade inexistente na base relacional
        response = self.client.get("/api/v1/rotas?origem=CidadeInexistente&destino=Manaus")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("codigo", data)
        self.assertIn("mensagem", data)
        self.assertEqual(data["codigo"], "LOCALIDADE_NAO_ENCONTRADA")

    def test_06_busca_insensivel_a_acentuacao_e_rota_retorno(self):
        # Testa consulta sem acento ('Belem' em vez de 'Belém') e sentido inverso (Manaus -> Belém)
        response = self.client.get("/api/v1/rotas?origem=manaus&destino=belem")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["total_opcoes"], 2)  # Retorno via avião e barco regional

    def test_07_validacao_origem_igual_destino_422(self):
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Belém")
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["codigo"], "PARAMETRO_INVALIDO")
        self.assertIn("mesma localidade", data["mensagem"])

    def test_08_validacao_criterio_invalido_422(self):
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&criterio=criterio_inexistente")
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["codigo"], "PARAMETRO_INVALIDO")

    def test_09_validacao_formato_data_invalida_422(self):
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&data=20/11/2026")
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["codigo"], "PARAMETRO_INVALIDO")

    def test_10_filtro_data_viagem_sexta_vs_sabado(self):
        # Sexta-feira 2026-11-20 -> 3 opções
        resp_sexta = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&data=2026-11-20")
        self.assertEqual(resp_sexta.status_code, 200)
        self.assertEqual(resp_sexta.json()["total_opcoes"], 3)

        # Sábado 2026-11-21 -> 1 opção (voo diário)
        resp_sabado = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&data=2026-11-21")
        self.assertEqual(resp_sabado.status_code, 200)
        self.assertEqual(resp_sabado.json()["total_opcoes"], 1)

    def test_11_campos_iso_e_id_deterministico(self):
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus")
        self.assertEqual(response.status_code, 200)
        primeira = response.json()["rotas"][0]
        self.assertTrue(primeira["id"].startswith("rota-t"))
        self.assertIn("data_atualizacao_iso", primeira)
        self.assertIn("dias_desde_atualizacao", primeira)

    def test_12_parametro_ausente_422_erro_padrao_e_docs_ativos(self):
        for url in [
            "/api/v1/rotas?origem=Belém",
            "/api/v1/rotas?destino=Manaus",
            "/api/v1/rotas?origem=&destino=Manaus",
        ]:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 422, f"Esperado 422 para {url}")
            data = resp.json()
            self.assertEqual(data["codigo"], "PARAMETRO_INVALIDO")
            self.assertIn("mensagem", data)

        self.assertEqual(self.client.get("/docs").status_code, 200)
        self.assertEqual(self.client.get("/openapi.json").status_code, 200)

    def test_13_autocomplete_localidades_busca_sem_acento(self):
        resp = self.client.get("/api/v1/localidades?busca=bele")
        self.assertEqual(resp.status_code, 200)
        nomes = [loc["nome"] for loc in resp.json()]
        self.assertIn("Belém", nomes)
        self.assertEqual(len(nomes), 1)

    def test_14_opcao_unica_sem_selos_comparativos(self):
        # Parintins -> Manaus (1 opção, > 30 dias): apenas selo Desatualizado
        resp_p = self.client.get("/api/v1/rotas?origem=Parintins&destino=Manaus")
        self.assertEqual(resp_p.status_code, 200)
        dp = resp_p.json()
        self.assertEqual(dp["total_opcoes"], 1)
        self.assertEqual(dp["rotas"][0]["selo"], ["Desatualizado"])

        # Santarém -> Manaus (1 opção, sem trecho 8): nenhum selo comparativo
        resp_s = self.client.get("/api/v1/rotas?origem=Santarém&destino=Manaus")
        self.assertEqual(resp_s.status_code, 200)
        ds = resp_s.json()
        self.assertEqual(ds["total_opcoes"], 1)
        self.assertEqual(ds["rotas"][0]["id"], "rota-t4")
        self.assertEqual(ds["rotas"][0]["selo"], [])

    def test_15_banco_ausente_retorna_503_nos_dois_endpoints(self):
        caminho_falso = os.path.join(os.path.dirname(DB_PATH), "nao_existe_embarque.db")
        with patch.object(main, "DB_PATH", caminho_falso):
            r_loc = self.client.get("/api/v1/localidades")
            self.assertEqual(r_loc.status_code, 503)
            self.assertEqual(r_loc.json()["codigo"], "BANCO_INDISPONIVEL")

            r_rotas = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus")
            self.assertEqual(r_rotas.status_code, 503)
            self.assertEqual(r_rotas.json()["codigo"], "BANCO_INDISPONIVEL")

    def test_16_detalhe_rota_sete_casos_secao_4_5(self):
        # 1. rota-t3-t4 -> 200
        r1 = self.client.get("/api/v1/rotas/rota-t3-t4")
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["id"], "rota-t3-t4")
        self.assertEqual(len(d1["trechos"]), 2)
        self.assertEqual(d1["preco_total"], 750.0)

        # 2. rota-t3-t1 -> 404 (trechos não se encadeiam)
        r2 = self.client.get("/api/v1/rotas/rota-t3-t1")
        self.assertEqual(r2.status_code, 404)
        self.assertEqual(r2.json()["codigo"], "ROTA_NAO_ENCONTRADA")

        # 3. rota-t999 -> 404 (trecho inexistente)
        r3 = self.client.get("/api/v1/rotas/rota-t999")
        self.assertEqual(r3.status_code, 404)
        self.assertEqual(r3.json()["codigo"], "ROTA_NAO_ENCONTRADA")

        # 4. rota-xyz -> 422 (id fora do padrão)
        r4 = self.client.get("/api/v1/rotas/rota-xyz")
        self.assertEqual(r4.status_code, 422)
        self.assertEqual(r4.json()["codigo"], "PARAMETRO_INVALIDO")

        # 5. rota-t3-t4?data=2026-11-21 (sábado) -> 404 (barco não sai sábado)
        r5 = self.client.get("/api/v1/rotas/rota-t3-t4?data=2026-11-21")
        self.assertEqual(r5.status_code, 404)
        d5 = r5.json()
        self.assertEqual(d5["codigo"], "ROTA_NAO_ENCONTRADA")
        self.assertIn("A rota não opera na data informada.", d5["mensagem"])

        # 6. rota-t3-t4?data=2026-11-20 -> 200 com chegada_estimada_iso
        r6 = self.client.get("/api/v1/rotas/rota-t3-t4?data=2026-11-20")
        self.assertEqual(r6.status_code, 200)
        d6 = r6.json()
        self.assertEqual(d6["chegada_dia_offset"], 2)
        self.assertEqual(d6["chegada_estimada_iso"], "2026-11-22T08:00")
        self.assertEqual(d6["trechos"][0]["intervalo_conexao_minutos"], 280)

        # 7. rota-t3-t4?data=20/11/2026 -> 422 (data fora do padrão ISO)
        r7 = self.client.get("/api/v1/rotas/rota-t3-t4?data=20/11/2026")
        self.assertEqual(r7.status_code, 422)
        self.assertEqual(r7.json()["codigo"], "PARAMETRO_INVALIDO")

    def test_17_rotas_campos_novos_belem_manaus_2026_11_20(self):
        resp = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&data=2026-11-20")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_opcoes"], 3)

        # Localizar a Opção C
        r_c = next(r for r in data["rotas"] if r["id"] == "rota-t3-t4")
        self.assertEqual(r_c["data_viagem"], "2026-11-20")
        self.assertEqual(r_c["hora_partida"], "08:00")
        self.assertEqual(r_c["chegada_estimada"], "08:00")
        self.assertEqual(r_c["chegada_dia_offset"], 2)
        self.assertEqual(r_c["chegada_estimada_iso"], "2026-11-22T08:00")

        # Validar campos de TrechoResponse
        t3 = r_c["trechos"][0]
        self.assertEqual(t3["modal_codigo"], "aviao_regional")
        self.assertEqual(t3["modal_categoria"], "aereo")
        self.assertEqual(t3["hora_partida"], "08:00")
        self.assertEqual(t3["hora_chegada_estimada"], "09:20")
        self.assertEqual(t3["partida_dia_offset"], 0)
        self.assertEqual(t3["chegada_dia_offset"], 0)
        self.assertEqual(t3["intervalo_conexao_minutos"], 280)
        self.assertEqual(t3["frequencia_descricao"], "Diário")
        self.assertEqual(t3["dias_semana_mask"], 127)

        t4 = r_c["trechos"][1]
        self.assertEqual(t4["modal_codigo"], "barco_regional")
        self.assertEqual(t4["modal_categoria"], "fluvial")
        self.assertEqual(t4["hora_partida"], "14:00")
        self.assertEqual(t4["hora_chegada_estimada"], "08:00")
        self.assertEqual(t4["partida_dia_offset"], 0)
        self.assertEqual(t4["chegada_dia_offset"], 2)
        self.assertIsNone(t4["intervalo_conexao_minutos"])
        self.assertEqual(t4["frequencia_descricao"], "Terças, Quintas e Sextas-feiras")
        self.assertEqual(t4["dias_semana_mask"], 26)
        self.assertEqual(t4["acomodacoes"][0]["tipo"], "rede")

    def test_18_selos_detalhe_iguais_a_busca(self):
        # Na busca geral, rota-t2 tem 'Menor tempo' e 'Mais confiável'; rota-t3-t4 não tem selos comparativos
        resp_lista = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus&data=2026-11-20")
        self.assertEqual(resp_lista.status_code, 200)
        selos_lista_t3_t4 = next(r["selo"] for r in resp_lista.json()["rotas"] if r["id"] == "rota-t3-t4")
        selos_lista_t2 = next(r["selo"] for r in resp_lista.json()["rotas"] if r["id"] == "rota-t2")

        resp_det_t3_t4 = self.client.get("/api/v1/rotas/rota-t3-t4?data=2026-11-20")
        self.assertEqual(resp_det_t3_t4.status_code, 200)
        self.assertEqual(resp_det_t3_t4.json()["selo"], selos_lista_t3_t4)

        resp_det_t2 = self.client.get("/api/v1/rotas/rota-t2?data=2026-11-20")
        self.assertEqual(resp_det_t2.status_code, 200)
        self.assertEqual(resp_det_t2.json()["selo"], selos_lista_t2)

    def test_19_banco_ausente_retorna_503_detalhe_rota(self):
        caminho_falso = os.path.join(os.path.dirname(DB_PATH), "nao_existe_embarque.db")
        with patch.object(main, "DB_PATH", caminho_falso):
            r_det = self.client.get("/api/v1/rotas/rota-t3-t4")
            self.assertEqual(r_det.status_code, 503)
            self.assertEqual(r_det.json()["codigo"], "BANCO_INDISPONIVEL")

    def test_20_a_prova_de_enriquecimento_do_seed(self):
        import shutil
        import sqlite3
        import tempfile

        # Cria cópia temporária do banco relacional
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            temp_db_path = tmp_file.name

        try:
            shutil.copyfile(DB_PATH, temp_db_path)

            # Aplica enriquecimento independente do Fernando (novo camarote + telefone)
            con = sqlite3.connect(temp_db_path)
            cur = con.cursor()
            cur.execute("""
                INSERT INTO acomodacao_trecho (trecho_id, tipo, regime, valor_total_reais, descricao)
                VALUES (4, 'camarote_duplo', 'fixo', 850.00, 'Camarote privativo com ar condicionado')
            """)
            cur.execute("""
                UPDATE operador
                SET telefone_contato = '(91) 90000-0000'
                WHERE id = (SELECT operador_id FROM trecho WHERE id = 4)
            """)
            con.commit()
            con.close()

            with patch.object(main, "DB_PATH", temp_db_path):
                motor.carregar_do_banco(temp_db_path)
                resp = self.client.get("/api/v1/rotas/rota-t3-t4?data=2026-11-20")
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                t4 = data["trechos"][1]

                # Prova 1: acomodações do trecho 4 possuem os tipos enriquecidos
                self.assertGreaterEqual(len(t4["acomodacoes"]), 2)
                tipos = [a["tipo"] for a in t4["acomodacoes"]]
                self.assertIn("rede", tipos)
                self.assertIn("camarote_duplo", tipos)

                # Prova 2: telefone de contato do operador vem preenchido
                self.assertEqual(t4["telefone_contato"], "(91) 90000-0000")
        finally:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            # Restaura estado com o banco oficial
            motor.carregar_do_banco(DB_PATH)

    def test_21_validacao_contrato_openapi_rota_detalhe(self):
        import yaml
        openapi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "openapi.yaml"))
        self.assertTrue(os.path.exists(openapi_path), "docs/openapi.yaml deve existir")
        with open(openapi_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        opcao_schema = spec["components"]["schemas"]["OpcaoRota"]
        propriedades_opcao = set(opcao_schema["properties"].keys())

        trecho_schema = spec["components"]["schemas"]["TrechoItem"]
        propriedades_trecho = set(trecho_schema["properties"].keys())

        # Faz requisição real para o endpoint de detalhe
        resp = self.client.get("/api/v1/rotas/rota-t3-t4?data=2026-11-20")
        self.assertEqual(resp.status_code, 200)
        json_rota = resp.json()

        # Todas as chaves da resposta da rota devem pertencer às propriedades declaradas no schema
        chaves_resposta = set(json_rota.keys())
        self.assertTrue(
            chaves_resposta.issubset(propriedades_opcao),
            f"Chaves na resposta não documentadas em OpcaoRota: {chaves_resposta - propriedades_opcao}"
        )

        # Campos obrigatórios essenciais
        for campo_obrigatorio in [
            "id", "origem_nome", "destino_nome", "modais", "preco_total",
            "duracao_total_minutos", "trechos", "hora_partida", "chegada_estimada",
            "chegada_dia_offset"
        ]:
            self.assertIn(campo_obrigatorio, chaves_resposta)

        # Todas as chaves de cada trecho devem pertencer às propriedades de TrechoItem
        for t_json in json_rota["trechos"]:
            chaves_trecho = set(t_json.keys())
            self.assertTrue(
                chaves_trecho.issubset(propriedades_trecho),
                f"Chaves no trecho não documentadas em TrechoItem: {chaves_trecho - propriedades_trecho}"
            )
            for c_trecho in [
                "id", "origem_nome", "destino_nome", "modal_nome", "modal_codigo",
                "modal_categoria", "duracao_minutos", "tarifa_reais", "hora_partida",
                "hora_chegada_estimada"
            ]:
                self.assertIn(c_trecho, chaves_trecho)

    def test_22_detalhes_enriquecidos_p07_acomodacoes_e_operador(self):
        # Consulta rota Belém -> Manaus e valida enriquecimento do Trecho 2 Barco Santarém -> Manaus (Rota 1 C)
        response = self.client.get("/api/v1/rotas?origem=Belém&destino=Manaus")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        rota_c = next((r for r in data["rotas"] if len(r["trechos"]) == 2), None)
        self.assertIsNotNone(rota_c, "Rota 1 C (Belém -> Santarém -> Manaus) deve existir")

        trecho_barco = rota_c["trechos"][1]
        self.assertEqual(trecho_barco["origem_nome"], "Santarém")
        self.assertEqual(trecho_barco["destino_nome"], "Manaus")
        self.assertEqual(trecho_barco["operador_nome"], "Amazon Star")
        self.assertIn("90000-0000", trecho_barco["telefone_contato"])
        self.assertIn("vazante", trecho_barco["regime_hidrico_observacao"].lower())

        # Validar acomodações enriquecidas (Rede e Camarote duplo)
        tipos_ac = [ac["tipo"] for ac in trecho_barco["acomodacoes"]]
        self.assertIn("rede", tipos_ac)
        self.assertIn("camarote_duplo", tipos_ac)

        rede = next(ac for ac in trecho_barco["acomodacoes"] if ac["tipo"] == "rede")
        camarote = next(ac for ac in trecho_barco["acomodacoes"] if ac["tipo"] == "camarote_duplo")
        self.assertEqual(rede["valor_total_reais"], 210.0)
        self.assertEqual(camarote["valor_total_reais"], 900.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
