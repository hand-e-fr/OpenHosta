#!/bin/bash
# scripts/build_compat_matrix_types.sh
#
# Generates a markdown type-compatibility matrix.
# Rows  = one Python type per row (driven by COMPAT_META in test_compat_logistics.py)
# Cols  = one column per LLM model discovered via GET <base_url>/models
#
# Phase 0 — Setup:    create an isolated venv (uv, Python 3.12 by default)
# Phase 1 — Discover: call /models on every endpoint in .supported_providers.yaml
# Phase 2 — Test:     run each pytest test individually per (endpoint, model) pair
# Phase 3 — Report:   write docs/compat_matrix_types.md
#
# Usage:
#   bash scripts/build_compat_matrix_types.sh
#   bash scripts/build_compat_matrix_types.sh --python 3.11
#   bash scripts/build_compat_matrix_types.sh --models "gpt-4.1,gpt-4.1-mini"
#   bash scripts/build_compat_matrix_types.sh --config .supported_providers.yaml

set -uo pipefail

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 1

CONFIG_FILE="$REPO_ROOT/.supported_providers.yaml"
TEST_FILE="tests/typing/test_compat_logistics.py"
RESULTS_FILE="$REPO_ROOT/docs/compat_matrix_types.md"
LOG_DIR="$REPO_ROOT/logs"
LOG="$LOG_DIR/compat_types.log"
STATUS_DIR="$LOG_DIR/compat_type_status"
VENV_DIR="$REPO_ROOT/.venv_compat_types"

# ── CLI argument parsing ───────────────────────────────────────────────────────
PY_VERSION="3.12"
CLI_MODELS_FILTER="NONE"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python)  PY_VERSION="$2";         shift 2 ;;
        --models)  CLI_MODELS_FILTER="$2";   shift 2 ;;
        --config)  CONFIG_FILE="$2";         shift 2 ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--python 3.12] [--models \"m1,m2\"] [--config file]" >&2
            exit 1 ;;
    esac
done

# ── Sanity checks ─────────────────────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config file not found: $CONFIG_FILE" >&2; exit 1
fi
if [[ ! -f "$TEST_FILE" ]]; then
    echo "❌ Test file not found: $TEST_FILE" >&2; exit 1
fi

mkdir -p "$LOG_DIR" "$STATUS_DIR" "$(dirname "$RESULTS_FILE")"
rm -f "$LOG"
rm -rf "$STATUS_DIR"/*
touch "$LOG"

echo "🔧 Type compatibility matrix builder"          | tee -a "$LOG"
echo "📂 Repo root  : $REPO_ROOT"                    | tee -a "$LOG"
echo "📄 Config     : $CONFIG_FILE"                  | tee -a "$LOG"
echo "🧪 Test file  : $TEST_FILE"                    | tee -a "$LOG"
echo "🐍 Python     : $PY_VERSION"                   | tee -a "$LOG"
[[ "$CLI_MODELS_FILTER" != "NONE" ]] && \
echo "🔍 Filter     : $CLI_MODELS_FILTER"            | tee -a "$LOG"

# ── Phase 0 — Venv setup ──────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "━━━ Phase 0: Environment setup ━━━" | tee -a "$LOG"

if ! uv python --help &>/dev/null; then
    echo "❌ uv does not support 'uv python'." | tee -a "$LOG"; exit 1
fi

echo "📦 Installing Python $PY_VERSION via uv..." | tee -a "$LOG"
uv python install "$PY_VERSION" &>> "$LOG" \
    || { echo "❌ Failed to install Python $PY_VERSION." | tee -a "$LOG"; exit 1; }

echo "🏗️  Creating venv $VENV_DIR ..." | tee -a "$LOG"
rm -rf "$VENV_DIR"
uv venv "$VENV_DIR" --python "$PY_VERSION" &>> "$LOG" \
    || { echo "❌ Failed to create venv." | tee -a "$LOG"; exit 1; }

PYTHON="$VENV_DIR/bin/python3"
PYTEST="$VENV_DIR/bin/pytest"

echo "📥 Installing project, pytest, pyyaml, pydantic..." | tee -a "$LOG"
uv pip install -e . --python "$PYTHON" &>> "$LOG" \
    || { echo "❌ Failed to install project." | tee -a "$LOG"; exit 1; }
uv pip install pytest==8.3.2 pyyaml pydantic pillow --python "$PYTHON" &>> "$LOG"

echo "✅ Environment ready: $("$PYTHON" --version)" | tee -a "$LOG"

# ── Embedded Python helpers ────────────────────────────────────────────────────

# Helper: parse .supported_providers.yaml → tab-separated lines
#   <id> <base_url> <api_key|-> <yaml_model_filter_csv|NONE>
parse_providers() {
"$PYTHON" - "$CONFIG_FILE" <<'PYEOF'
import sys
try:
    import yaml
except ImportError:
    sys.exit("❌ PyYAML not found in venv.")
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
for ep in data.get("endpoints", []):
    eid        = ep.get("id", "unknown")
    url        = ep.get("base_url", "").rstrip("/")
    key        = ep.get("api_key", "-")
    models     = ep.get("models", [])
    filter_csv = ",".join(models) if models else "NONE"
    print(f"{eid}\t{url}\t{key}\t{filter_csv}")
PYEOF
}

# Helper: GET <base_url>/models → one retained model ID per line
list_models() {
    local base_url="$1" api_key="$2" yaml_filter="$3" cli_filter="$4"
"$PYTHON" - "$base_url" "$api_key" "$yaml_filter" "$cli_filter" <<'PYEOF'
import sys, json, urllib.request, urllib.error
base_url, api_key, yaml_filter, cli_filter = sys.argv[1:]
base_url = base_url.rstrip("/")
req = urllib.request.Request(f"{base_url}/models")
if api_key != "-":
    req.add_header("Authorization", f"Bearer {api_key}")
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read())
except urllib.error.URLError as e:
    print(f"ERROR: {e}", file=sys.stderr); sys.exit(1)
all_ids = [m["id"] for m in body.get("data", [])]
if cli_filter != "NONE":
    wanted = set(cli_filter.split(","))
elif yaml_filter != "NONE":
    wanted = set(yaml_filter.split(","))
else:
    wanted = None
for mid in all_ids:
    if wanted is None or mid in wanted:
        print(mid)
PYEOF
}

# ── Phase 1 — Model discovery ─────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "━━━ Phase 1: Model discovery ━━━" | tee -a "$LOG"

declare -a PAIRS=()           # "eid|model_id|base_url|api_key"
declare -a ALL_MODEL_LABELS=()

while IFS=$'\t' read -r eid url api_key yaml_filter; do
    echo "🔍 [$eid] Calling $url/models ..." | tee -a "$LOG"
    mapfile -t models_found < <(list_models "$url" "$api_key" "$yaml_filter" "$CLI_MODELS_FILTER" 2>>"$LOG")

    if [[ ${#models_found[@]} -eq 0 ]]; then
        echo "  ⚠️  No models retained — skipping." | tee -a "$LOG"; continue
    fi

    echo "  ✅ ${#models_found[@]} model(s) retained." | tee -a "$LOG"
    for mid in "${models_found[@]}"; do
        echo "    • $mid" | tee -a "$LOG"
        PAIRS+=("${eid}|${mid}|${url}|${api_key}")
        ALL_MODEL_LABELS+=("$mid")
    done
done < <(parse_providers)

if [[ ${#PAIRS[@]} -eq 0 ]]; then
    echo "❌ No models to test. Exiting." | tee -a "$LOG"; exit 1
fi
echo "Total: ${#PAIRS[@]} (endpoint × model) pair(s)." | tee -a "$LOG"

# ── Phase 1b — Collect individual test IDs ────────────────────────────────────
echo "" | tee -a "$LOG"
echo "📋 Collecting test IDs from $TEST_FILE ..." | tee -a "$LOG"

mapfile -t RAW_IDS < <(
    "$PYTEST" "$TEST_FILE" --collect-only -q 2>/dev/null \
    | grep "::" | grep -v "^$" | awk '{print $1}'
)

if [[ ${#RAW_IDS[@]} -eq 0 ]]; then
    echo "❌ No tests found in $TEST_FILE." | tee -a "$LOG"; exit 1
fi

# Strip the file prefix to keep only  TestClass::test_name
declare -a TEST_IDS=()
for raw in "${RAW_IDS[@]}"; do
    # raw = tests/typing/test_compat_logistics.py::TestCompatLogistics::test_int
    short="${raw##*test_compat_logistics.py::}"
    TEST_IDS+=("$short")
done

echo "  Found ${#TEST_IDS[@]} test(s):" | tee -a "$LOG"
for tid in "${TEST_IDS[@]}"; do echo "    • $tid" | tee -a "$LOG"; done

# ── Phase 2 — Run tests ───────────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "━━━ Phase 2: Running type tests ━━━" | tee -a "$LOG"

for pair in "${PAIRS[@]}"; do
    IFS='|' read -r eid mid base_url api_key <<< "$pair"
    mid_safe="${mid//\//_}"
    mkdir -p "$STATUS_DIR/$mid_safe"

    echo "" | tee -a "$LOG"
    echo "🤖 Model: $mid  (endpoint: $eid)" | tee -a "$LOG"

    for tid in "${TEST_IDS[@]}"; do
        # tid = TestCompatLogistics::test_int
        test_safe="${tid//::/_}"
        test_log="$LOG_DIR/types_${mid_safe}_${test_safe}.log"

        PYTEST_ARGS=(
            "${TEST_FILE}::${tid}"
            "--model-name=${mid}"
            "--endpoint-url=${base_url}"
            "-v" "--tb=short"
        )
        [[ "$api_key" != "-" ]] && PYTEST_ARGS+=("--endpoint-api-key=${api_key}")

        echo -n "  🧪 $tid ... " | tee -a "$LOG"
        if "$PYTEST" "${PYTEST_ARGS[@]}" > "$test_log" 2>&1; then
            echo "PASS" > "$STATUS_DIR/$mid_safe/$test_safe"
            echo "✅" | tee -a "$LOG"
        else
            echo "FAIL" > "$STATUS_DIR/$mid_safe/$test_safe"
            echo "❌" | tee -a "$LOG"
        fi
    done
done

# ── Phase 3 — Build the report ────────────────────────────────────────────────
echo "" | tee -a "$LOG"
echo "━━━ Phase 3: Writing report ━━━" | tee -a "$LOG"

"$PYTHON" - "$TEST_FILE" "$STATUS_DIR" "${ALL_MODEL_LABELS[@]}" <<'PYEOF' > "$RESULTS_FILE"
import sys, os

test_file   = sys.argv[1]
status_dir  = sys.argv[2]
model_list  = sys.argv[3:]   # one arg per model label

# ── Load COMPAT_META from the test file ──
import importlib.util
mod_name = "test_compat_logistics"
spec = importlib.util.spec_from_file_location(mod_name, test_file)
mod  = importlib.util.module_from_spec(spec)
sys.modules[mod_name] = mod
spec.loader.exec_module(mod)
meta = mod.COMPAT_META   # list of (test_id, type_display, signature)

# ── Read status files ──
# Status files: status_dir/<mid_safe>/<test_safe>  → "PASS" | "FAIL"
def read_status(mid_safe, test_id):
    test_safe = test_id.replace("::", "_")
    p = os.path.join(status_dir, mid_safe, test_safe)
    if not os.path.exists(p):
        return "⚠️"
    return "✅" if open(p).read().strip() == "PASS" else "❌"

# Sanitize model names for dir lookup
def mid_safe(m):
    return m.replace("/", "_")

# ── Render markdown ──
lines = []
lines.append("# Type Compatibility Matrix")
lines.append("")
lines.append("Type support for `emulate()` — nominal logistics document management cases.")
lines.append("")

# Header
cols = " | ".join(f"`{m}`" for m in model_list)
lines.append(f"| Python type | Fonction testée (`return emulate()`) | {cols} |")

sep_models = " | ".join(":---:" for _ in model_list)
lines.append(f"| --- | --- | {sep_models} |")

# Rows
for (test_id, type_display, signature) in meta:
    cells = " | ".join(read_status(mid_safe(m), test_id) for m in model_list)
    lines.append(f"| `{type_display}` | `{signature}` | {cells} |")

lines.append("")
lines.append("### Summary")
lines.append("")
lines.append(f"- **Models:** {', '.join(f'`{m}`' for m in model_list)}")
lines.append(f"- **Types tested:** {len(meta)}")
lines.append(f"- 📅 Updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
lines.append("")
lines.append("_Detailed logs: `logs/types_<model>_<TestClass_test_name>.log`_")

print("\n".join(lines))
PYEOF

echo "✨ Done! Report: $RESULTS_FILE" | tee -a "$LOG"
