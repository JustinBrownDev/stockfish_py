import os


class Game:
    idx = 9
    date = ""
    playerW = ""
    playerB = ""
    winner = ""
    whiteElo = ""
    blackElo = ""
    timeControl = ""
    endTime = ""
    terminationMessage = ""
    moveList = []
    timeList = []



def parsePgn(filepath):
    gameList = []
    class_idx = 0
    with open(filepath, 'r') as file:
        txt = file.read()
    info_idx = 0
    moves_idx = txt.find('\n\n')
    while not info_idx == -1 and not moves_idx == -1:
        gameList.append(Game())
        gameList[class_idx].idx = class_idx
        for item in txt[info_idx:moves_idx].split('\n'):
            value = item[item.find('"') + 1: item.rfind('"')]
            if item[:5] == "[Date":
                gameList[class_idx].date = value
            elif item[:7] == "[White ":
                gameList[class_idx].playerW = value
            elif item[:7] == "[Black ":
                gameList[class_idx].playerB = value
            elif item[:7] == "[Result":
                gameList[class_idx].winner = value
            elif item[:9] == "[WhiteElo":
                gameList[class_idx].whiteElo = value
            elif item[:9] == "[BlackElo":
                gameList[class_idx].blackElo = value
            elif item[:12] == "[TimeControl":
                gameList[class_idx].timeControl = value
            elif item[:8] == "[EndTime":
                gameList[class_idx].endTime = value
            elif item[:12] == "[Termination":
                gameList[class_idx].terminationMessage = value
        info_idx = txt.find('\n\n', moves_idx + 1)
        p_split = txt[moves_idx:info_idx].strip().replace('\n', ' ').split('.')
        move_list = []
        timeList = []
        for move in p_split:
            if len(move) > 1:
                trim = move.strip().split(' ')
                for item in trim:
                    if '{' not in item and '}' not in item and len(item) > 1 and not item.isnumeric():
                        if ':' in item:
                            timeList.append(item)
                        else:
                            move_list.append(item)
        gameList[class_idx].timeList = timeList
        clumped_movelist = []
        moveBuf = ''
        for i,mv in enumerate(move_list):
            if i % 2 == 0:
                moveBuf = mv
                if i == len(move_list)-1:
                    clumped_movelist.append((moveBuf, ''))
            else:
                clumped_movelist.append((moveBuf, mv))
        gameList[class_idx].moveList = clumped_movelist
        moves_idx = txt.find('\n\n', info_idx + 1)
        class_idx += 1

    return gameList
def enumerate_pgns():
    dirPath = """C:\\Users\\justi\\Desktop\\stockfish_py\\pgns\\"""
    dirList = [dirPath + f for f in os.listdir(dirPath)]
    return dirList

def get_all_games():
    gamList = []
    for pgn in enumerate_pgns():
        gamList += parsePgn(pgn)
    return gamList

for g in get_all_games():
    print(f"{g.playerW}[{g.whiteElo}] vs {g.playerB}[{g.blackElo}]")
    print(g.moveList)
    print(g.terminationMessage, g.winner)