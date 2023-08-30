# importing required librarys
import time

from stockfish import Stockfish
import pygame
import chess
import math
from time import sleep

move_num = 0

e = Stockfish(path="stockf/stockfish-windows-x86-64-avx2.exe", depth=10)
e.update_engine_parameters({"Hash": 2048, "UCI_Elo": 2000, "MultiPV": 3, "Threads": 4})
# initialise display
X = 1500
Y = 800
EVAL_BAR_WIDTH = 20
GRAPH_WIDTH = 680
GRAPH_HEIGHT = 100
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
RETRY_POS = (900, 700)
RETRY_SIZE = (200, 100)

SQUARE_SIZE = BOARD_WIDTH / 8
# basic colours
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
YELLOW = (204, 204, 0)
BLUE = (50, 255, 255)
Graph_Dark = (30, 33, 29)
Graph_Light = (209, 237, 199)
Background_Light = (212, 247, 178)
Background_Dark = (131, 179, 86)
# initialise chess board
Move_List = []
b = chess.Board()


# load piece images


def parse_pgn(filepath="""C:\\Users\\justi\\Desktop\\stockfish_py\\BlunderBrand0n_vs_ForeverEmo_2023.07.24.pgn"""):
    with open(filepath, 'r') as file:
        txt = file.read()
    one_idx = txt.rfind(']') + 1
    p_split = txt[one_idx:].strip().replace('\n', ' ').split('.')
    p_split.pop(0)
    moveList = []
    for move in p_split:
        trim = move.strip().split(' ')
        if 'e.p.' in trim:
            trim[trim.index('e.p.') - 1] += 'e.p.'
            trim[1] += trim[2]
        mTupe = (trim[0], trim[1])
        moveList.append(mTupe)
    return moveList


def to_alg(num):
    return chr(num % 8 + 97) + str(num // 8 + 1)


def to_square_num(c):
    try:
        return (int(c[1]) - 1) * 8 + ord(c[0]) - 97
    except:
        return 'castling'


def algToUci(algMove, board):
    if algMove == '1-0' or algMove == '0-1' or algMove == '1/2-1/2':
        return "GAME OVER"
    algMove = algMove.replace('+', '').replace('#', '')
    algLen = len(algMove)
    toSquare = to_square_num(algMove[algLen - 2:])

    def correctPiece(move):
        from_notation = algMove[:len(algMove) - 2]
        from_notation = from_notation.replace('x', '')
        if len(from_notation) < 2:
            return True
        if from_notation[1].isalpha():
            file = (ord(from_notation[1]) - 97)
            if move.from_square % 8 == file:
                return True
        else:
            rank = int(from_notation[1])
            if move.from_square // 8 + 1 == rank:
                return True

        return False

    def piece(move):  #
        # print(f"piece: {str(board.piece_at(move.from_square)).lower()} == {algMove[0]}\n{move.to_square} == {toSquare}")
        if not str(board.piece_at(move.from_square)).lower() == algMove[0].lower():
            return False
        if not move.to_square == toSquare:
            return False
        return True

    def pawn(move):  #
        return move.to_square == toSquare and str(move)[0] == str(move)[2]

    def pieceTakes(move):  #
        if not board.piece_at(move.to_square):
            return False
        if not str(board.piece_at(move.from_square)).lower() == str(algMove)[0].lower():
            return False
        if not toSquare == move.to_square:
            return False
        return True

    def pawnTakes(move):  #
        if not board.piece_at(move.to_square):
            return False
        if not str(board.piece_at(move.from_square)).lower() == 'p':
            return False
        if not toSquare == move.to_square:
            return False
        return True

    def castle(move):
        # foo = [str(board.piece_at(move.from_square)).lower() == 'k', move.to_square == 2 or move.to_square == 6]
        # if True in foo:
        # print(f"\n toSquare:{toSquare}")
        # print(f"{str(board.piece_at(move.from_square)).lower()} == k\n{move.to_square} == 2 or {move.to_square} == 6")
        # print(f"{str(board.piece_at(move.from_square)).lower() == 'k'} or {move.to_square == 2 or move.to_square == 6}")
        if not str(board.piece_at(move.from_square)).lower() == 'k':
            return False
        if move.to_square == 2 or move.to_square == 6 or move.to_square == 58 or move.to_square == 62:
            return True
        return False

    if "0-0" in algMove or "O-O" in algMove:
        evalFunc = castle
    elif toSquare == 'castling':
        print(f"Broke on {algMove} could not find evalFunc (castling)")
        return "PAUSE"
    elif 'x' in algMove:
        if algMove[0].upper() == algMove[0]:
            evalFunc = pieceTakes
        else:
            evalFunc = pawnTakes
    elif algLen == 2:
        evalFunc = pawn
    elif '-' not in algMove:
        evalFunc = piece

    else:
        print(f"Broke on {algMove} could not find evalFunc")
        return "PAUSE"

    for move in board.legal_moves:
        evf = evalFunc(move)
        tsec = toSquare == 'castling'
        cpm = correctPiece(move)
        # print(f"{evf} {tsec} {cpm}")
        if evf and (tsec or cpm):
            return move
    print(f"Broke on {algMove} could not find legal move with {evalFunc.__name__}")
    return "PAUSE"


def update(scrn, board, evaluation, piece_moved=-1, holding=-1):
    '''
    updates the screen basis the board class
    '''
    retry_rect = pygame.Rect(RETRY_POS, RETRY_SIZE)
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render("RETRY", True, (0, 0, 0), WHITE)
    scrn.blit(text, retry_rect)
    graph_rect = pygame.Rect((BOARD_WIDTH + EVAL_BAR_WIDTH, 0), (GRAPH_WIDTH, GRAPH_HEIGHT))
    pygame.draw.rect(scrn, Graph_Dark, graph_rect)
    graph_move_width = int(GRAPH_WIDTH / len(eval_graph))
    last_evaluation = 50
    for i, eva in enumerate(eval_graph):
        normalized_eva = int(eva * GRAPH_HEIGHT)
        if normalized_eva > GRAPH_HEIGHT:
            normalized_eva = GRAPH_HEIGHT
        elif normalized_eva < 0:
            normalized_eva = 0

        points = [(BOARD_WIDTH + EVAL_BAR_WIDTH + 20 + ((i - 1) * graph_move_width), GRAPH_HEIGHT - last_evaluation),
                  (BOARD_WIDTH + EVAL_BAR_WIDTH + 20 + (i * graph_move_width), GRAPH_HEIGHT - normalized_eva),
                  (BOARD_WIDTH + EVAL_BAR_WIDTH + 20 + (i * graph_move_width), GRAPH_HEIGHT),
                  (BOARD_WIDTH + EVAL_BAR_WIDTH + 20 + ((i - 1) * graph_move_width), GRAPH_HEIGHT)]
        if i % 10 == 0:
            font = pygame.font.Font('freesansbold.ttf', 16)
            text = font.render(str(int(i / 2)), True, (0, 0, 0), WHITE)
            scrn.blit(text, (BOARD_WIDTH + EVAL_BAR_WIDTH + 20 + ((i - 1) * graph_move_width), 110))
        # print(f"e:{eva} ne:{normalized_eva}")
        graph_trapazoid = pygame.draw.polygon(scrn, Graph_Light, points)
        last_evaluation = normalized_eva
    for i in range(0, 64):
        r = pygame.Rect(((i % 8) * SQUARE_SIZE + 20, BOARD_WIDTH - SQUARE_SIZE - (i // 8) * SQUARE_SIZE),
                        (SQUARE_SIZE, SQUARE_SIZE))
        if (i + (i // 8)) % 2 == 1:
            pygame.draw.rect(scrn, Background_Light, r)
        else:
            pygame.draw.rect(scrn, Background_Dark, r)

    normalized_eval = ((evaluation['value'] * -1 + 1000) / 2000) * 800
    rect2 = pygame.Rect((0, int(normalized_eval)), (20, 800 - int(normalized_eval)))
    rect1 = pygame.Rect((0, 0), (20, int(normalized_eval)))
    pygame.draw.rect(scrn, Background_Dark, rect1)
    pygame.draw.rect(scrn, Background_Light, rect2)
    for i in range(64):
        piece = board.piece_at(i)
        if piece == None:
            pass
        elif i == holding:
            pos = pygame.mouse.get_pos()
            scrn.blit(pieces[str(piece)], (pos[0] - int(SQUARE_SIZE / 4), pos[1] - int(SQUARE_SIZE / 4)))
        else:
            scrn.blit(pieces[str(piece)],
                      ((i % 8) * SQUARE_SIZE + 38, BOARD_WIDTH - SQUARE_SIZE - (i // 8) * SQUARE_SIZE + 16))
            if i == piece_moved:
                print(f"[{move_num}] {eval_graph[move_num]} -> {eval_graph[move_num - 1]}")
                if move_num > 0:
                    evalChange = eval_graph[move_num] - eval_graph[move_num - 1]
                else:
                    evalChange = eval_graph[move_num] - 0.5

                evalChange *= 100
                sign = '-'
                abs_eval_change = math.fabs(evalChange)
                move_quality = False
                color_move = move_num % 2  # even = white
                evalString = ""
                if (evalChange > 0 and color_move == 0) or (evalChange < 0 and color_move == 1):  # good
                    move_quality = True
                if move_quality:
                    sign = '+'
                print(f"evalChange:{evalChange}, colorMove:{color_move}, moveQuality:{move_quality}")
                if abs_eval_change > 50:
                    if move_quality:  # brilliantly good
                        evalString = "!!!!"
                    else:  # catastrophically bad
                        evalString = "????"
                elif abs_eval_change > 30:
                    if move_quality:  # extreemly good
                        evalString = "!!!"
                    else:  # extreemly bad
                        evalString = "???"
                elif abs_eval_change > 15:
                    if move_quality:  # very good
                        evalString = "!!"
                    else:  # very bad
                        evalString = "??"
                elif abs_eval_change > 5:
                    if move_quality:  # kinda good
                        evalString = "!"
                    else:  # kinda bad
                        evalString = "?"

                evalString = sign + str(math.fabs(int(evalChange))) + evalString
                font = pygame.font.Font('freesansbold.ttf', 16)
                text = font.render(evalString, True, (0, 0, 0), None)
                scrn.blit(text, (
                (i % 8) * SQUARE_SIZE + 38 + 30, BOARD_WIDTH - SQUARE_SIZE - (i // 8) * SQUARE_SIZE + 18 - 10))

    pygame.display.flip()


def calc_eval_graph():
    board = chess.Board()
    eval_arr = []
    for mv_num in range(0, len(pgn_moves) * 2):
        color = mv_num % 2
        move = int(mv_num / 2)
        move = algToUci(pgn_moves[move][color], board)
        e.make_moves_from_current_position([move, ])
        board.push(move)
        evaluation = e.get_evaluation()
        normalized_eval = ((evaluation['value'] + 1000) / 2000)
        eval_arr.append(normalized_eval)
        print(normalized_eval)
    e.set_position([])
    return eval_arr


def undo_move(board):
    global move_num
    global Move_List
    move_num -= 1
    popped_move = board.pop()
    Move_List.pop()
    e.set_position(Move_List)
    return popped_move


def make_move(board, move):
    global Move_List
    global move_num
    move_num += 1
    Move_List.append(move)
    e.make_moves_from_current_position([move, ])
    print(e.get_board_visual())
    board.push(move)


def set_board(board):
    e.set_position([])
    e.get_board_visual()
    board.reset_board()
    for i in range(0, move_num + 1):
        color = i % 2
        mv_num = int(i / 2)
        make_move(board, algToUci(pgn_moves[mv_num][color], board))


holding_piece = None
retrying_move = False
arrow_down_start = pygame.time.get_ticks()
arrow_down = None
start_click_location = None
pieceSelectLocation = None
index_moves = []
input_empty = {
    "arrow": None,  # step move forward/backward
    "pickingUpPiece": False,  # if true, picking piece up
    "piecePickupLocation": None,  #
    "pieceDropLocation": None,  #
    "retryClicked": False,
    "goingOffScript": False,
    "move": None
}


def proc_input(board):
    events = pygame.event.get()
    input_dic = {
        "arrow": None,  # step move forward/backward
        "pickingUpPiece": False,  # if true, picking piece up
        "piecePickupLocation": None,  #
        "pieceDropLocation": None,  #
        "retryClicked": False,
        "goingOffScript": False,
        "move": None
    }

    def pos_on_board(pos):
        if pos[0] - 20 < BOARD_WIDTH and pos[1] < BOARD_WIDTH and pos[0] > EVAL_BAR_WIDTH:
            square = (math.floor((pos[0] - EVAL_BAR_WIDTH) / SQUARE_SIZE), math.floor(pos[1] / 100))
            index = (7 - square[1]) * 8 + (square[0])
            if 0 < index < 64:
                return index
        return None

    global index_moves
    global start_click_location
    global holding_piece
    global retrying_move
    global pieceSelectLocation
    global arrow_down_start
    global arrow_down
    for event in events:
        if event.type == pygame.QUIT:
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_click_location = pygame.mouse.get_pos()
            start_click_square = pos_on_board(start_click_location)
            if pieceSelectLocation is None:
                piece = board.piece_at(start_click_square)
                if piece is not None:
                    input_dic["pickingUpPiece"] = True
                    input_dic["piecePickupLocation"] = start_click_square
                    all_moves = list(board.legal_moves)
                    index_moves = []
                    for m in all_moves:
                        if m.from_square == start_click_square:
                            index_moves.append(m)
                            holding_piece = True
                    print(f"selected piece: {index_moves}")
            # pick up piece
        elif event.type == pygame.MOUSEBUTTONUP:
            holding_piece = False
            stop_click_location = pygame.mouse.get_pos()
            start_click_square = pos_on_board(start_click_location)
            stop_click_sqaure = pos_on_board(stop_click_location)
            if start_click_square is not None and start_click_square == stop_click_sqaure:  # clicked a square
                print(f'PSL:{pieceSelectLocation}')
                if pieceSelectLocation is not None:  # click moved a piece
                    index_moves_to_square = [a.to_square for a in index_moves]
                    print(f"moving piece {index_moves}")
                    if start_click_square in index_moves_to_square:
                        print(f"got here")
                        move = index_moves[index_moves_to_square.index(start_click_square)]
                        index_moves = []
                        input_dic["move"] = move
                    pieceSelectLocation = None

                    pass
                else:  # click select a piece
                    pieceSelectLocation = stop_click_sqaure
            elif start_click_square is not None and stop_click_sqaure is not None:
                index_moves_to_square = [a.to_square for a in index_moves]
                if stop_click_sqaure in index_moves_to_square:
                    move = index_moves[index_moves_to_square.index(stop_click_sqaure)]
                    index_moves = []
                    input_dic["move"] = move
                pieceSelectLocation = None
                # drag to square
            else:  # not on board
                pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                input_dic["arrow"] = event.key
                arrow_down_start = pygame.time.get_ticks()
                arrow_down = event.key
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                input_dic["arrow"] = None
                arrow_down_start = None
                arrow_down = None
        elif arrow_down_start is not None and pygame.time.get_ticks() < arrow_down_start + 500:
            input_dic["arrow"] = arrow_down
    return input_dic


def main(BOARD):
    global move_num
    pygame.key.set_repeat(50)
    gameOver = False
    evaluation = -1
    pygame.display.set_caption('Chess')
    index_moves = []
    status = True
    waitingForPlayerMove = False
    last_move_was_retry = False
    temp_moves = []
    update(scrn, BOARD, e.get_evaluation(), 0)
    holding_piece_square = -1
    onScript = True
    last_script_location = 0
    while (status):
        inputs = proc_input(BOARD)
        if inputs is None:
            status = False
        else:
            if not inputs == input_empty:
                print(inputs)
            if holding_piece and inputs["piecePickupLocation"] is not None:
                holding_piece_square = inputs["piecePickupLocation"]
            if not holding_piece:
                holding_piece_square = -1
            if inputs['move'] is not None:
                mv = inputs['move']
                if not mv == pgn_moves[move_num]:
                    onScript = False
                    last_script_location = move_num
                make_move(BOARD, inputs['move'])
            if inputs["arrow"] is not None and not onScript:
                set_board(BOARD)
                move_num = last_script_location
            elif inputs["arrow"] == pygame.K_LEFT:
                undo_move(BOARD)
            elif inputs["arrow"] == pygame.K_RIGHT:
                color = move_num % 2
                mv_num = int(move_num / 2)
                make_move(BOARD, algToUci(pgn_moves[mv_num][color], BOARD))

            update(scrn, BOARD, e.get_evaluation(), holding=holding_piece_square)
            if BOARD.outcome() is not None:
                if not gameOver:
                    outcome = BOARD.outcome()
                    result = outcome.result()
                    winner = outcome.winner
                    if not winner is None:
                        print(f"{outcome.winner}")
                    else:
                        print("Draw")
                    gameOver = True
            elif gameOver:
                gameOver = False
    pygame.quit()


if __name__ == '__main__':
    pgn_moves = parse_pgn()
    eval_graph = calc_eval_graph()
    scrn = pygame.display.set_mode((X, Y))
    pygame.init()
    pieces = {'p': pygame.image.load('img/blackp.png').convert_alpha(),
              'n': pygame.image.load('img/blackn.png').convert_alpha(),
              'b': pygame.image.load('img/blackb.png').convert_alpha(),
              'r': pygame.image.load('img/blackr.png').convert_alpha(),
              'q': pygame.image.load('img/blackq.png').convert_alpha(),
              'k': pygame.image.load('img/blackk.png').convert_alpha(),
              'P': pygame.image.load('img/whitep.png').convert_alpha(),
              'N': pygame.image.load('img/whiten.png').convert_alpha(),
              'B': pygame.image.load('img/whiteb.png').convert_alpha(),
              'R': pygame.image.load('img/whiter.png').convert_alpha(),
              'Q': pygame.image.load('img/whiteq.png').convert_alpha(),
              'K': pygame.image.load('img/whitek.png').convert_alpha(),

              }
    main(b)
