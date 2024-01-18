"""Jogo da Velha"""


class Velha:
    # O tabuleiro é uma lista de strings
    tabuleiro: list[str] = None
    # O jogador atual pode ser 'X' ou 'O'
    jogador: str = ''
    # O vencedor pode ser 'X', 'O', '=' (empate) ou '' (ainda está jogando)
    vencedor: str = ''

    def __init__(self):
        # Inicia o tabuleiro com o índice da casa
        self.tabuleiro = [str(i) for i in range(9)]
        # O jogador X começa jogando
        self.jogador = 'X'
        # O vencedor começa indefinido
        self.vencedor = ''

    def exibir(self):
        for i in range(3):
            for j in range(3):
                print(self.tabuleiro[3 * i + j], end=' ')
            print()

    def jogar(self):
        self.__init__()
        while self.vencedor == '':
            self.exibir()
            self.fazer_jogada()
            self.vencedor = self.verificar_vencedor()
            self.trocar_jogador()
        self.exibir()
        print(f'O vencedor é {jogo.vencedor}')

    def trocar_jogador(self):
        if self.jogador == 'O':
            self.jogador = 'X'
        else:
            self.jogador = 'O'

    def fazer_jogada(self):
        jogada = -1
        valida = False
        while not valida:
            # Pede a jogada
            jogada = int(input(f'Onde você quer jogar ({self.jogador})? '))
            # Verifica se a jogada é válida
            if jogada < 0 or jogada > 8:
                # Jogada inválida, fora do tabuleiro
                print(f'Índice {jogada} fora do tabuleiro [0-8].')
            elif self.tabuleiro[jogada] in ['X', 'O']:
                # Jogada inválida, índice ocupado
                print('Esta casa já está ocupada.')
            else:
                # Jogada válida, encerra o laço
                valida = True
        # Temos uma jogada válida, vamos marcá-la no tabuleiro
        self.tabuleiro[jogada] = self.jogador

    def verificar_vencedor(self):
        empate = True
        verificacoes = [
            [0,1], [3,1], [6,1],  # linhas
            [0,3], [1,3], [2,3],  # colunas
            [0,4], [2,2]          # diagonais
        ]
        # Executar todas as verificações
        for inicio, incremento in verificacoes:
            temp = self.verificar(inicio, incremento)
            if temp in ['X', 'O']:
                # Um jogador venceu, retorna o vencedor
                return temp
            empate = empate and temp == '='
        if empate:
            return '='
        return ''

    def verificar(self, inicio, inc):
        vencedor = self.tabuleiro[inicio]
        for i in range(1,3):
            casa = self.tabuleiro[inicio + i * inc]
            if casa.isnumeric():
                return ''
            if vencedor != self.tabuleiro[inicio + i * inc]:
                return '='
        return vencedor


if __name__ == '__main__':
    jogo = Velha()
    jogo.jogar()