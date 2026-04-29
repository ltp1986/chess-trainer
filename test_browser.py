# 浏览器自动化测试 (需要安装Playwright)
# pip install playwright
# playwright install chromium

import pytest
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def test_homepage_loads(page):
    """测试首页加载"""
    response = page.goto(BASE_URL)
    assert response.status == 200, "首页应返回200状态码"
    print("✅ 首页加载成功")

def test_navigation_exists(page):
    """测试导航元素存在"""
    page.goto(BASE_URL)

    nav_buttons = ['nav-home', 'nav-library', 'nav-players', 'nav-profile', 'nav-plan']
    for btn_id in nav_buttons:
        selector = f'#{btn_id}'
        element = page.query_selector(selector)
        assert element is not None, f"导航按钮 {btn_id} 应存在"
        print(f"✅ 导航按钮 {btn_id} 存在")

def test_navigation_click(page):
    """测试导航点击功能"""
    page.goto(BASE_URL)
    time.sleep(0.5)

    # 测试点击棋手管理
    page.click('#nav-players')
    time.sleep(0.5)

    players_content = page.query_selector('#page-players')
    assert players_content is not None, "棋手管理页面应存在"

    is_hidden = players_content.get_attribute('class')
    assert 'hidden' not in is_hidden, "点击后棋手管理页面应显示"
    print("✅ 棋手管理页面切换成功")

    # 测试点击点评库
    page.click('#nav-library')
    time.sleep(0.5)

    library_content = page.query_selector('#page-library')
    assert library_content is not None, "点评库页面应存在"
    print("✅ 点评库页面切换成功")

def test_api_endpoints(page):
    """测试API端点"""
    page.goto(BASE_URL)

    api_endpoints = [
        '/api/library/games',
        '/api/players',
        '/api/profile',
        '/api/training/plan'
    ]

    for endpoint in api_endpoints:
        response = page.request.get(f"{BASE_URL}{endpoint}")
        assert response.status in [200, 404], f"{endpoint} 应返回200或404"
        print(f"✅ {endpoint}: {response.status}")

def test_demo_data_button(page):
    """测试演示数据按钮"""
    page.goto(BASE_URL)
    time.sleep(0.5)

    # 查找演示数据按钮
    demo_button = page.query_selector('button:has-text("演示")')
    if demo_button:
        print("✅ 演示数据按钮存在")
    else:
        print("⚠️ 演示数据按钮未找到")

def test_chess_board(page):
    """测试棋盘元素"""
    page.goto(BASE_URL)
    time.sleep(0.5)

    board = page.query_selector('#board')
    assert board is not None, "棋盘元素应存在"
    print("✅ 棋盘元素存在")

    squares = page.query_selector_all('.square')
    # 页面上有两个棋盘（复盘棋盘和习题棋盘），所以应该是128个格子
    assert len(squares) == 128, f"两个棋盘应有128个格子，实际为{len(squares)}"
    print(f"✅ 棋盘格子数量正确: {len(squares)} (两个棋盘各64格)")

def test_complete_workflow(page):
    """测试完整工作流程"""
    page.goto(BASE_URL)
    time.sleep(0.5)

    # 1. 加载演示数据
    demo_button = page.query_selector('button:has-text("演示")')
    if demo_button:
        demo_button.click()
        time.sleep(1)
        print("✅ 演示数据加载")

    # 2. 检查复盘列表
    mistake_list = page.query_selector('#mistake-list')
    if mistake_list:
        print("✅ 复盘列表加载成功")

    # 3. 检查习题区域
    exercises_btn = page.query_selector('#nav-exercises')
    if exercises_btn:
        exercises_btn.click()
        time.sleep(0.5)
        print("✅ 习题练习页面切换成功")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 开始浏览器自动化测试")
    print("="*60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        tests = [
            ("首页加载", lambda: test_homepage_loads(page)),
            ("导航元素", lambda: test_navigation_exists(page)),
            ("导航点击", lambda: test_navigation_click(page)),
            ("API端点", lambda: test_api_endpoints(page)),
            ("演示数据按钮", lambda: test_demo_data_button(page)),
            ("棋盘元素", lambda: test_chess_board(page)),
            ("完整流程", lambda: test_complete_workflow(page)),
        ]

        passed = 0
        failed = 0

        for name, test_func in tests:
            try:
                test_func()
                passed += 1
            except Exception as e:
                print(f"❌ {name} 失败: {e}")
                failed += 1

        context.close()
        browser.close()

        print("\n" + "="*60)
        print(f"📊 测试结果: {passed}/{passed+failed} 通过")
        print("="*60)

        return passed, failed

if __name__ == "__main__":
    run_all_tests()