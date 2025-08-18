# API Testing

Make sure the server is running (make run). Then do the following.

## Health check

```bash
curl -s http://localhost:8000/ | jq
```

## Minimal chat request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain what a protocol is in Swift in one or two sentences."}
    ]
  }' | jq
```

You should receive a JSON response from the OpenAI API explaining Swift protocols.
