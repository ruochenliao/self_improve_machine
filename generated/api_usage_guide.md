# Swift-Flux API Quickstart

Try these commands:

1. **Code generation**: `curl -X POST http://your-api-url/generate-code -d '{"prompt": "Python script to calculate factorial"}'`
2. **Code review**: `curl -X POST http://your-api-url/code-review -F 'code=@my_script.py'
3. **Summarize text**: `curl http://your-api-url/summarize?url=https://example.com/article`

All endpoints return JSON with `result` field.