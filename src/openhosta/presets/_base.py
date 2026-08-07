"""Base preset classes with cross-backend equivalence documentation."""

# ============================================================================
# THINKING / REASONING — equivalence table
#
# +-----------+--------------------+--------------------+------------------------+-------------------------+------------------
# | preset    | vLLM / SGLang      | Ollama             | OpenAI o-series        | Anthropic                | Google Gemini
# +-----------+--------------------+--------------------+------------------------+-------------------------+------------------
# | disabled  | enable_thinking    | thinking_enabled   | [no temp/reasoning]    | thinking: disabled      | thinking_config
# |           | = False            | = false            |                        | (empty ext_thinking)    | {disable: true}
# +-----------+--------------------+--------------------+------------------------+-------------------------+------------------
# | enabled   | enable_thinking    | thinking_enabled   | (n/a)                  | (default)               | (default)
# |           | = True             | = true             |                        | thinking: {type: "enabled"}
# +-----------+--------------------+--------------------+------------------------+-------------------------+------------------
# | minimal   | budget_tokens:128  | thinking_budget:128| reasoning.effort:low   | thinking: {budget:128}  | budget:128
# | low       | budget_tokens:1024 | thinking_budget:1K | reasoning.effort:low   | thinking: {budget:1024} | budget:1024
# | medium    | budget_tokens:2048 | thinking_budget:2K | reasoning.effort:medium| thinking: {budget:2048} | budget:2048
# | high      | budget_tokens:4096 | thinking_budget:4K | reasoning.effort:high  | thinking: {budget:4096} | budget:4096
# | max       | budget_tokens:16384| thinking_budget:16K| (n/a)                  | thinking: {budget:16384}| (n/a)
# +-----------+--------------------+--------------------+------------------------+-------------------------+------------------
# ============================================================================

# ============================================================================
# SAMPLING — equivalence table
#
# +-----------+------+-------+-------+-------+-------+--------+--------+
# | preset    | temp | top_p | top_k | min_p | rep_p | pres_p | freq_p |
# +-----------+------+-------+-------+-------+-------+--------+--------+
# | creative  | 1.0  | 0.95  |  20   | 0.0   | 1.0   | 0.0    | 0.0    |
# | general   | 1.0  | 0.95  |  20   | 0.0   | 1.0   | 0.0    | 0.0    |
# | coding    | 0.6  | 0.95  |  20   | 0.0   | 1.0   | 0.0    | 0.0    |
# | instruct  | 0.7  | 0.80  |  20   | 0.0   | 1.0   | 1.5    | 0.0    |
# | precise   | 0.2  | 0.50  |  10   | 0.0   | 1.1   | 0.0    | 0.0    |
# +-----------+------+-------+-------+-------+-------+--------+--------+
# ============================================================================

# ============================================================================
# OUTPUT LENGTH — equivalent across all backends (max_tokens / max_new_tokens)
#
# +----------+----------+
# | preset   | max_tokens |
# +----------+----------+
# | short    | 256      |
# | medium   | 2048     |
# | long     | 8192     |
# +----------+----------+
# ============================================================================

# ============================================================================
# SAFETY / CONTENT FILTERING — backend-specific implementations
#
# +----------+------------------+---------------------+-----------------------+
# | preset   | vLLM / SGLang   | Anthropic           | OpenAI / Gemini       |
# +----------+------------------+---------------------+-----------------------+
# | strict   | pres_pen: 2.0   | safety: strict      | content_filter: strict|
# | relaxed  | pres_pen: 0.0   | safety: relaxed     | content_filter: none  |
# | off      | freq_pen: 0.0   | safety: off         | (n/a)                 |
# +----------+------------------+---------------------+-----------------------+
# ============================================================================

__all__ = []
