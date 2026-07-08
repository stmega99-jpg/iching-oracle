"""
tarot.py — 最小AI占いMVP（タロット3枚引き）
エンジン不要ゾーンの実証: カードの引き=乱数、意味=学習データ、解釈=LLM。
ANTHROPIC_API_KEY があれば Claude が読む。無ければカードだけ表示。
実行: python tarot.py "相談したいこと"
"""
import os, sys, random, textwrap

MAJOR = [
    ("愚者", "始まり・自由・無垢"), ("魔術師", "創造・意志・技術"),
    ("女教皇", "直感・秘密・内なる声"), ("女帝", "豊穣・母性・実り"),
    ("皇帝", "支配・安定・責任"), ("教皇", "規範・信頼・導き"),
    ("恋人", "選択・調和・愛"), ("戦車", "前進・勝利・意志力"),
    ("力", "内なる強さ・忍耐"), ("隠者", "内省・探求・孤独"),
    ("運命の輪", "転機・循環・好機"), ("正義", "均衡・公正・因果"),
    ("吊るされた男", "停滞・視点転換・献身"), ("死神", "終わりと再生・変容"),
    ("節制", "調整・中庸・融合"), ("悪魔", "束縛・執着・欲望"),
    ("塔", "崩壊・衝撃・解放"), ("星", "希望・可能性・癒し"),
    ("月", "不安・幻想・無意識"), ("太陽", "成功・活力・祝福"),
    ("審判", "復活・決断・覚醒"), ("世界", "完成・統合・達成"),
]
POSITIONS = ["過去", "現在", "未来"]

def draw(n=3):
    picked = random.sample(MAJOR, n)
    return [(pos, name, meaning, random.choice([True, False]))
            for (name, meaning), pos in zip(picked, POSITIONS)]

def format_spread(spread):
    out = []
    for pos, name, meaning, upright in spread:
        ori = "正位置" if upright else "逆位置"
        out.append(f"【{pos}】{name}（{ori}）— {meaning}")
    return "\n".join(out)

def narrate(question, spread):
    try:
        import anthropic
    except ImportError:
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    client = anthropic.Anthropic()
    prompt = (
        "あなたは温かく的確なタロット占い師です。相談者の質問と3枚のスプレッドを踏まえ、"
        "過去→現在→未来の流れで、具体的で前向きな読みを日本語400字程度で語ってください。\n\n"
        f"質問: {question}\n\nスプレッド:\n{format_spread(spread)}"
    )
    msg = client.messages.create(
        model="claude-sonnet-5",  # 語りの質を上げるなら claude-fable-5
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

def main():
    question = " ".join(sys.argv[1:]).strip() or "これからの運勢"
    spread = draw()
    print(f"\n■ 相談: {question}\n")
    print(format_spread(spread) + "\n")
    reading = narrate(question, spread)
    if reading:
        print("―― 占い師の読み ――\n" + textwrap.fill(reading, 38))
    else:
        print("(ANTHROPIC_API_KEY を設定すると Claude が読みます。今はカードのみ)")

if __name__ == "__main__":
    main()
