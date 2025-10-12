With seed=42
Hardware: RTX 5090 32GB VRAM

This table could be generated with:
```bash
pytest tests/functionnal --junitxml=results.xml
python3 tests/parse_junit.py results.xml > tests/results.md
```

| Test       | Model            | Duration | Passed | Failed | Comments
|------------|------------------|----------|--------|--------|---------
| functional | gpt-4.1 (OpenAI) | 50.2s    | 43     | 1      | 
| functional | gpt-oss:20b      | 65.3s    | 40     | 4      | Does not support vision
| functional | mistral-small3.2 | 35.5s    | 39     | 5      | 
| functional | gemma3:12b       | 45.1s    | 39     | 5      | would do put fetch instead of git push 
| functional | gemma3:4b        | 37.6s    | 36     | 8      |
| functional | qwen3:4b         | 126.3s   | 37     | 7      |