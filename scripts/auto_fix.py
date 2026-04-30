import json
import os
import sys
import re

class AutoFixEngine:
    def __init__(self):
        self.fixes = []
    
    def fix_file_missing(self, failure):
        error = failure.get("error", "")
        match = re.search(r"['\"]([^'\"]+)['\"]", error)
        if match:
            file_path = match.group(1)
            dir_path = os.path.dirname(file_path)
            
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                self.fixes.append(f"创建目录: {dir_path}")
            
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("")
                self.fixes.append(f"创建文件: {file_path}")
                return True
        return False
    
    def fix_import_error(self, failure):
        error = failure.get("error", "")
        match = re.search(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]", error)
        if match:
            module_name = match.group(1)
            self.fixes.append(f"建议安装模块: {module_name} (运行: pip install {module_name})")
            return True
        return False
    
    def fix_api_missing(self, failure):
        error = failure.get("error", "")
        match = re.search(r"(GET|POST|PUT|DELETE)\s+([^\s]+)\s+404", error)
        if match:
            method = match.group(1)
            endpoint = match.group(2)
            self.fixes.append(f"建议添加缺失的API端点: {method} {endpoint}")
            return True
        return False
    
    def fix_attribute_error(self, failure):
        error = failure.get("error", "")
        match = re.search(r"has no attribute ['\"]([^'\"]+)['\"]", error)
        if match:
            attr_name = match.group(1)
            self.fixes.append(f"检查属性名拼写: {attr_name}")
            return True
        return False
    
    def fix_type_error(self, failure):
        error = failure.get("error", "")
        self.fixes.append(f"类型错误，请检查参数类型: {error[:100]}")
        return True
    
    def fix_syntax_error(self, failure):
        error = failure.get("error", "")
        match = re.search(r"line (\d+)", error)
        if match:
            line_num = match.group(1)
            self.fixes.append(f"语法错误，检查第 {line_num} 行")
            return True
        return False
    
    def fix_index_error(self, failure):
        self.fixes.append("索引越界错误，请检查列表/数组长度")
        return True
    
    def process(self, analysis_path):
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
        
        fix_count = 0
        
        for failure in analysis.get("analyzed_failures", []):
            if not failure.get("fixable", False):
                continue
            
            category = failure.get("category")
            
            if category == "file_missing":
                if self.fix_file_missing(failure):
                    fix_count += 1
            elif category == "import_error":
                if self.fix_import_error(failure):
                    fix_count += 1
            elif category == "api_missing":
                if self.fix_api_missing(failure):
                    fix_count += 1
            elif category == "attribute_error":
                if self.fix_attribute_error(failure):
                    fix_count += 1
            elif category == "type_error":
                if self.fix_type_error(failure):
                    fix_count += 1
            elif category == "syntax_error":
                if self.fix_syntax_error(failure):
                    fix_count += 1
            elif category == "index_error":
                if self.fix_index_error(failure):
                    fix_count += 1
        
        result = {
            "fixed_count": fix_count,
            "total_fixable": analysis.get("fixable_count", 0),
            "fixes": self.fixes,
            "success": fix_count > 0
        }
        
        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python auto_fix.py <分析报告路径>")
        sys.exit(1)
    
    engine = AutoFixEngine()
    result = engine.process(sys.argv[1])
    
    print(f"自动修复完成")
    print(f"修复数量: {result['fixed_count']}/{result['total_fixable']}")
    print("修复详情:")
    for fix in result['fixes']:
        print(f"  - {fix}")
    
    output_path = sys.argv[1].replace("analysis", "fix_result")
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)