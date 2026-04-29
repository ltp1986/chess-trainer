const assert = require('assert');
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

describe('前端功能集成测试', function() {
    let dom;
    let document;
    let window;
    
    beforeEach(function() {
        const htmlContent = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf-8');
        dom = new JSDOM(htmlContent, {
            runScripts: 'dangerously',
            resources: 'usable'
        });
        document = dom.window.document;
        window = dom.window;
    });
    
    describe('页面结构测试', function() {
        it('应该包含导航栏', function() {
            const navButtons = document.querySelectorAll('.nav-btn');
            assert.ok(navButtons.length > 0, '导航按钮应该存在');
            
            const buttonTexts = Array.from(navButtons).map(btn => btn.textContent);
            assert.ok(buttonTexts.includes('🏠 首页'), '应该包含首页按钮');
            assert.ok(buttonTexts.includes('📊 能力画像'), '应该包含能力画像按钮');
            assert.ok(buttonTexts.includes('📅 训练计划'), '应该包含训练计划按钮');
            assert.ok(buttonTexts.includes('📝 错题集'), '应该包含错题集按钮');
        });
        
        it('应该包含主内容区域', function() {
            const pageHome = document.getElementById('page-home');
            assert.ok(pageHome, '首页内容区域应该存在');
            
            const pageProfile = document.getElementById('page-profile');
            assert.ok(pageProfile, '能力画像页面应该存在');
            
            const pageExercises = document.getElementById('page-exercises');
            assert.ok(pageExercises, '错题集页面应该存在');
        });
        
        it('应该包含练习模态框', function() {
            const modal = document.getElementById('exercise-modal');
            assert.ok(modal, '练习模态框应该存在');
            
            const practiceBoard = document.getElementById('practice-board');
            assert.ok(practiceBoard, '练习棋盘应该存在');
            
            const hintBtn = document.getElementById('practice-hint');
            assert.ok(hintBtn, '提示按钮应该存在');
            
            const answerBtn = document.getElementById('practice-answer');
            assert.ok(answerBtn, '答案按钮应该存在');
        });
    });
    
    describe('模态框功能测试', function() {
        it('练习模态框应该有正确的结构', function() {
            const modal = document.getElementById('exercise-modal');
            
            const title = modal.querySelector('h3');
            assert.ok(title, '模态框应该有标题');
            assert.ok(title.textContent.includes('错题练习'), '标题应该包含"错题练习"');
            
            const infoPanel = modal.querySelector('.bg-gray-50');
            assert.ok(infoPanel, '信息面板应该存在');
            
            const feedbackArea = document.getElementById('practice-feedback');
            assert.ok(feedbackArea, '反馈区域应该存在');
            
            const hintArea = document.getElementById('practice-hint-text');
            assert.ok(hintArea, '提示文本区域应该存在');
        });
    });
    
    describe('表单测试', function() {
        it('棋手表单应该包含必要字段', function() {
            const form = document.getElementById('player-form');
            assert.ok(form, '棋手表单应该存在');
            
            const nameInput = document.getElementById('player-name');
            assert.ok(nameInput, '姓名输入框应该存在');
            assert.strictEqual(nameInput.required, true, '姓名应该是必填项');
            
            const levelSelect = document.getElementById('player-level');
            assert.ok(levelSelect, '等级选择框应该存在');
            
            const ratingInput = document.getElementById('player-rating');
            assert.ok(ratingInput, '评级输入框应该存在');
            assert.strictEqual(ratingInput.min, '0', '评级最小值应该是0');
            assert.strictEqual(ratingInput.max, '3000', '评级最大值应该是3000');
        });
        
        it('棋局表单应该包含PGN输入选项', function() {
            const form = document.getElementById('game-form');
            assert.ok(form, '棋局表单应该存在');
            
            const fileInput = document.getElementById('game-file');
            assert.ok(fileInput, 'PGN文件输入应该存在');
            assert.strictEqual(fileInput.accept, '.pgn', '应该只接受PGN文件');
            
            const pgnTextarea = document.getElementById('game-pgn');
            assert.ok(pgnTextarea, 'PGN文本输入应该存在');
        });
    });
});

describe('前端API调用测试', function() {
    const api = require('../js/api.js');
    
    describe('API调用封装', function() {
        it('apiCall函数应该存在', function() {
            assert.ok(typeof api.apiCall === 'function', 'apiCall应该是一个函数');
        });
    });
});

describe('工具函数测试', function() {
    const utils = require('../js/utils.js');
    
    describe('工具函数', function() {
        it('showLoading函数应该存在', function() {
            assert.ok(typeof utils.showLoading === 'function', 'showLoading应该是一个函数');
        });
        
        it('formatTime函数应该存在', function() {
            assert.ok(typeof utils.formatTime === 'function', 'formatTime应该是一个函数');
        });
    });
});