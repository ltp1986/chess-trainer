import json
import os
import sys
from datetime import datetime

def generate_report(test_results_path, output_path):
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
        "failures": []
    }
    
    if os.path.exists(test_results_path):
        with open(test_results_path, 'r') as f:
            data = json.load(f)
            
            if isinstance(data, list):
                for result in data:
                    report["total"] += 1
                    if result.get("status") == "passed":
                        report["passed"] += 1
                    elif result.get("status") == "failed":
                        report["failed"] += 1
                        report["failures"].append({
                            "test_name": result.get("name"),
                            "error": result.get("error", ""),
                            "traceback": result.get("traceback", ""),
                            "file": result.get("file", "")
                        })
                    elif result.get("status") == "error":
                        report["failed"] += 1
                        report["errors"].append({
                            "test_name": result.get("name"),
                            "error": result.get("error", ""),
                            "traceback": result.get("traceback", ""),
                            "file": result.get("file", "")
                        })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"测试报告已生成: {output_path}")
    print(f"总计: {report['total']}, 通过: {report['passed']}, 失败: {report['failed']}")
    
    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_test_report.py <测试结果路径> <输出路径>")
        sys.exit(1)
    
    generate_report(sys.argv[1], sys.argv[2])