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

    def test_14_conexao_impossivel_descartada_fim_a_fim(self):
        # Motor novo carregado do banco + trecho em memória Santarém (3) -> Manaus (2) partindo às 07:00
        from datetime import date
        motor_teste = MotorRoteamentoMultimodal()
        motor_teste.carregar_do_banco(self.db_path)
        trecho_incompativel = Trecho(
            id=88,
            origem_id=3,
            destino_id=2,
            operador_nome="Barco Teste Conexão",
            modal_codigo="barco_regional",
            modal_nome="Barco regional",
            duracao_minutos=2520,
            tarifa_reais=200.0,
            data_ultima_atualizacao=date.today().strftime("%Y-%m-%d"),
            hora_partida="07:00:00",
            hora_chegada="01:00:00",
            dias_semana_mask=127,
        )
        motor_teste.adicionar_trecho(trecho_incompativel)

        rotas = motor_teste.calcular_rotas(origem_id=1, destino_id=2, criterio="menor_custo")
        ids = [r.id for r in rotas]
        self.assertNotIn("rota-t3-t88", ids, "Conexão voo (chega 09:20) + barco (parte 07:00) deve ser descartada")
        self.assertIn("rota-t3-t4", ids, "A conexão válida (chega 09:20 -> parte 14:00) deve permanecer")

    def test_15_opcao_unica_sem_selos_comparativos(self):
        # Parintins (5) -> Manaus (2): opção única e > 30 dias deve ter apenas 'Desatualizado'
        rotas_parintins = self.motor.calcular_rotas(origem_id=5, destino_id=2)
        self.assertEqual(len(rotas_parintins), 1)
        self.assertEqual(rotas_parintins[0].selos, ["Desatualizado"])

        # Santarém (3) -> Manaus (2): opção única atualizada (< 30 dias) não recebe selos comparativos
        rotas_santarem = self.motor.calcular_rotas(origem_id=3, destino_id=2)
        self.assertEqual(len(rotas_santarem), 1)
        self.assertEqual(rotas_santarem[0].id, "rota-t4")
        self.assertEqual(rotas_santarem[0].selos, [])

    def test_16_data_referencia_sistema_e_sobrescrita(self):
        from datetime import date, timedelta
        hoje = date.today()
        tr_hoje = Trecho(
            id=901, origem_id=1, destino_id=2, operador_nome="Op", modal_codigo="barco_regional",
            modal_nome="Barco regional", duracao_minutos=100, tarifa_reais=50.0,
            data_ultima_atualizacao=hoje.strftime("%Y-%m-%d")
        )
        tr_10d = Trecho(
            id=902, origem_id=1, destino_id=2, operador_nome="Op", modal_codigo="barco_regional",
            modal_nome="Barco regional", duracao_minutos=100, tarifa_reais=50.0,
            data_ultima_atualizacao=(hoje - timedelta(days=10)).strftime("%Y-%m-%d")
        )
        antigo = os.environ.pop("DATA_REFERENCIA", None)
        try:
            self.assertEqual(tr_hoje.dias_desde_atualizacao(), 0)
            self.assertEqual(tr_10d.dias_desde_atualizacao(), 10)
            os.environ["DATA_REFERENCIA"] = (hoje + timedelta(days=5)).strftime("%Y-%m-%d")
            self.assertEqual(tr_hoje.dias_desde_atualizacao(), 5)
            self.assertEqual(tr_10d.dias_desde_atualizacao(), 15)
        finally:
            if antigo is None:
                os.environ.pop("DATA_REFERENCIA", None)
            else:
                os.environ["DATA_REFERENCIA"] = antigo

    def test_17_limite_cinco_opcoes_apos_ordenacao(self):
        from datetime import date
        motor_lim = MotorRoteamentoMultimodal()
        motor_lim.adicionar_localidade(Localidade(1, "A", "PA", True))
        motor_lim.adicionar_localidade(Localidade(2, "B", "AM", True))
        hoje_str = date.today().strftime("%Y-%m-%d")
        # Cria 6 opções diretas com tarifas crescentes e durações decrescentes
        for idx in range(6):
            motor_lim.adicionar_trecho(Trecho(
                id=100 + idx, origem_id=1, destino_id=2, operador_nome=f"Op {idx}",
                modal_codigo="barco_regional", modal_nome="Barco regional",
                duracao_minutos=600 - idx * 50,
                tarifa_reais=100.0 + idx * 50.0,
                data_ultima_atualizacao=hoje_str
            ))
        por_custo = motor_lim.calcular_rotas(1, 2, criterio="menor_custo")
        self.assertEqual(len(por_custo), 5)
        self.assertEqual([r.custo_total_reais for r in por_custo], [100.0, 150.0, 200.0, 250.0, 300.0])

        por_tempo = motor_lim.calcular_rotas(1, 2, criterio="menor_tempo")
        self.assertEqual(len(por_tempo), 5)
        self.assertEqual([r.duracao_total_minutos for r in por_tempo], [350, 400, 450, 500, 550])


if __name__ == "__main__":
    unittest.main(verbosity=2)
