function initNavigation() {
    console.log('🔧 初始化导航...');
    try {
        const navButtons = document.querySelectorAll('.nav-btn');
        const pages = document.querySelectorAll('.page-content');
        
        console.log(`找到 ${navButtons.length} 个导航按钮`);
        console.log(`找到 ${pages.length} 个页面容器`);

        if (navButtons.length === 0) {
            console.error('❌ 未找到导航按钮!');
            return;
        }

        pages.forEach(page => {
            if (page) page.classList.add('hidden');
        });
        const homePage = document.getElementById('page-home');
        if (homePage) {
            homePage.classList.remove('hidden');
            console.log('✅ 首页已显示');
        }

        navButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                try {
                    const btnId = this.id;
                    const pageId = btnId.replace('nav-', 'page-');
                    console.log(`🔄 导航切换: ${btnId} -> ${pageId}`);

                    navButtons.forEach(b => {
                        b.classList.remove('active', 'bg-blue-500', 'text-white');
                        b.classList.add('bg-gray-200', 'text-gray-700');
                    });
                    this.classList.add('active', 'bg-blue-500', 'text-white');

                    pages.forEach(page => {
                        if (page) page.classList.add('hidden');
                    });
                    const targetPage = document.getElementById(pageId);
                    if (targetPage) {
                        targetPage.classList.remove('hidden');
                        console.log(`✅ 页面 ${pageId} 已显示`);
                    } else {
                        console.error(`❌ 未找到页面: ${pageId}`);
                    }

                    const fileSelection = document.getElementById('file-selection');
                    if (fileSelection) {
                        fileSelection.classList.toggle('hidden', pageId !== 'page-home');
                    }

                    switch(pageId) {
                        case 'page-library': loadLibraryPage(); break;
                        case 'page-players': loadPlayersPage(); break;
                        case 'page-profile': loadProfilePage(); break;
                        case 'page-plan': loadPlanPage(); break;
                        case 'page-exercises': loadExercisesPage(); break;
                    }
                } catch (error) {
                    console.error('❌ 导航切换失败:', error);
                }
            });
        });

        console.log('✅ 导航初始化完成');
    } catch (error) {
        console.error('❌ 导航初始化失败:', error);
    }
}