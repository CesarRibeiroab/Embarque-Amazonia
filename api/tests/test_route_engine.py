"""
Suíte Abrangente de Testes Automatizados do Motor de Roteamento Multimodal
Localizado em: api/tests/test_route_engine.py
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
        # Opção B é o voo direto da Azul (135 min, modal aviao_regional, atualizado hoje)
        opcao_b = next((r for r in rotas if r.trechos[0].modal_codigo == "aviao_regional"), None)
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

    def test_09_filtro_por_dia_da_semana(self):
        # Sexta-feira (20/11/2026): todas as 3 opções (A, B e C) operam
        rotas_sexta = self.motor.calcular_rotas(origem_id=1, destino_id=2, data_viagem="2026-11-20")
        self.assertEqual(len(rotas_sexta), 3, "Na sexta-feira (20/11/2026), as 3 opções A, B e C devem estar ativas")

        # Sábado (2026-11-21): Barco de linha não sai aos sábados. Apenas o voo diário (Opção B) opera
        rotas_sabado = self.motor.calcular_rotas(origem_id=1, destino_id=2, data_viagem="2026-11-21")
        self.assertEqual(len(rotas_sabado), 1, "No sábado, apenas o voo diário deve estar ativo")
        self.assertEqual(rotas_sabado[0].trechos[0].modal_codigo, "aviao_regional")

    def test_10_filtro_por_modais(self):
        # Filtro estrito para aviação regional
        rotas_ar = self.motor.calcular_rotas(origem_id=1, destino_id=2, modais_filtro=["aviao_regional"])
        self.assertEqual(len(rotas_ar), 1)
        self.assertEqual(rotas_ar[0].trechos[0].modal_codigo, "aviao_regional")

    def test_11_origem_igual_destino_devolve_lista_vazia(self):
        # Belém -> Belém deve retornar lista vazia
        rotas_mesmo = self.motor.calcular_rotas(origem_id=1, destino_id=1)
        self.assertEqual(len(rotas_mesmo), 0, "Origem igual ao destino não pode gerar rota viável")

    def test_12_recarga_do_banco_idempotente(self):
        # Recarregar o banco uma segunda vez não pode multiplicar arestas
        self.motor.carregar_do_banco(self.db_path)
        rotas = self.motor.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_tempo")
        self.assertEqual(len(rotas), 3, "Após recarga, Belém -> Manaus deve continuar devolvendo exatamente 3 opções")

    def test_13_id_deterministico_baseado_em_trechos(self):
        rotas = self.motor.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_tempo")
        # Checar se os IDs seguem o padrão 'rota-t{ids}'
        ids = [r.id for r in rotas]
        self.assertIn("rota-t2", ids, "Voo direto deve ter id 'rota-t2'")
        self.assertIn("rota-t1", ids, "Barco direto deve ter id 'rota-t1'")
        self.assertIn("rota-t3-t4", ids, "Combinada deve ter id 'rota-t3-t4'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
