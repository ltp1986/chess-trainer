import os
import re

OUT = r"D:\Chess_Output"

def check_svg_for_arrows(svg_path):
    """检查SVG文件中是否包含箭头元素"""
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    # chess.svg 生成的箭头通常是 <line> 或 <path> 元素
    # 红色箭头颜色 #e74c3c
    # 绿色箭头颜色 #27ae60

    has_red = "#e74c3c" in content
    has_green = "#27ae60" in content
    has_line = "<line" in content or "<path" in content

    # 检查是否有 marker（箭头头部）
    has_marker = "marker-" in content or "markerId" in content

    return {
        "file": os.path.basename(svg_path),
        "has_red": has_red,
        "has_green": has_green,
        "has_line": has_line,
        "has_marker": has_marker,
        "content_length": len(content)
    }

def main():
    images_dir = os.path.join(OUT, "images")

    if not os.path.exists(images_dir):
        print("❌ images 目录不存在")
        return

    svg_files = [f for f in os.listdir(images_dir) if f.endswith(".svg")]

    if not svg_files:
        print("❌ 没有找到 SVG 文件")
        return

    print(f"找到 {len(svg_files)} 个 SVG 文件\n")
    print("=" * 60)

    for svg_file in sorted(svg_files):
        path = os.path.join(images_dir, svg_file)
        result = check_svg_for_arrows(path)

        status = []
        if result["has_red"]:
            status.append("🔴红箭头")
        if result["has_green"]:
            status.append("🟢绿箭头")
        if result["has_line"]:
            status.append("线条")
        if result["has_marker"]:
            status.append("箭头头部")

        if status:
            print(f"✅ {result['file']}: {', '.join(status)}")
        else:
            print(f"❌ {result['file']}: 无箭头")
            # 打印部分内容用于调试
            with open(path, "r") as f:
                content = f.read()
            print(f"   内容预览: {content[:200]}...")

    print("=" * 60)

    # 统计
    total = len(svg_files)
    with_arrows = sum(1 for f in svg_files
                      if check_svg_for_arrows(os.path.join(images_dir, f))["has_red"]
                      or check_svg_for_arrows(os.path.join(images_dir, f))["has_green"])

    print(f"\n总结: {with_arrows}/{total} 个文件包含箭头")

if __name__ == "__main__":
    main()
