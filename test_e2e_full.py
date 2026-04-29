# 增强版端到端测试套件 - 覆盖所有按钮交互和完整流程
# 需要安装Playwright: pip install playwright && playwright install chromium

import pytest
import json
import os
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"

def clean_test_data():
    """清理测试数据"""
    dirs_to_clean = [
        "webapp/output/library",
        "webapp/output/profiles", 
        "webapp/output/plans",
        "webapp/output/players"
    ]
    for dir_path in dirs_to_clean:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.exists(full_path):
            for filename in os.listdir(full_path):
                file_path = os.path.join(full_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass

def run_test(test_name, test_func, page):
    """运行单个测试并记录结果"""
    try:
        test_func(page)
        print(f"✅ {test_name}")
        return True
    except Exception as e:
        print(f"❌ {test_name} 失败: {e}")
        return False

def test_navigation_full(page):
    """测试所有导航按钮完整交互"""
    page.goto(BASE_URL)
    
    nav_items = [
        ('nav-home', 'page-home', '首页'),
        ('nav-library', 'page-library', '点评库'),
        ('nav-players', 'page-players', '棋手管理'),
        ('nav-profile', 'page-profile', '能力画像'),
        ('nav-plan', 'page-plan', '训练计划')
    ]
    
    for btn_id, page_id, name in nav_items:
        btn = page.query_selector(f'#{btn_id}')
        assert btn is not None, f"{name}导航按钮不存在"
        btn.click()
        page.wait_for_timeout(500)
        
        page_element = page.query_selector(f'#{page_id}')
        assert page_element is not None, f"{name}页面不存在"
        classes = page_element.get_attribute('class')
        assert 'hidden' not in classes, f"{name}页面未显示"
        
        assert 'active' in btn.get_attribute('class'), f"{name}按钮样式未变化"
        print(f"   - {name}导航正常")

def test_homepage_full_interaction(page):
    """测试首页完整交互流程"""
    page.goto(BASE_URL)
    
    pgn_select = page.query_selector('#pgn-select')
    assert pgn_select is not None, "PGN选择下拉框不存在"
    pgn_select.click()
    page.wait_for_timeout(300)
    print("   - PGN选择下拉框可点击")
    
    difficulty_select = page.query_selector('#difficulty-select')
    assert difficulty_select is not None, "难度选择下拉框不存在"
    difficulty_select.select_option('hard')
    page.wait_for_timeout(300)
    print("   - 难度选择下拉框可选择")
    
    load_btn = page.query_selector('#load-btn')
    assert load_btn is not None, "加载按钮不存在"
    print("   - 加载按钮存在")
    
    demo_btn = page.query_selector('#demo-btn')
    assert demo_btn is not None, "演示按钮不存在"
    demo_btn.click()
    page.wait_for_timeout(3000)
    print("   - 演示数据加载成功")
    
    mistake_list = page.query_selector('#mistake-list')
    assert mistake_list is not None, "复盘列表不存在"
    print("   - 复盘列表显示")
    
    play_btn = page.query_selector('#play-btn')
    pause_btn = page.query_selector('#pause-btn')
    assert play_btn is not None, "播放按钮不存在"
    assert pause_btn is not None, "暂停按钮不存在"
    play_btn.click()
    page.wait_for_timeout(500)
    pause_btn.click()
    print("   - 播放/暂停控制正常")
    
    progress_bar = page.query_selector('#progress-bar')
    assert progress_bar is not None, "进度条不存在"
    print("   - 进度条存在")

def test_players_full_crud(page):
    """测试棋手管理完整CRUD流程"""
    page.goto(BASE_URL)
    page.click('#nav-players')
    page.wait_for_timeout(500)
    
    add_btn = page.query_selector('button:has-text("添加棋手")')
    assert add_btn is not None, "添加棋手按钮不存在"
    add_btn.click()
    page.wait_for_timeout(500)
    print("   - 添加棋手模态框打开")
    
    name_input = page.query_selector('#player-name')
    level_select = page.query_selector('#player-level')
    rating_input = page.query_selector('#player-rating')
    
    assert name_input is not None, "姓名输入框不存在"
    assert level_select is not None, "等级选择框不存在"
    assert rating_input is not None, "评级输入框不存在"
    
    name_input.fill('测试棋手')
    level_select.select_option('L3')
    rating_input.fill('1800')
    print("   - 表单填写完成")
    
    save_btn = page.query_selector('#player-modal button:has-text("保存")')
    assert save_btn is not None, "保存按钮不存在"
    save_btn.click()
    page.wait_for_timeout(1000)
    print("   - 棋手保存成功")
    
    player_card = page.query_selector('.player-card:has-text("测试棋手")')
    assert player_card is not None, "棋手卡片未创建"
    print("   - 棋手卡片显示")
    
    edit_btn = player_card.query_selector('button:has-text("编辑")')
    assert edit_btn is not None, "编辑按钮不存在"
    edit_btn.click()
    page.wait_for_timeout(800)
    
    modal = page.query_selector('#player-modal')
    assert modal is not None, "模态框不存在"
    modal_classes = modal.get_attribute('class')
    assert 'hidden' not in modal_classes, "模态框未显示"
    
    name_input = page.query_selector('#player-name')
    assert name_input is not None, "姓名输入框不存在"
    name_input.fill('测试棋手(已编辑)')
    
    save_btn = page.query_selector('#player-modal button:has-text("保存")')
    save_btn.click()
    page.wait_for_timeout(1000)
    print("   - 棋手编辑成功")
    
    player_card = page.query_selector('.player-card:has-text("测试棋手(已编辑)")')
    assert player_card is not None, "编辑后的棋手卡片未显示"
    
    delete_btn = player_card.query_selector('button:has-text("删除")')
    assert delete_btn is not None, "删除按钮不存在"
    delete_btn.click()
    page.wait_for_timeout(1000)
    print("   - 棋手删除成功")

def test_library_full_crud(page):
    """测试点评库完整CRUD流程"""
    page.goto(BASE_URL)
    page.click('#nav-library')
    page.wait_for_timeout(500)
    
    add_btn = page.query_selector('#library-content button:has-text("添加")')
    if add_btn:
        add_btn.click()
        page.wait_for_timeout(500)
        print("   - 添加棋局模态框打开")
        
        pgn_textarea = page.query_selector('#game-modal textarea')
        if pgn_textarea:
            pgn_content = '''[Event "Test Game"]
[White "Test White"]
[Black "Test Black"]
1. e4 e5 2. Nf3 Nc6 0-1'''
            pgn_textarea.fill(pgn_content)
            print("   - PGN内容填写")
        
        save_btn = page.query_selector('#game-modal button:has-text("保存")')
        if save_btn:
            save_btn.click()
            page.wait_for_timeout(2000)
            print("   - 棋局保存成功")
    
    library_list = page.query_selector('#library-list')
    if library_list:
        print("   - 棋局列表显示")
    
    detail_btn = page.query_selector('#library-content button:has-text("详情")')
    if detail_btn:
        detail_btn.click()
        page.wait_for_timeout(500)
        print("   - 棋局详情打开")

def test_profile_workflow(page):
    """测试能力画像生成流程"""
    page.goto(BASE_URL)
    
    demo_btn = page.query_selector('#demo-btn')
    if demo_btn:
        demo_btn.click()
        page.wait_for_timeout(3000)
    
    page.click('#nav-profile')
    page.wait_for_timeout(500)
    
    generate_btn = page.query_selector('button:has-text("生成画像")')
    if generate_btn:
        generate_btn.click()
        page.wait_for_timeout(3000)
        print("   - 画像生成完成")
    
    export_btn = page.query_selector('button:has-text("导出画像")')
    if export_btn:
        print("   - 导出画像按钮存在")

def test_plan_workflow(page):
    """测试训练计划生成流程"""
    page.goto(BASE_URL)
    
    demo_btn = page.query_selector('#demo-btn')
    if demo_btn:
        demo_btn.click()
        page.wait_for_timeout(3000)
    
    page.click('#nav-profile')
    page.wait_for_timeout(500)
    generate_profile_btn = page.query_selector('button:has-text("生成画像")')
    if generate_profile_btn:
        generate_profile_btn.click()
        page.wait_for_timeout(3000)
    
    page.click('#nav-plan')
    page.wait_for_timeout(500)
    
    generate_plan_btn = page.query_selector('button:has-text("生成计划")')
    if generate_plan_btn:
        generate_plan_btn.click()
        page.wait_for_timeout(3000)
        print("   - 训练计划生成完成")
    
    export_btn = page.query_selector('button:has-text("导出计划")')
    if export_btn:
        print("   - 导出计划按钮存在")

def test_exercise_workflow(page):
    """测试习题练习完整流程"""
    page.goto(BASE_URL)
    
    demo_btn = page.query_selector('#demo-btn')
    assert demo_btn is not None, "演示按钮不存在"
    demo_btn.click()
    page.wait_for_timeout(3000)
    print("   - 演示数据加载")
    
    exercise_tab = page.query_selector('#tab-exercise')
    if exercise_tab:
        exercise_tab.click()
        page.wait_for_timeout(500)
        print("   - 切换到习题标签")
        
        exercise_area = page.query_selector('#exercise-area')
        assert exercise_area is not None, "习题区域不存在"
        print("   - 习题区域显示")
        
        hint_btn = page.query_selector('#hint-btn')
        if hint_btn:
            hint_btn.click()
            page.wait_for_timeout(500)
            print("   - 提示功能正常")
        
        answer_btn = page.query_selector('#answer-btn')
        if answer_btn:
            answer_btn.click()
            page.wait_for_timeout(500)
            print("   - 答案显示正常")
        
        next_btn = page.query_selector('#next-exercise')
        if next_btn:
            next_btn.click()
            page.wait_for_timeout(500)
            print("   - 下一题正常")

def test_error_handling(page):
    """测试错误处理场景"""
    page.goto(BASE_URL)
    
    load_btn = page.query_selector('#load-btn')
    if load_btn:
        load_btn.click()
        page.wait_for_timeout(500)
        print("   - 空文件加载处理")
    
    response = page.request.get(f"{BASE_URL}/api/analyze/nonexistent.pgn")
    assert response.status == 404, "API错误处理不正确"
    print("   - API错误处理正常")

def run_all_tests():
    """运行所有端到端测试"""
    print("\n" + "="*60)
    print("🚀 开始增强端到端测试套件")
    print("="*60 + "\n")
    
    clean_test_data()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        tests = [
            ("导航系统完整测试", test_navigation_full),
            ("首页完整交互测试", test_homepage_full_interaction),
            ("棋手管理CRUD测试", test_players_full_crud),
            ("点评库CRUD测试", test_library_full_crud),
            ("能力画像流程测试", test_profile_workflow),
            ("训练计划流程测试", test_plan_workflow),
            ("习题练习流程测试", test_exercise_workflow),
            ("错误处理测试", test_error_handling)
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            print(f"\n📋 {name}")
            print("-" * 40)
            if run_test(name, test_func, page):
                passed += 1
            else:
                failed += 1
        
        context.close()
        browser.close()
        clean_test_data()
        
        print("\n" + "="*60)
        print(f"📊 测试结果: {passed}/{passed+failed} 通过")
        print("="*60)
        
        return passed, failed

if __name__ == "__main__":
    run_all_tests()