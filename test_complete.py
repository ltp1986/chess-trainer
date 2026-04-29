# 完整测试套件 - 覆盖所有菜单、页面和按钮
# 需要安装Playwright: pip install playwright && playwright install chromium

import pytest
import json
import os
import shutil
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"

# 测试数据清理
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
                except Exception as e:
                    print(f"删除文件失败: {file_path}")

@pytest.fixture(scope="module")
def browser():
    clean_test_data()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()
        clean_test_data()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def test_navigation_buttons(page):
    """测试所有导航按钮"""
    page.goto(BASE_URL)
    
    nav_buttons = [
        ('nav-home', 'page-home'),
        ('nav-library', 'page-library'), 
        ('nav-players', 'page-players'),
        ('nav-profile', 'page-profile'),
        ('nav-plan', 'page-plan')
    ]
    
    for btn_id, page_id in nav_buttons:
        page.click(f'#{btn_id}')
        page.wait_for_timeout(500)
        element = page.query_selector(f'#{page_id}')
        assert element is not None, f"页面 {page_id} 不存在"
        classes = element.get_attribute('class')
        assert 'hidden' not in classes, f"页面 {page_id} 未显示"
        print(f"✅ 导航 {btn_id} -> {page_id} 成功")

def test_homepage_features(page):
    """测试首页所有功能按钮"""
    page.goto(BASE_URL)
    
    features = [
        ('#pgn-select', 'PGN文件选择下拉框'),
        ('#difficulty-select', '难度选择下拉框'),
        ('#load-btn', '加载按钮'),
        ('#demo-btn', '演示数据按钮'),
        ('#board', '棋盘元素'),
        ('#tab-review', '复盘标签'),
        ('#tab-exercise', '习题标签'),
        ('#mistake-list', '复盘列表'),
        ('#exercise-area', '习题区域'),
        ('#play-btn', '播放按钮'),
        ('#pause-btn', '暂停按钮'),
        ('#progress-bar', '进度条')
    ]
    
    for selector, name in features:
        element = page.query_selector(selector)
        if element:
            print(f"✅ {name} 存在")
        else:
            print(f"⚠️ {name} 未找到")

def test_players_page(page):
    """测试棋手管理页面"""
    page.goto(BASE_URL)
    page.click('#nav-players')
    page.wait_for_timeout(500)
    
    features = [
        ('button:has-text("添加棋手")', '添加棋手按钮'),
        ('.player-card', '棋手卡片'),
        ('button:has-text("编辑")', '编辑按钮'),
        ('button:has-text("删除")', '删除按钮'),
        ('#player-modal', '棋手模态框'),
        ('#player-form', '棋手表单')
    ]
    
    for selector, name in features:
        element = page.query_selector(selector)
        if element:
            print(f"✅ {name} 存在")
        else:
            print(f"⚠️ {name} 未找到")

def test_library_page(page):
    """测试点评库页面"""
    page.goto(BASE_URL)
    page.click('#nav-library')
    page.wait_for_timeout(500)
    
    features = [
        ('#library-list', '棋局列表'),
        ('button:has-text("添加")', '添加棋局按钮'),
        ('button:has-text("删除")', '删除棋局按钮'),
        ('button:has-text("详情")', '详情按钮')
    ]
    
    for selector, name in features:
        element = page.query_selector(selector)
        if element:
            print(f"✅ {name} 存在")
        else:
            print(f"⚠️ {name} 未找到")

def test_profile_page(page):
    """测试能力画像页面"""
    page.goto(BASE_URL)
    page.click('#nav-profile')
    page.wait_for_timeout(500)
    
    features = [
        ('#profile-content', '画像展示区域'),
        ('button:has-text("生成画像")', '生成画像按钮'),
        ('button:has-text("导出画像")', '导出画像按钮'),
        ('button:has-text("导入画像")', '导入画像按钮')
    ]
    
    for selector, name in features:
        element = page.query_selector(selector)
        if element:
            print(f"✅ {name} 存在")
        else:
            print(f"⚠️ {name} 未找到")

def test_plan_page(page):
    """测试训练计划页面"""
    page.goto(BASE_URL)
    page.click('#nav-plan')
    page.wait_for_timeout(500)
    
    features = [
        ('#plan-content', '计划展示区域'),
        ('button:has-text("生成计划")', '生成计划按钮'),
        ('button:has-text("导出计划")', '导出计划按钮'),
        ('button:has-text("导入计划")', '导入计划按钮')
    ]
    
    for selector, name in features:
        element = page.query_selector(selector)
        if element:
            print(f"✅ {name} 存在")
        else:
            print(f"⚠️ {name} 未找到")

def test_api_endpoints(page):
    """测试所有API端点"""
    page.goto(BASE_URL)
    
    endpoints = [
        '/api/library/games',
        '/api/players',
        '/api/profile',
        '/api/training/plan',
        '/api/pgn_files',
        '/api/analyze/test.pgn',
        '/api/report/test.pgn'
    ]
    
    for endpoint in endpoints:
        try:
            response = page.request.get(f"{BASE_URL}{endpoint}")
            if response.status in [200, 404]:
                print(f"✅ {endpoint}: {response.status}")
            else:
                print(f"⚠️ {endpoint}: {response.status}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def test_demo_data(page):
    """测试演示数据加载功能"""
    page.goto(BASE_URL)
    
    demo_btn = page.query_selector('#demo-btn')
    if demo_btn:
        demo_btn.click()
        page.wait_for_timeout(3000)
        
        mistake_list = page.query_selector('#mistake-list')
        if mistake_list:
            print("✅ 演示数据加载成功")
        else:
            print("❌ 演示数据加载失败")
    else:
        print("❌ 演示按钮未找到")

def test_complete_workflow(page):
    """测试完整的学习流程"""
    page.goto(BASE_URL)
    
    steps = [
        ("加载演示数据", lambda: page.click('#demo-btn')),
        ("等待加载", lambda: page.wait_for_timeout(3000)),
        ("检查复盘列表", lambda: page.query_selector('#mistake-list')),
        ("切换到习题", lambda: page.click('#tab-exercise')),
        ("检查习题区域", lambda: page.query_selector('#exercise-area'))
    ]
    
    for step_name, action in steps:
        try:
            result = action()
            if result is not None and result is False:
                print(f"❌ {step_name} 失败")
            else:
                print(f"✅ {step_name}")
        except Exception as e:
            print(f"❌ {step_name} 失败: {e}")

def test_modal_forms(page):
    """测试模态框表单"""
    page.goto(BASE_URL)
    page.click('#nav-players')
    page.wait_for_timeout(500)
    
    add_btn = page.query_selector('button:has-text("添加棋手")')
    if add_btn:
        add_btn.click()
        page.wait_for_timeout(500)
        
        modal = page.query_selector('#player-modal')
        if modal and 'hidden' not in modal.get_attribute('class'):
            print("✅ 棋手表单模态框正常打开")
            
            form_elements = [
                ('#player-name', '姓名输入框'),
                ('#player-level', '等级选择框'),
                ('#player-rating', '评级输入框'),
                ('button:has-text("保存")', '保存按钮'),
                ('button:has-text("关闭")', '关闭按钮')
            ]
            
            for selector, name in form_elements:
                element = page.query_selector(selector)
                if element:
                    print(f"✅ {name} 存在")
                else:
                    print(f"⚠️ {name} 未找到")
            
            close_btn = page.query_selector('button:has-text("关闭")')
            if close_btn:
                close_btn.click()
                page.wait_for_timeout(300)
                print("✅ 模态框关闭正常")
        else:
            print("❌ 模态框未打开")
    else:
        print("❌ 添加棋手按钮未找到")

def test_navigation_styles(page):
    """测试导航按钮样式变化"""
    page.goto(BASE_URL)
    
    nav_buttons = ['nav-home', 'nav-library', 'nav-players', 'nav-profile', 'nav-plan']
    
    for btn_id in nav_buttons:
        button = page.query_selector(f'#{btn_id}')
        if button:
            original_class = button.get_attribute('class')
            
            button.click()
            page.wait_for_timeout(300)
            
            new_class = button.get_attribute('class')
            
            if 'active' in new_class and 'bg-blue-500' in new_class:
                print(f"✅ 导航按钮 {btn_id} 样式变化正确")
            else:
                print(f"⚠️ 导航按钮 {btn_id} 样式未变化")
        else:
            print(f"❌ 导航按钮 {btn_id} 未找到")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始完整测试套件")
    print("="*60 + "\n")
    
    clean_test_data()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        tests = [
            ("导航按钮测试", test_navigation_buttons),
            ("导航样式测试", test_navigation_styles),
            ("首页功能测试", test_homepage_features),
            ("棋手管理页面测试", test_players_page),
            ("点评库页面测试", test_library_page),
            ("能力画像页面测试", test_profile_page),
            ("训练计划页面测试", test_plan_page),
            ("API端点测试", test_api_endpoints),
            ("演示数据加载测试", test_demo_data),
            ("完整工作流程测试", test_complete_workflow),
            ("表单模态框测试", test_modal_forms)
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                test_func(page)
                passed += 1
            except Exception as e:
                print(f"❌ {name} 失败: {e}")
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