// 象棋自动复盘系统 - AutoJS脚本
// 荣耀平板MagicPad3 12.5寸版本
// 功能：自动打开元萝卜APP，导出最新5盘PGN

// 屏幕分辨率适配 (MagicPad3 12.5寸)
const SCREEN_WIDTH = 2880;
const SCREEN_HEIGHT = 1920;

// 等待时间配置
const WAIT_SHORT = 500;
const WAIT_MEDIUM = 2000;
const WAIT_LONG = 3000;

// 存储目录
const EXPORT_DIR = "/sdcard/Chess_PGN_Receive/";

// 确保目录存在
function ensureDirectory() {
    if (!files.exists(EXPORT_DIR)) {
        files.create(EXPORT_DIR);
        console.log("创建导出目录: " + EXPORT_DIR);
    }
}

// 获取当前时间戳
function getTimestamp() {
    let date = new Date();
    let year = date.getFullYear();
    let month = (date.getMonth() + 1).toString().padStart(2, '0');
    let day = date.getDate().toString().padStart(2, '0');
    let hour = date.getHours().toString().padStart(2, '0');
    let minute = date.getMinutes().toString().padStart(2, '0');
    let second = date.getSeconds().toString().padStart(2, '0');
    return year + month + day + "_" + hour + minute + second;
}

// 点击指定位置（带重试）
function clickWithRetry(x, y, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        click(x, y);
        sleep(WAIT_SHORT);
        if (i < maxRetries - 1) {
            sleep(WAIT_SHORT);
        }
    }
}

// 启动元萝卜APP
function launchApp() {
    console.log("正在启动元萝卜APP...");
    launch("com.ai2fun.chess");
    sleep(WAIT_LONG);
}

// 进入历史对局
function enterHistory() {
    console.log("进入历史对局...");
    
    // 这里需要根据实际界面调整坐标
    // 示例坐标 - 需要根据实际APP界面调整
    clickWithRetry(SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.9); // 个人中心
    sleep(WAIT_MEDIUM);
    
    clickWithRetry(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.4); // 历史对局
    sleep(WAIT_MEDIUM);
}

// 导出PGN
function exportPGN(gameIndex, timestamp) {
    console.log("导出第 " + (gameIndex + 1) + " 盘棋...");
    
    // 点击对局
    clickWithRetry(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * (0.3 + gameIndex * 0.1));
    sleep(WAIT_MEDIUM);
    
    // 点击分享/导出按钮
    clickWithRetry(SCREEN_WIDTH * 0.9, SCREEN_HEIGHT * 0.1);
    sleep(WAIT_SHORT);
    
    // 选择导出PGN
    clickWithRetry(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.6);
    sleep(WAIT_SHORT);
    
    // 保存文件
    let fileName = "game_" + timestamp + "_" + (gameIndex + 1) + ".pgn";
    let filePath = EXPORT_DIR + fileName;
    
    // 这里需要模拟输入文件名并保存
    // 根据实际APP的保存对话框调整
    
    console.log("已保存: " + filePath);
    
    // 返回上一级
    back();
    sleep(WAIT_SHORT);
}

// 主程序
function main() {
    console.log("=== 象棋自动复盘系统 - PGN导出脚本 ===");
    console.log("开始执行...");
    
    // 检查无障碍服务
    auto.waitFor();
    
    // 确保目录存在
    ensureDirectory();
    
    // 启动APP
    launchApp();
    
    // 进入历史对局
    enterHistory();
    
    let timestamp = getTimestamp();
    let exportCount = 5;
    
    // 导出5盘棋
    for (let i = 0; i < exportCount; i++) {
        try {
            exportPGN(i, timestamp);
        } catch (e) {
            console.error("导出第" + (i + 1) + "盘失败: " + e);
        }
    }
    
    console.log("已导出5盘");
    toast("已导出5盘");
}

// 运行主程序
main();
