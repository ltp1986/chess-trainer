# -*- coding: utf-8 -*-
"""
象棋自动复盘系统 - 测试配置文件
"""
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试目录（使用当前项目下的test文件夹）
WATCH_DIR = os.path.join(PROJECT_ROOT, "test")

# 输出目录（使用当前项目下的test_output文件夹）
REPORT_DIR = os.path.join(PROJECT_ROOT, "test_output", "report")
EXERCISE_DIR = os.path.join(PROJECT_ROOT, "test_output", "exercise")

# Stockfish配置（测试时可留空）
STOCKFISH_PATH = ""
STOCKFISH_DEPTH = 25

# 分析记录文件
ANALYZED_FILE = os.path.join(WATCH_DIR, "analyzed.txt")

# 习题配置
EXERCISE_COUNT = 10
DIFFICULTY_LEVEL = "二级~一级"  # 棋协二级~一级
