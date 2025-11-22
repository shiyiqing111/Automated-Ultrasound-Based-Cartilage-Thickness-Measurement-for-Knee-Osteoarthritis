import pandas as pd
from pathlib import Path

# ======== 配置部分 ========
# 原始标注文件路径（可改成你的 annotation_points_summary.xlsx）
RAW_ANNOT_FILE = Path(r"C:\Users\Charlotte\Desktop\dissertation\US_new\annotation_points_summary2.xlsx")

# 合并后的输出文件
MERGED_OUTPUT = Path(__file__).resolve().parent / "merged_annotation.xlsx"

# =======================================
def _region_order(label: str) -> int:
    """将 Label 列转成解剖区域顺序"""
    label = str(label).lower().strip()
    if "lateral" in label:
        return 0
    elif "femoral" in label or "condyle" in label:
        return 1
    elif "medial" in label:
        return 2
    else:
        return 99  # 其他或无效

def merge_annotation(df: pd.DataFrame) -> pd.DataFrame:
    """把每张图的三段坐标合并为一行"""
    df["region_order"] = df["Label"].apply(_region_order)

    merged_rows = []
    for fname, group in df.groupby("Filename"):
        group = group.sort_values("region_order")
        row = {"Filename": fname}
        for i, (_, seg) in enumerate(group.iterrows(), start=1):
            row[f"x{2*i-1}"], row[f"y{2*i-1}"] = seg["x1"], seg["y1"]
            row[f"x{2*i}"], row[f"y{2*i}"] = seg["x2"], seg["y2"]
            row[f"Pixel_Distance_{i}"] = seg.get("Pixel_Distance", None)
        merged_rows.append(row)
    return pd.DataFrame(merged_rows)


if __name__ == "__main__":
    if not RAW_ANNOT_FILE.exists():
        raise FileNotFoundError(f"未找到原始标注文件: {RAW_ANNOT_FILE}")

    df_raw = pd.read_excel(RAW_ANNOT_FILE)
    print(f"✅ 读取原始标注文件，共 {len(df_raw)} 条记录。")

    df_merged = merge_annotation(df_raw)
    df_merged.to_excel(MERGED_OUTPUT, index=False)
    print(f"✅ 已合并完毕：{len(df_merged)} 张图（每张包含三条线段）")
    print(f"💾 已保存至: {MERGED_OUTPUT}")
