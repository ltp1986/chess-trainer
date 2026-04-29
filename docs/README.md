# 象棋自动复盘系统

## 项目结构

```
Chess/
├── android_autojs/              # 安卓AutoJS脚本
│   └── chess_export.js          # PGN导出脚本（MagicPad3版）
│
├── windows_python/              # Windows端程序
│   ├── src/
│   │   ├── config.py            # 配置文件
│   │   └── chess_analyzer.py    # 主程序
│   ├── config/                  # 配置目录
│   ├── assets/                  # 资源目录
│   └── requirements.txt         # Python依赖
│
└── docs/                        # 文档
    └── README.md                # 本文件
```

## 一、AutoJS脚本使用说明

### 1.1 环境准备
- 荣耀平板MagicPad3（12.5寸）
- 安装AutoJS应用
- 安装元萝卜象棋APP
- 开启无障碍服务

### 1.2 配置修改
编辑 `android_autojs/chess_export.js`，根据实际APP界面调整点击坐标。

### 1.3 运行
将脚本导入AutoJS并运行。

## 二、Windows程序使用说明

### 2.1 环境准备
- Windows 10/11
- Python 3.8+
- Stockfish象棋引擎（下载地址：https://stockfishchess.org/）

### 2.2 安装依赖
```bash
cd windows_python
pip install -r requirements.txt
```

### 2.3 配置修改
编辑 `windows_python/src/config.py`，设置正确的目录路径和Stockfish路径。

### 2.4 运行程序
```bash
cd windows_python/src
python chess_analyzer.py
```

## 三、打包成单EXE

### 3.1 安装PyInstaller
```bash
pip install pyinstaller
```

### 3.2 打包命令
```bash
cd windows_python
pyinstaller --onefile --noconsole --name "象棋复盘系统" --add-data "src/config.py;." src/chess_analyzer.py
```

打包后的EXE文件位于 `dist/` 目录。

## 四、目录说明

程序运行后会自动创建以下目录：
- `D:\Chess_PGN_Receive\` - PGN文件接收目录（存放待分析的PGN棋谱文件）
- `D:\Chess_Out\report\` - 复盘报告输出目录（生成的PDF复盘报告）
- `D:\Chess_Out\exercise\` - 习题输出目录（生成的PDF习题集）

### 4.1 Web应用配置

Web应用（`webapp/`）的PGN文件路径同样指向 `D:\Chess_PGN_Receive`，确保前后端使用同一数据源。

## 五、功能特性

- 自动监控新PGN文件
- 调用Stockfish深度分析（深度25）
- 生成PDF复盘报告
- 生成定制习题PDF（10道，难度二级~一级）
- 已分析文件自动记录，避免重复分析
- 完整中文注释
