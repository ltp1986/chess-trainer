# -*- coding: utf-8 -*-
import os
WATCH_DIR = r"D:\Chess_PGN_Receive"
REPORT_DIR = r"D:\Chess_Out\report"
EXERCISE_DIR = r"D:\Chess_Out\exercise"
STOCKFISH_PATH = r"D:\stockfish\stockfish-windows-x86-64-avx2.exe"
ANALYZED_FILE = os.path.join(WATCH_DIR, "analyzed.txt")
STOCKFISH_DEPTH = 25
STOCKFISH_THREADS = 2
STOCKFISH_HASH = 128
BLUNDER_THRESHOLD = 50
MAX_BLUNDERS = 3
EXERCISE_COUNT = 10
MIN_ELO = 1400
MAX_ELO = 1650
EXERCISE_TYPES = ["牵制战术", "闪击战术", "捉双战术", "消除保护", "基础防守", "基础残局"]
PAGE_SIZE = "A4"
SHOW_BOARD_IMAGE = True
BOARD_IMAGE_SIZE = 200

# 并发配置
MAX_WORKERS = 3
ENABLE_PARALLEL = True

DEBUG_MODE = True