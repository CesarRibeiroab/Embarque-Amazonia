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


if __name__ == "__main__":
    unittest.main(verbosity=2)
