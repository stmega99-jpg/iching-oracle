"""
iching.py — 易オラクル / I Ching oracle
決定論エンジンが卦を計算し、LLMは解釈だけを担う。
判じ層は strict private by default：相談は手元から一切出ない（Ollama）。
クラウドは明示 opt-in の時だけ。エンジン単体はゼロ依存・キー不要で動く。

  python iching.py "相談事"                      # 既定＝ローカルのみ。外に出さない
  python iching.py "相談事" --anthropic            # クラウド(Anthropic)を明示使用
  python iching.py "相談事" --allow-cloud-fallback  # ローカル→失敗時のみクラウドへ
  python iching.py "相談事" --model qwen2.5        # モデル指定
"""
import sys, os, json, random, urllib.request
from iching_data import HEX_BY_BINARY

# 3ビット(下→上, 1=陽) -> (名, 記号, 象) ※検証済み
TRIGRAMS = {
    (1, 1, 1): ("乾", "☰", "天"), (1, 1, 0): ("兌", "☱", "沢"),
    (1, 0, 1): ("離", "☲", "火"), (1, 0, 0): ("震", "☳", "雷"),
    (0, 1, 1): ("巽", "☴", "風"), (0, 1, 0): ("坎", "☵", "水"),
    (0, 0, 1): ("艮", "☶", "山"), (0, 0, 0): ("坤", "☷", "地"),
}

def toss_line():
    s = sum(random.choice([2, 3]) for _ in range(3))  # 三枚コイン
    return (s % 2 == 1), (s in (6, 9))                # (陽か, 変爻か)

def cast():
    return [toss_line() for _ in range(6)]  # index0=初爻(下)

def trigrams_of(lines):
    lower = TRIGRAMS[tuple(1 if y else 0 for y, _ in lines[0:3])]
    upper = TRIGRAMS[tuple(1 if y else 0 for y, _ in lines[3:6])]
    return upper, lower

def hexagram_of(lines):
    binary = "".join("1" if y else "0" for y, _ in lines)  # 下→上
    return HEX_BY_BINARY.get(binary)  # (番号, 名, 上, 下) or None

def changed(lines):
    return [((not y) if c else y, False) for y, c in lines]

def show(lines, label):
    up, lo = trigrams_of(lines)
    h = hexagram_of(lines)
    name = f"第{h[0]}卦 {h[1]}" if h else "?"
    print(f"{label}: {name}")
    print(f"      上[{up[0]}/{up[2]} {up[1]}] ・ 下[{lo[0]}/{lo[2]} {lo[1]}]")

# ---- 判じ層（LLM）: 卦は改変禁止＝条文、解釈は大胆＝判決 ----
def _build_prompt(question, lines, moving):
    ph = hexagram_of(lines)
    body = f"本卦 第{ph[0]}卦 {ph[1]}"
    if moving:
        rh = hexagram_of(changed(lines))
        body += f"／変爻 {'・'.join(f'第{i}爻' for i in moving)}／之卦 第{rh[0]}卦 {rh[1]}"
    return (
        "あなたは易の占い師です。次の卦は決定論エンジンが出した正確な結果で、改変禁止。\n"
        "規律：(1)この卦と爻に紐づけて、相談者のために大胆に判じる。"
        "(2)厳しい面は正直に述べてよいが、之卦（向かう先）に沿って、"
        "手触りのある一歩で閉じる——凶で終わらせない。日本語400字程度。\n\n"
        f"相談：{question}\n卦：{body}"
    )

def _judge_ollama(prompt, model, host="http://localhost:11434"):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(host + "/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:  # 相談は手元から出ない
        return json.loads(r.read().decode())["response"].strip()

def _judge_anthropic(prompt, model="claude-sonnet-5"):
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=model, max_tokens=800, messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text

def judge(question, lines, moving, provider="local", model=None):
    """provider: 'local'(既定・厳格) / 'anthropic'(明示クラウド) / 'auto'(local→cloudフォールバック)"""
    prompt = _build_prompt(question, lines, moving)
    # ローカル経路。'local' はここで失敗しても絶対にクラウドへ行かない。
    if provider in ("local", "auto"):
        try:
            return _judge_ollama(prompt, model or os.environ.get("ICHING_MODEL", "llama3.1"))
        except Exception:
            if provider == "local":
                return None  # strict：相談を外に漏らさず終了
    # クラウド経路。明示 opt-in（anthropic）か、明示フォールバック許可（auto）の時だけ。
    if provider in ("anthropic", "auto") and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _judge_anthropic(prompt, model or "claude-sonnet-5")
        except Exception:
            return None
    return None

def reading(question, provider="local", model=None):
    lines = cast()
    moving = [i + 1 for i, (_, c) in enumerate(lines) if c]
    print(f"\n■ 相談: {question}\n")
    show(lines, "本卦")
    if moving:
        print(f"変爻:  {'・'.join(f'第{i}爻' for i in moving)}")
        show(changed(lines), "之卦")
    else:
        print("変爻:  なし（本卦のまま）")
    verdict = judge(question, lines, moving, provider, model)
    if verdict:
        print("\n―― 判じ ――\n" + verdict)
    else:
        print("\n(判じ未生成。既定はローカルのみ＝相談は外に出ません。"
              "`ollama serve` で判じが出る。クラウドを使うなら明示的に "
              "--anthropic か --allow-cloud-fallback。上の卦はエンジンで確定済み。)")

if __name__ == "__main__":
    args = sys.argv[1:]
    provider = "local"  # strict private by default：クラウドには絶対触れない
    if "--local" in args:
        args.remove("--local"); provider = "local"
    if "--anthropic" in args:
        args.remove("--anthropic"); provider = "anthropic"
    if "--allow-cloud-fallback" in args or "--auto" in args:
        for f in ("--allow-cloud-fallback", "--auto"):
            if f in args:
                args.remove(f)
        provider = "auto"
    model = None
    if "--model" in args:
        i = args.index("--model")
        if i + 1 < len(args):
            model = args[i + 1]; del args[i:i + 2]
        else:
            args.remove("--model")
    reading(" ".join(args).strip() or "これからの流れ", provider, model)
