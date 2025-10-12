With seed=42
Hardware: RTX 5090 32GB VRAM

This table could be generated with:
```bash
pytest tests/functionnal --junitxml=results.xml
python3 tests/parse_junit.py results.xml > tests/results.md
```

| Test       | Model            | Duration | Passed | Failed | Comments
|------------|------------------|----------|--------|--------|---------
| functional | gpt-4.1 (OpenAI) | 56.4s    | 44     | 0      | 
| functional | gpt-oss:20b      | 63.8s    | 41     | 3      | Does not support vision. some casting issues
| functional | mistral-small3.2 | 35.5s    | 40     | 4      | simple math issues, casting issues with dataclass
| functional | gemma3:12b       | 44.1s    | 41     | 3      | would do put fetch instead of git push
| functional | gemma3:4b        | 41.5s    | 37     | 7      | would do put fetch instead of git push, casting issues with dataclass
| functional | qwen3:4b         | 119.5s   | 38     | 6      | Does not support vision. Casting issues