# API Testing

Run the following curl command to test the API while the server is running (`make run`):

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful programming tutor specializing in Swift and iOS development."},
      {"role": "user", "content": "Can you explain what a protocol is in Swift?"}
    ],
    "user_id": "student123",
    "context": {
      "current_lesson": "swift_basics"
    }
  }'
```

You should receive a JSON response from the OpenAI API explaining Swift protocols.
