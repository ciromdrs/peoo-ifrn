import unittest

from velha import Velha


class TestVelha(unittest.TestCase):
    def test_verificar(self):
        # Nome do subteste, tabuleiro, vencedor esperado
        data = [
            [
                'Vence na linha 0',
                [
                    'X', 'X', 'X',
                    '3', 'O', '5',
                    '6', '7', 'O',
                ],
                [0,1],
                'X'
            ],
            [
                'Vence na linha 1',
                [
                    '0', 'O', '2',
                    'X', 'X', 'X',
                    '6', '7', 'O',
                ],
                [3,1],
                'X'
            ],
            [
                'Vence na linha 2',
                [
                    '0', 'O', '2',
                    '3', '4', '5',
                    'X', 'X', 'X',
                ],
                [6,1],
                'X'
            ],
            [
                'Vence na coluna 0',
                [
                    'X', '1', '2',
                    'X', 'O', '5',
                    'X', '7', 'O',
                ],
                [0,3],
                'X'
            ],
            [
                'Vence na coluna 1',
                [
                    '0', 'X', '2',
                    'O', 'X', '5',
                    '6', 'X', 'O',
                ],
                [1,3],
                'X'
            ],
            [
                'Vence na coluna 2',
                [
                    '0', 'O', 'X',
                    '3', 'O', 'X',
                    '6', '7', 'X',
                ],
                [2,3],
                'X'
            ],
            [
                'Vence na diagonal principal',
                [
                    'X', 'O', 'O',
                    '3', 'X', '5',
                    '6', '7', 'X',
                ],
                [0,4],
                'X'
            ],
            [
                'Vence na diagonal inversa',
                [
                    '0', 'O', 'X',
                    '3', 'X', 'O',
                    'X', '7', '8',
                ],
                [2,2],
                'X'
            ],
        ]
        for rotulo, tabuleiro, verificacao, esperado in data:
            with self.subTest(rotulo):
                jogo = Velha()
                jogo.tabuleiro = tabuleiro
                inicio, incremento = verificacao

                vencedor = jogo.verificar(inicio, incremento)

                self.assertEqual(vencedor, esperado)

    def test_verificar_vencedor(self):
        # Nome do subteste, tabuleiro, vencedor esperado
        data = [
            [
                'Vence',
                [
                    'X', 'X', 'X',
                    '3', 'O', '5',
                    '6', '7', 'O',
                ],
                'X'
            ],
            [
                'Empate',
                [
                    'X', 'O', 'X',
                    'O', 'X', 'X',
                    'O', 'X', 'O',
                ],
                '='
            ],
            [
                'Indeterminado',
                [
                    '0', 'O', 'X',
                    '3', 'X', 'O',
                    '6', 'X', '8',
                ],
                ''
            ],
        ]
        for rotulo, tabuleiro, esperado in data:
            with self.subTest(rotulo):
                jogo = Velha()
                jogo.tabuleiro = tabuleiro

                vencedor = jogo.verificar_vencedor()

                self.assertEqual(vencedor, esperado)
