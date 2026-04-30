import json
import os
import sys
import re

ERROR_PATTERNS = {
    "FileNotFoundError": {
        "pattern": r"FileNotFoundError|No such file or directory",
        "category": "file_missing",
        "fixable": True,
        "description": "文件或目录缺失"
    },
    "ImportError": {
        "pattern": r"ImportError|ModuleNotFoundError",
        "category": "import_error",
        "fixable": True,
        "description": "模块导入失败"
    },
    "404": {
        "pattern": r"404|Not Found",
        "category": "api_missing",
        "fixable": True,
        "description": "API端点不存在"
    },
    "AssertionError": {
        "pattern": r"AssertionError|expect.*toBe|expect.*toEqual|Test.*failed",
        "category": "assertion_failure",
        "fixable": True,
        "description": "断言失败 - 根据测试期望修复代码"
    },
    "TypeError": {
        "pattern": r"TypeError",
        "category": "type_error",
        "fixable": True,
        "description": "类型错误"
    },
    "SyntaxError": {
        "pattern": r"SyntaxError",
        "category": "syntax_error",
        "fixable": True,
        "description": "语法错误"
    },
    "AttributeError": {
        "pattern": r"AttributeError",
        "category": "attribute_error",
        "fixable": True,
        "description": "属性不存在"
    },
    "IndexError": {
        "pattern": r"IndexError",
        "category": "index_error",
        "fixable": True,
        "description": "索引越界"
    }
}

def analyze_failures(report_path, output_path):
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    analysis = {
        "timestamp": report["timestamp"],
        "total_failures": report["failed"],
        "analyzed_failures": [],
        "fixable_count": 0,
        "unfixable_count": 0,
        "categories": {}
    }
    
    all_failures = report.get("failures", []) + report.get("errors", [])
    
    for failure in all_failures:
        analysis_result = {
            "test_name": failure.get("test_name"),
            "file": failure.get("file"),
            "error": failure.get("error", ""),
            "traceback": failure.get("traceback", ""),
            "identified": False,
            "category": None,
            "fixable": False,
            "suggestion": None
        }
        
        for error_type, config in ERROR_PATTERNS.items():
            if re.search(config["pattern"], failure.get("error", "") + failure.get("traceback", ""), re.IGNORECASE):
                analysis_result["identified"] = True
                analysis_result["category"] = config["category"]
                analysis_result["fixable"] = config["fixable"]
                analysis_result["suggestion"] = config["description"]
                
                if config["category"] not in analysis["categories"]:
                    analysis["categories"][config["category"]] = 0
                analysis["categories"][config["category"]] += 1
                
                if config["fixable"]:
                    analysis["fixable_count"] += 1
                else:
                    analysis["unfixable_count"] += 1
                break
        
        analysis["analyzed_failures"].append(analysis_result)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"分析报告已生成: {output_path}")
    print(f"可自动修复: {analysis['fixable_count']}, 需人工处理: {analysis['unfixable_count']}")
    
    return analysis

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python analyze_failures.py <测试报告路径> <输出路径>")
        sys.exit(1)
    
    analyze_failures(sys.argv[1], sys.argv[2])