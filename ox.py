import tkinter
import tkinter.messagebox
import random
from enum import Enum

FS = ("Times New Roman", 20)
FL = ("Times New Roman", 40)

BOARD_SIZE = 3
CANVAS_WIDTH = 480 # 盤面の横幅(px)
CANVAS_HEIGHT = 480 # 盤面の縦幅(px)
SQUARE_WIDTH = CANVAS_WIDTH // BOARD_SIZE # マスの横幅(px)
SQUARE_HEIGHT = CANVAS_HEIGHT // BOARD_SIZE # マスの縦幅(px)

BLACK = 1
WHITE = 2
COLOR_LIST = [BLACK, WHITE]

class Phase(Enum):
    STANDBY = 0
    MAIN = 1
    END = 2
    RESULT = 3

mx = 0 # クリックしたマスのX座標
my = 0 # クリックしたマスのY座標
mc = 0 # クリックしたかどうかを判別する変数
proc = Phase.STANDBY # 進行を管理する変数
turn = 0 # 手番を管理する変数
who = ["YOU", "CPU"] # プレイヤーの手番を管理する配列
msg = "" # メッセージ

board = [] # 盤面の状況を管理する2次元配列
back = [] # 現在の盤面の状況を保存する2次元配列
placeable_square_X = [] # 配置可能なマスのX座標
placeable_square_Y = [] # 配置可能なマスのX座標

for y in range(BOARD_SIZE):
    board.append([0] * BOARD_SIZE)
    back.append([0] * BOARD_SIZE)

def click(e): # クリックされた時に呼び出し
    global mx, my, mc
    mx = e.x // SQUARE_WIDTH # クリックしたマスのX座標を判定
    my = e.y // SQUARE_HEIGHT # クリックしたマスのY座標を判定
    if 0 <= mx and mx < BOARD_SIZE and 0 <= my and my < BOARD_SIZE: # 盤面内をクリックしたら
        mc = 1 # クリック判定

def display_board(): # 盤面を表示する関数
    cvs.delete("all") # 初期化
    cvs.create_text(SQUARE_WIDTH*1.5, CANVAS_HEIGHT+30, text=msg, fill="silver", font=FS) # 下部にメッセージを表示
    
    for i in range(BOARD_SIZE):
        X = i * SQUARE_WIDTH
        Y = i * SQUARE_HEIGHT
        # 線を引く
        cvs.create_line(0, Y+SQUARE_HEIGHT, CANVAS_WIDTH, Y+SQUARE_HEIGHT, fill="black", width=2)
        cvs.create_line(X+SQUARE_WIDTH, 0, X+SQUARE_WIDTH, CANVAS_HEIGHT, fill="black", width=2)
    
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            X = x * SQUARE_WIDTH
            Y = y * SQUARE_HEIGHT
            
            # マスに円を描写
            if board[y][x] == BLACK:
                cvs.create_oval(X+10, Y+10, X+SQUARE_WIDTH-10, Y+SQUARE_HEIGHT-10, fill="black", width=0)
            elif board[y][x] == WHITE:
                cvs.create_oval(X+10, Y+10, X+SQUARE_WIDTH-10, Y+SQUARE_HEIGHT-10, fill="white", width=0)
    cvs.update()

def init_board(): # 盤面を初期化する関数
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            board[y][x] = 0

def match_over(): # 勝負がついたかどうか判定する関数
    # 横で一列揃ったか判定
    for y in range(BOARD_SIZE):
        check_color = board[y][0]
        for x in range(1, BOARD_SIZE):
            if board[y][x] != check_color:
                continue
            return check_color
    
    # 縦で一列揃ったか判定
    for x in range(BOARD_SIZE):
        check_color = board[0][x]
        for y in range(1, BOARD_SIZE):
            if board[y][x] != check_color:
                continue
            return check_color
    
    # 斜めで一列揃ったか判定
    check_color = board[0][0]
    for i in range(1, BOARD_SIZE):
        if board[i][i] != check_color:
            continue
        return check_color
    check_color = board[BOARD_SIZE-1][0]
    for i in range(1, BOARD_SIZE):
        if board[BOARD_SIZE-1-i][i] != check_color:
            continue
        return check_color
    
    return 0
    
def place_disc(x, y, color): # OXを置く関数
    board[y][x] = color

def is_placeable(x, y): # そのマスにOXを置けるか判定する関数
    if board[y][x] > 0:
        return False
    return True

def placeable_square_existence(): # まだOXを置けるかどうか判定する関数
    placeable_square_X.clear()
    placeable_square_Y.clear()
    
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if is_placeable(x, y):
                placeable_square_X.append(x)
                placeable_square_Y.append(y)
    
    if len(placeable_square_X) > 0:
        return True
    return False

def save(): # 盤面をセーブ (CPU用)
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            back[y][x] = board[y][x]

def load(): # 盤面をロード (CPU用)
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            board[y][x] = back[y][x]

def simulate(color): # 現在の盤面からランダムに置く試行をする関数
    while True:
        if placeable_square_existence() == False or match_over() > 0:
            break
        color = 3 - color
        k = random.randint(0, (len(placeable_square_X)-1))
        x = placeable_square_X[k]
        y = placeable_square_Y[k]
        place_disc(x, y, color)

def computer(color, loops): # CPUが打つ手を探索する関数
    global msg
    win = [0]*(BOARD_SIZE * BOARD_SIZE)
    
    save()
    
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if is_placeable(x, y):
                msg += "."
                display_board()
                win[y*BOARD_SIZE+x] = 1
                
                for i in range(loops):
                    place_disc(x, y, color)
                    simulate(color)
                    if match_over() == color:
                        win[y*BOARD_SIZE+x] += 1
                    load()
    
    m = 0
    n = 0
    for i in range(BOARD_SIZE * BOARD_SIZE):
        if win[i] > m:
            m = win[i]
            n = i
    x = n % BOARD_SIZE
    y = n // BOARD_SIZE
    
    return x, y

def main():
    global proc, turn, mc, msg
    display_board()

    if proc == Phase.STANDBY:
        msg = "先手 or 後手？"
        cvs.create_text(SQUARE_WIDTH*1.5, SQUARE_HEIGHT*1, text="Tic-Tac-Toe", fill="gold", font=FL)
        cvs.create_text(SQUARE_WIDTH//2, SQUARE_HEIGHT*2.5, text="先手(O)", fill="lime", font=FS)
        cvs.create_text(SQUARE_WIDTH*2.5, SQUARE_HEIGHT*2.5, text="後手(X)", fill="lime", font=FS)

        if mc == 1:
            mc = 0
            if mx == 0 and my == 2:
                init_board()
                COLOR_LIST[0] = BLACK
                COLOR_LIST[1] = WHITE
                turn = 0
                proc = Phase.MAIN
            if mx == 2 and my == 2:
                init_board()
                COLOR_LIST[0] = WHITE
                COLOR_LIST[1] = BLACK
                turn = 1
                proc = Phase.MAIN
    
    elif proc == Phase.MAIN:
        if turn == 0:
            msg = "Your Turn"
            if mc == 1:
                if is_placeable(mx, my):
                    place_disc(mx, my, COLOR_LIST[turn])
                    proc = Phase.END
                mc = 0
        else:
            msg = "CPU's Turn"
            cx, cy = computer(COLOR_LIST[turn], 100)
            place_disc(cx, cy, COLOR_LIST[turn])
            proc = Phase.END
    
    elif proc == Phase.END:
        msg = ""
        turn = 1 - turn
        if placeable_square_existence() == False:
            proc = Phase.RESULT
        else:
            proc = Phase.MAIN
    
    elif proc == Phase.RESULT:
        if COLOR_LIST[0] == match_over():
            tkinter.messagebox.showinfo("", "YOU WIN!")
        elif COLOR_LIST[1] == match_over():
            tkinter.messagebox.showinfo("", "YOU LOSE...")
        else:
            tkinter.messagebox.showinfo("", "DRAW")
        
        proc = Phase.STANDBY

    root.after(100, main)

root = tkinter.Tk() # ウィンドウオブジェクト
root.title("Tic-Tac-Toe") # ウィンドウタイトル
root.resizable(False, False) # ウィンドウのサイズ変更不可
root.bind("<Button>", click) # マウスをクリックしたときにクリック関数を呼び出し
cvs = tkinter.Canvas(width=CANVAS_WIDTH, height=CANVAS_HEIGHT+60, bg="green") # キャンバス
cvs.pack() # ウィンドウにキャンバスを設置
root.after(100, main)
root.mainloop() # ウィンドウを表示