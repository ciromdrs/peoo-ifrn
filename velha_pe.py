"""Jogo da Velha"""


# FUNÇÕES

def jogar():
    '''Executa uma partida completa do Jogo da Velha.'''
    # Inicialização das variáveis
    # O jogador X começa jogando
    jogador = 'X'
    # O vencedor pode ser 'X', 'O', '=' (empate) ou '' (indefinido, ainda está jogando)
    vencedor = ''
    '''O tabuleiro é uma lista de strings.
    Casas vazias contêm o seu índice, começando em 1 e terminando em 9.
    Ex.: a lista ['1', '2', 'O', '4', 'O', 'X', 'O', '7', 'X'] corresponde ao jogo abaixo
    1|2|O
    -----
    4|O|X
    -----
    O|7|X'''
    tabuleiro: list[str] = [str(i) for i in range(9)] 
    # Aqui começa o jogo
    while vencedor == '':
        exibir(tabuleiro)
        fazer_jogada(jogador, tabuleiro)
        vencedor = verificar_vencedor(tabuleiro)
        jogador = trocar_jogador(jogador)
    exibir(tabuleiro)
    print(f'O vencedor é {vencedor}')

def exibir(tabuleiro: list[str]):
    '''Exibe o tabuleiro.'''
    for i in range(3):
        for j in range(3):
            print(tabuleiro[3 * i + j], end=' ')
        print()

def trocar_jogador(atual: str) -> str:
    '''Dado o jogador `atual`, retorna o próximo jogador.
    Ex.: se `atual == 'X'`, retorna `'O'`.'''
    if atual == 'O':
        return 'X'
    return 'O'

def fazer_jogada(jogador: str, tabuleiro: list[str]):
    '''Realiza uma jogada no tabuleiro, isto é, pede ao usuário uma posição no tabuleiro e marca com o símbolo do jogador atual.
    `jogador` é o jogador atual (X ou O).
    `tabuleiro` é a lista que representa o tabuleiro do jogo.'''
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

def verificar_vencedor(tabuleiro: list[str]) -> str:
    '''Verifica se houve um vencedor no jogo.
    Retorna:
    - 'X', se ele for o vencedor (análogo para 'O').
    - '=', se o jogo estiver empatado.
    - '' (vazio), se ainda houver posições a jogar.
    '''
    # Booleano para guardar se o jogo foi empate.
    # Assume que está empatado até que se verifique que não está.
    empate = True
    # Lista com todas as verificações necessárias para detectar um vencedor.
    # Cada elemento da lista é um par (inicio, incremento), a serem usados a seguir.
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

def verificar(tabuleiro: list[str], inicio: int, inc: int) -> str:
    '''Verifica se um sequência (linha, coluna ou diagonal) no tabuleiro contém um vencedor.

    Parâmetros:
    A combinação dos parâmetros `inicio` e `inc` descreve uma sequência (linha, coluna ou diagonal) no tabuleiro.
    O primeiro elemento da sequência está na posição `inicio`.
    Os outros dois elementos estão na posição `inicio` acrescida uma e duas vezes do incremento `inc`.
    Exemplos:
    - A primeira linha da matriz é [0, 1], pois os elementos estão nas posições 0, 1 (0+1) e 2 (0+1+1).
    - A segunda coluna é [1, 3], pois os elementos estão nas posições 1, 4 (1+3) e 7 (1+3+3).
    - A diagonal invertida é [2, 2], pois os elementos estão nas posições 2, 4 (2+2) e 6 (2+2+2).
    
    Retorno:
    - 'X' caso este seja o vencedor (análogo para 'O').
    - '=' caso a sequência esteja toda preenchida e não haja vencedor.
    - '' (vazio) caso ainda haja elementos a preencher na sequência.'''
    vencedor = tabuleiro[inicio]
    for i in range(1,3):
        casa = tabuleiro[inicio + i * inc]
        if casa.isnumeric():
            return ''
        if vencedor != tabuleiro[inicio + i * inc]:
            return '='
    return vencedor


# PROGRAMA PRINCIPAL

if __name__ == '__main__':
    jogar()