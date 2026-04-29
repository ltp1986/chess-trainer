import os,time,chess,chess.pgn,chess.engine
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics,cidfonts

pdfmetrics.registerFont(cidfonts.UnicodeCIDFont('STSong-Light'))
FONT_CN = 'STSong-Light'

WATCH = r"D:\Chess_PGN_Receive"
OUT = r"D:\Chess_Output"
LOG = os.path.join(OUT,"analyzed.txt")
DEPTH = 25
BIG_STEP = 50
MIN_STEP = 4

def ensure_out_dirs():
    os.makedirs(OUT,exist_ok=True)
    os.makedirs(os.path.join(OUT,"复盘"),exist_ok=True)
    os.makedirs(os.path.join(OUT,"习题"),exist_ok=True)

def find_engine():
    custom = r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"
    if os.path.exists(custom):return custom
    for n in ["stockfish.exe","stockfish-windows.exe"]:
        if os.path.exists(n):return n
        if os.path.exists(f"./engine/{n}"):return f"./engine/{n}"
    raise Exception("请放置stockfish.exe")

def load_analyzed():
    ensure_out_dirs()
    if not os.path.exists(LOG):return set()
    with open(LOG,"r",encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip()}

def mark_analyzed(name):
    ensure_out_dirs()
    with open(LOG,"a",encoding="utf-8") as f:f.write(name+"\n")

def is_valid_pgn(path):
    if not path.endswith(".pgn"):return False
    if os.path.getsize(path)==0:return False
    try:
        with open(path,encoding="utf-8") as f:
            game=chess.pgn.read_game(f)
        if not game:return False
        moves=list(game.mainline_moves())
        return len(moves)>=MIN_STEP
    except:
        return False

def get_step_count(path):
    try:
        with open(path,encoding="utf-8") as f:
            game=chess.pgn.read_game(f)
        return len(list(game.mainline_moves())) if game else 0
    except:
        return 0

def progress(cur,total,s):
    pct=cur/total
    bar="█"*int(pct*20)+"▁"*(20-int(pct*20))
    ela=time.time()-s
    eta=ela/cur*(total-cur)if cur>0 else 0
    print(f"\r{cur}/{total} | {int(pct*100)}% {bar} 剩余{int(eta//60):02d}:{int(eta%60):02d}",end="")

def analyze_one(path):
    name=os.path.basename(path)
    with open(path,encoding="utf-8") as f:game=chess.pgn.read_game(f)
    if not game:return None,[]
    b=game.board()
    e=chess.engine.SimpleEngine.popen_uci(find_engine())
    moves=list(game.mainline_moves())
    total=len(moves)
    scores=[]
    s=time.time()
    print(f"\n分析：{name} 步数：{total}")
    for i,m in enumerate(moves,1):
        res=e.analyse(b,chess.engine.Limit(depth=DEPTH))
        scores.append(res["score"].white().score(mate_score=1000))
        b.push(m)
        progress(i,total,s)
    e.quit()
    print("\n完成")
    mistakes=[]
    for i in range(1,len(scores)):
        d=scores[i]-scores[i-1]
        if d<-150:
            mistakes.append({"step":i+1,"move":moves[i].uci(),"loss":-d})
    return game,(mistakes[:5]if len(mistakes)>=5 else mistakes)

def pdf_report(game,errs,name):
    ensure_out_dirs()
    dt=datetime.now().strftime("%Y%m%d_%H%M%S")
    c=canvas.Canvas(os.path.join(OUT,"复盘",f"报告_{name}_{dt}.pdf"),pagesize=A4)
    c.setFont(FONT_CN,12)
    c.drawString(50,800,"专业复盘报告")
    c.drawString(50,770,f"白：{game.headers.get('White','?')}")
    c.drawString(50,750,f"黑：{game.headers.get('Black','?')}")
    c.drawString(50,730,f"结果：{game.headers.get('Result','?')}")
    y=690
    for m in errs:
        c.drawString(50,y,f"第{m['step']}步 失分{m['loss']}cp {m['move']}")
        y-=20
    c.save()

def pdf_exam(name):
    ensure_out_dirs()
    dt=datetime.now().strftime("%Y%m%d_%H%M%S")
    c=canvas.Canvas(os.path.join(OUT,"习题",f"习题_{name}_{dt}.pdf"),pagesize=A4)
    c.setFont(FONT_CN,12)
    c.drawString(50,820,"专项习题集")
    c.drawString(50,800,f"来源：{name}")
    c.drawString(50,780,"题数：10")
    y=740
    for i in range(1,11):
        c.drawString(50,y,f"第{i}题：找出最佳着法")
        y-=25
    c.save()

def process_batch(files):
    analyzed=load_analyzed()
    big=[]
    small=[]
    for f in files:
        path=os.path.join(WATCH,f)
        step=get_step_count(path)
        if step>=BIG_STEP:
            big.append((step,f))
        else:
            small.append((step,f))
    big.sort(reverse=True)
    small.sort()
    for _,f in big+small:
        path=os.path.join(WATCH,f)
        game,errs=analyze_one(path)
        if not game:continue
        pdf_report(game,errs,f)
        if errs:
            pdf_exam(f)
            print(f"✅ {f} | 失误{len(errs)}个 | 已生成习题")
        else:
            print(f"✅ {f} | 无失误 | 不生成习题")
        mark_analyzed(f)

def run():
    print("=== 象棋智能复盘系统（最终版）===")
    while True:
        analyzed=load_analyzed()
        todo=[]
        for f in os.listdir(WATCH):
            path=os.path.join(WATCH,f)
            if f in analyzed:continue
            if is_valid_pgn(path):
                todo.append(f)
        if todo:
            process_batch(todo)
        time.sleep(3)

if __name__=="__main__":
    run()
