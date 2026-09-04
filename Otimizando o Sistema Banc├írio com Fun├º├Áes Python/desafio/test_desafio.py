import unittest
from decimal import Decimal
from unittest.mock import patch

import desafio


class TestOperacoes(unittest.TestCase):
    def test_deposito_usa_valor_exato(self):
        saldo, extrato = desafio.depositar(Decimal("0.00"), "10,10", "")
        self.assertEqual(saldo, Decimal("10.10"))
        self.assertIn("10,10", extrato)

    def test_deposito_recusa_zero_e_negativo(self):
        self.assertEqual(desafio.depositar(Decimal("5"), 0, ""), (Decimal("5"), ""))
        self.assertEqual(desafio.depositar(Decimal("5"), -1, ""), (Decimal("5"), ""))

    def test_saque_respeita_saldo_limite_e_contagem(self):
        saldo, extrato, quantidade = desafio.sacar(
            saldo=Decimal("600"), valor=Decimal("500"), extrato="",
            limite=Decimal("500"), numero_saques=0, limite_saques=3)
        self.assertEqual(saldo, Decimal("100.00"))
        self.assertEqual(quantidade, 1)
        self.assertIn("500,00", extrato)

        resultado = desafio.sacar(
            saldo=Decimal("600"), valor=Decimal("501"), extrato="",
            limite=Decimal("500"), numero_saques=0, limite_saques=3)
        self.assertEqual(resultado, (Decimal("600"), "", 0))

    def test_usuario_e_conta(self):
        usuarios, contas = [], {}
        respostas = ["123.456.789-00", "ana silva", "01/01/1990", "Rua A", "1", "Centro", "Recife", "pe"]
        with patch("builtins.input", side_effect=respostas):
            self.assertTrue(desafio.criar_usuario(usuarios))
        with patch("builtins.input", return_value="12345678900"):
            self.assertTrue(desafio.criar_conta("0001", 1, usuarios, contas))
        self.assertEqual(contas[1]["cpf"], "12345678900")
        self.assertEqual(contas[1]["saldo"], Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
