"""
Suíte Abrangente de Testes Automatizados do Motor de Roteamento Multimodal
Localizado em: api/tests/test_route_engine.py

Cobre os requisitos estritos do Trello:
1. Rota 1 (Belém -> Manaus): Opções A, B e C combinada (com 2 d, R$ 750,00).
2. Rota 1 Opção B: Acúmulo conjunto dos selos 'Menor tempo' e 'Mais confiável'.
3. Cálculo dinâmico da conexão da Opção C (4 h 40 min = 280 min calculados pela diferença 14:00 - 09:20).
4. Rota 2 (Manaus -> Tefé): Voadeira expressa R$ 320 vs Barco regional R$ 190.
5. Rota 3 (Cametá -> Alenquer): Retorno de lista vazia para localidades sem conexão.
6. Rejeição de conexão impossível (horário de partida antes da chegada).
7. Atribuição do selo 'Desatualizado' para trechos com mais de 30 dias de recência.
8. Carregamento direto a partir do banco de dados SQLite (comprovando fonte única de dados).
"""

import os
import unittest
import sys

# Adicionar a pasta api/engine ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine')))

from route_engine import MotorRoteamentoMultimodal, Localidade, Trecho, calcular_intervalo_conexao


class TesteMotorRoteamentoCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'embarque.db'))
        cls.motor = MotorRoteamentoMultimodal()
        cls.motor.carregar_do_banco(cls.db_path)

    def test_01_conexao_calculada_dinamicamente(self):
        # Voo chega 09:20 e barco parte 14:00 -> 4h 40min = 280 minutos
        intervalo = calcular_intervalo_conexao("09:20:00", "14:00:00")
        self.assertEqual(intervalo, 280, "A conexão em Santarém deve ser calculada dinamicamente como 280 minutos")

    def test_02_conexao_impossivel_rejeitada(self):
        # Chegada às 10:00 e partida às 08:00 no mesmo dia deve ser rejeitada
        intervalo = calcular_intervalo_conexao("10:00:00", "08:00:00")
        self.assertIsNone(intervalo, "Conexão com partida anterior à chegada deve retornar None (rejeitada)")

    def test_03_rota_1_tres_opcoes_e_opcao_c_combinada(self):
        rotas = self.motor.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_tempo")
        self.assertEqual(len(rotas), 3, "A Rota 1 deve retornar exatamente 3 opções viáveis")

        opcao_c = next((r for r in rotas if len(r.trechos) == 2), None)
        self.assertIsNotNone(opcao_c, "Opção C combinada deve ser encontrada")
        self.assertEqual(opcao_c.custo_total_reais, 750.00, "Custo total da Opção C deve ser exatamente R$ 750,00")
        self.assertEqual(opcao_c.duracao_total_minutos, 2880, "Duração total de C deve ser 2880 min (80m voo + 280m conexão + 2520m barco)")
        self.assertEqual(opcao_c.duracao_formatada, "2 d", "Duração formatada deve ser '2 d'")
        self.assertEqual(opcao_c.numero_transbordos, 1, "Opção C deve ter 1 conexão")

    def test_04_rota_1_opcao_b_recebe_ambos_os_selos(self):
        rotas = self.motor.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_tempo")
        # Opção B é o voo direto da Azul (135 min, atualizado hoje)
        opcao_b = next((r for r in rotas if r.trechos[0].modal_codigo == "aviacao_regional"), None)
        self.assertIsNotNone(opcao_b)
        self.assertIn("Menor tempo", opcao_b.selos, "Opção B deve ter o selo 'Menor tempo'")
        self.assertIn("Mais confiável", opcao_b.selos, "Opção B deve ter o selo 'Mais confiável'")

    def test_05_rota_1_criterio_menor_custo(self):
        rotas = self.motor.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_custo")
        primeira = rotas[0]
        self.assertEqual(primeira.custo_total_reais, 350.00)
        self.assertIn("Menor custo", primeira.selos)

    def test_06_rota_2_manaus_tefe_valores_canonicos(self):
        rotas = self.motor.calcular_rotas(origem_id=2, destino_id=4, criterio="menor_tempo")
        self.assertEqual(len(rotas), 2, "Rota 2 deve retornar 2 opções")
        # Voadeira expressa: 11 h, R$ 320,00
        self.assertEqual(rotas[0].custo_total_reais, 320.00)
        self.assertEqual(rotas[0].duracao_formatada, "11 h")
        self.assertIn("Menor tempo", rotas[0].selos)

        # Barco regional Oliveira Navegações: 1 d 12 h, R$ 190,00
        rotas_custo = self.motor.calcular_rotas(origem_id=2, destino_id=4, criterio="menor_custo")
        self.assertEqual(rotas_custo[0].custo_total_reais, 190.00)
        self.assertEqual(rotas_custo[0].duracao_formatada, "1 d 12 h")
        self.assertIn("Menor custo", rotas_custo[0].selos)

    def test_07_rota_3_sem_resultados(self):
        rotas = self.motor.calcular_rotas(origem_id=6, destino_id=7)
        self.assertEqual(len(rotas), 0, "Cametá e Alenquer não possuem conexão viável (deve retornar [])")

    def test_08_trecho_desatualizado_acima_de_30_dias(self):
        # Parintins (5) -> Manaus (2) tem um trecho cadastrado com 45 dias de recência
        rotas = self.motor.calcular_rotas(origem_id=5, destino_id=2)
        self.assertGreater(len(rotas), 0)
        rota_desatualizada = rotas[0]
        self.assertGreater(rota_desatualizada.dias_max_desatualizacao, 30)
        self.assertIn("Desatualizado", rota_desatualizada.selos, "Trechos com mais de 30 dias devem receber o selo 'Desatualizado'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
