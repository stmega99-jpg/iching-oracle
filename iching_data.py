"""
iching_data.py — 検証済み64卦テーブル（King Wen順）
トリガム名で取得 → 検証済み8卦ビット表で二進に変換 → 門番で完全順列を保証。
記憶で二進を埋めない。構造は門番が保証する。
"""
from collections import Counter

# 3ビット(下→上, 1=陽) ※検証済み
TRIGRAM_BITS = {
    "Heaven": "111", "Lake": "110", "Fire": "101", "Thunder": "100",
    "Wind": "011", "Water": "010", "Mountain": "001", "Earth": "000",
}

# (King Wen番号, 名, 上卦, 下卦)  ※Wikipedia List of hexagrams より取得
KING_WEN = [
    (1, "Qian/Force", "Heaven", "Heaven"), (2, "Kun/Field", "Earth", "Earth"),
    (3, "Zhun/Sprouting", "Water", "Thunder"), (4, "Meng/Enveloping", "Mountain", "Water"),
    (5, "Xu/Attending", "Water", "Heaven"), (6, "Song/Conflict", "Heaven", "Water"),
    (7, "Shi/Leading", "Earth", "Water"), (8, "Bi/Grouping", "Water", "Earth"),
    (9, "Xiaoxu/Small Accumulating", "Wind", "Heaven"), (10, "Lu/Treading", "Heaven", "Lake"),
    (11, "Tai/Pervading", "Earth", "Heaven"), (12, "Pi/Obstruction", "Heaven", "Earth"),
    (13, "Tongren/Concording People", "Heaven", "Fire"), (14, "Dayou/Great Possessing", "Fire", "Heaven"),
    (15, "Qian/Humbling", "Earth", "Mountain"), (16, "Yu/Providing-For", "Thunder", "Earth"),
    (17, "Sui/Following", "Lake", "Thunder"), (18, "Gu/Correcting", "Mountain", "Wind"),
    (19, "Lin/Nearing", "Earth", "Lake"), (20, "Guan/Viewing", "Wind", "Earth"),
    (21, "Shike/Gnawing Bite", "Fire", "Thunder"), (22, "Bi/Adorning", "Mountain", "Fire"),
    (23, "Bo/Stripping", "Mountain", "Earth"), (24, "Fu/Returning", "Earth", "Thunder"),
    (25, "Wuwang/Without Embroiling", "Heaven", "Thunder"), (26, "Daxu/Great Accumulating", "Mountain", "Heaven"),
    (27, "Yi/Swallowing", "Mountain", "Thunder"), (28, "Daguo/Great Exceeding", "Lake", "Wind"),
    (29, "Kan/Gorge", "Water", "Water"), (30, "Li/Radiance", "Fire", "Fire"),
    (31, "Xian/Conjoining", "Lake", "Mountain"), (32, "Heng/Persevering", "Thunder", "Wind"),
    (33, "Dun/Retiring", "Heaven", "Mountain"), (34, "Dazhuang/Great Invigorating", "Thunder", "Heaven"),
    (35, "Jin/Prospering", "Fire", "Earth"), (36, "Mingyi/Darkening of the Light", "Earth", "Fire"),
    (37, "Jiaren/Dwelling People", "Wind", "Fire"), (38, "Kui/Polarising", "Fire", "Lake"),
    (39, "Jian/Limping", "Water", "Mountain"), (40, "Jie/Taking-Apart", "Thunder", "Water"),
    (41, "Sun/Diminishing", "Mountain", "Lake"), (42, "Yi/Augmenting", "Wind", "Thunder"),
    (43, "Guai/Displacement", "Lake", "Heaven"), (44, "Gou/Coupling", "Heaven", "Wind"),
    (45, "Cui/Clustering", "Lake", "Earth"), (46, "Sheng/Ascending", "Earth", "Wind"),
    (47, "Kun/Confining", "Lake", "Water"), (48, "Jing/Welling", "Water", "Wind"),
    (49, "Ge/Skinning", "Lake", "Fire"), (50, "Ding/Holding", "Fire", "Wind"),
    (51, "Zhen/Shake", "Thunder", "Thunder"), (52, "Gen/Bound", "Mountain", "Mountain"),
    (53, "Jian/Infiltrating", "Wind", "Mountain"), (54, "Guimei/Converting the Maiden", "Thunder", "Lake"),
    (55, "Feng/Abounding", "Thunder", "Fire"), (56, "Lu/Sojourning", "Fire", "Mountain"),
    (57, "Xun/Ground", "Wind", "Wind"), (58, "Dui/Open", "Lake", "Lake"),
    (59, "Huan/Dispersing", "Wind", "Water"), (60, "Jie/Articulating", "Water", "Lake"),
    (61, "Zhongfu/Center Returning", "Wind", "Lake"), (62, "Xiaoguo/Small Exceeding", "Thunder", "Mountain"),
    (63, "Jiji/Already Fording", "Water", "Fire"), (64, "Weiji/Not Yet Fording", "Fire", "Water"),
]

def _binary(upper, lower):
    # 下→上: 下卦(初〜三爻) + 上卦(四〜上爻)
    return TRIGRAM_BITS[lower] + TRIGRAM_BITS[upper]

# {6bit二進(下→上): (番号, 名, 上, 下)}
HEX_BY_BINARY = {_binary(u, l): (n, name, u, l) for (n, name, u, l) in KING_WEN}

def validate():
    bins = [_binary(u, l) for (_, _, u, l) in KING_WEN]
    dups = sorted(b for b, c in Counter(bins).items() if c > 1)
    missing = sorted({format(i, "06b") for i in range(64)} - set(bins))
    return dups, missing

if __name__ == "__main__":
    dups, missing = validate()
    ok = not dups and not missing
    print(f"エントリ数: {len(KING_WEN)}  ユニーク二進: {len(set(_binary(u,l) for _,_,u,l in KING_WEN))}")
    print(f"重複: {len(dups)}  欠落: {len(missing)}")
    print("門番: " + ("合格 ✓ 完全順列（全64卦がユニークに揃った）" if ok else f"失敗 ✗ dups={dups} missing={missing}"))
    # アンカー照合（自信のある既知値）
    anchors = {"111111": "Qian(1)", "000000": "Kun(2)", "111000": "Tai(11)",
               "000111": "Pi(12)", "101010": "Jiji(63)", "010101": "Weiji(64)"}
    print("\nアンカー照合:")
    for b, expect in anchors.items():
        got = HEX_BY_BINARY.get(b)
        mark = "✓" if got and str(got[0]) in expect else "?"
        print(f"  {b} -> {got[0]}:{got[1].split('/')[0]} (期待 {expect}) {mark}")
