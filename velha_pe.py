"""Jogo da Velha"""


def jogar():
    # O tabuleiro é uma lista de strings.
    # Casas vazias contêm o seu índice.
    tabuleiro: list[str] = [str(i) for i in range(9)] 
    # O jogador X começa jogando
    jogador = 'X'
    # O vencedor pode ser 'X', 'O', '=' (empate) ou '' (indefinido, ainda está jogando)
    vencedor = ''
    # Aqui começa o jogo
    while vencedor == '':
        exibir(tabuleiro)
        fazer_jogada(jogador, tabuleiro)
        vencedor = verificar_vencedor(tabuleiro)
        jogador = trocar_jogador(jogador)
    exibir(tabuleiro)
    print(f'O vencedor é {vencedor}')

def exibir(tabuleiro):
    for i in range(3):
        for j in range(3):
            print(tabuleiro[3 * i + j], end=' ')
        print()

def trocar_jogador(atual):
    if atual == 'O':
        return 'X'
    return 'O'

def fazer_jogada(jogador, tabuleiro):
    jogada = -1
    valida = False
    while not valida:
        # Pede a jogada
        jogada = int(input(f'Onde você quer jogar ({jogador})? '))
        # Verifica se a jogada é válida
        if jogada < 0 or jogada > 8:
            # Jogada inválida, fora do tabuleiro
            print(f'Índice {jogada} fora do tabuleiro [0-8].')
        elif tabuleiro[jogada] in ['X', 'O']:
            # Jogada inválida, índice ocupado
            print('Esta casa já está ocupada.')
        else:
            # Jogada válida, encerra o laço
            valida = True
    # Temos uma jogada válida, vamos marcá-la no tabuleiro
    tabuleiro[jogada] = jogador

def verificar_vencedor(tabuleiro):
    empate = True
    verificacoes = [
        [0,1], [3,1], [6,1],  # linhas
        [0,3], [1,3], [2,3],  # colunas
        [0,4], [2,2]          # diagonais
    ]
    # Executar todas as verificações
    for inicio, incremento in verificacoes:
        temp = verificar(tabuleiro, inicio, incremento)
        if temp in ['X', 'O']:
            # Um jogador venceu, retorna o vencedor
            return temp
        empate = empate and temp == '='
    if empate:
        return '='
    return ''

def verificar(tabuleiro, inicio, inc):
    vencedor = tabuleiro[inicio]
    for i in range(1,3):
        casa = tabuleiro[inicio + i * inc]
        if casa.isnumeric():
            return ''
        if vencedor != tabuleiro[inicio + i * inc]:
            return '='
    return vencedor


if __name__ == '__main__':
    jogar()