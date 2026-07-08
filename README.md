# 易 · I Ching Oracle

**A local-first I Ching oracle: verified hexagrams, private questions, poetic LLM readings.**

Most AI fortune-tellers let the model hallucinate everything — including the hexagram itself — and ship your question off to someone else's server. This one does neither.

- **The structure is computed, never hallucinated.** Which hexagram you drew, which lines are changing, which hexagram it transforms into: all derived by a deterministic coin-oracle and looked up in a **validated** 64-hexagram table.
- **The interpretation is written by an LLM — and by default, a _local_ one.** Your question never leaves your machine unless you explicitly opt into a cloud model.

Think of it like law: **quote the statute exactly, judge the case freely.**

## Two layers, opposite rules

| layer | rule |
|-------|------|
| hexagram / changing lines / resulting hexagram | **deterministic** — computed, then checked against a validated 64-pattern table |
| the reading (判じ) | **free** — an LLM interprets, bold and personal, but always anchored to the real hexagram above |

### The gatekeeper (門番)

Correctness is a checked invariant, not a hope. Any hexagram table must pass `validate()` — all 64 line-patterns present exactly once, a complete permutation. Corrupt or scraped data (duplicates, gaps) is rejected *before* it can reach a reading.

## How a reading works

```
coin cast (6 lines)
   → primary hexagram      (named, from the validated table)
   → changing lines
   → resulting hexagram     (where the situation is heading)
   → 判じ / the reading      (LLM, anchored to the above)
```

One rule for the reading: it may name the hard part honestly, but it **resolves toward the resulting hexagram and never ends in doom** — because the I Ching is a book of *change*, and no hexagram is a terminal state.

## Quick start

The engine (cast, hexagram, changing lines, validation) runs with **no dependencies and no API key**:

```bash
python iching.py "the question on your mind"
```

For the written reading, the default is **strict local — your question never touches the network:**

```bash
# default: local only. Nothing is ever sent to a cloud, even if an API key is set.
ollama serve                                    # in another shell:
python iching.py "should I take the new path?"  # same as --local; add --model llama3.1 to choose a model
```

Cloud is strictly opt-in — you have to say so out loud:

```bash
export ANTHROPIC_API_KEY=sk-...
python iching.py "should I take the new path?" --anthropic             # cloud only
python iching.py "should I take the new path?" --allow-cloud-fallback  # local first, cloud only if local fails
```

**By default nothing leaves your machine.** The cloud is used only when you pass `--anthropic` or `--allow-cloud-fallback`; a stray `ANTHROPIC_API_KEY` in your environment will never silently exfiltrate your question.

## Files

| path | what it is |
|------|------------|
| `iching.py` | the oracle: cast → hexagram → changing lines → resulting hexagram → reading |
| `iching_data.py` | the validated 64-hexagram King Wen table + the gatekeeper |
| `extras/tarot.py` | a minimal 3-card tarot draw (same engine/narrator split) |

## License

- **Code:** MIT — see [`LICENSE`](LICENSE).
- **Data:** the 64-hexagram / trigram table is derived from Wikipedia's *List of hexagrams of the I Ching* (CC BY-SA). See [`NOTICE`](NOTICE) for attribution.

*The dice are honest. Only the poetry is free — and by default, it whispers locally.*
