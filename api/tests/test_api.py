"""
Testes de Integração da API FastAPI (Endpoints REST)
Valida GET /api/v1/localidades, GET /api/v1/rotas, filtros de modais e formato de erro ErroPadrao
"""

import os
import sys
import unittest

# Adicionar pasta api ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
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

    def test_04_buscar_rotas_caso_sem_resultados_erro_padrao(self):
        response = self.client.get("/api/v1/rotas?origem=Cametá&destino=Alenquer")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        # Validação do formato ErroPadrao {"codigo": "...", "mensagem": "..."}
        self.assertIn("codigo", data)
        self.assertIn("mensagem", data)
        self.assertEqual(data["codigo"], "ROTA_NAO_ENCONTRADA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
