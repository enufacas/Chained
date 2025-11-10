# 🤖 AI Friends: Daily Conversations

This directory contains daily conversations with different AI models about the Chained project.

## Purpose

Every day, the AI Friend workflow:
1. Selects a free AI API (using services like Puter.js that provide no-auth access)
2. Shares information about the Chained project
3. Asks for advice and suggestions
4. Saves the conversation
5. Documents it on GitHub Pages

## Structure

- `conversation_YYYYMMDD_HHMMSS.json` - Individual conversation files
- `index.json` - Index of all conversations

## Conversation Format

Each conversation file contains:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "date": "Human-readable date",
  "model": "AI model name (e.g., gpt-4.1-nano, claude-3, gemini-pro)",
  "question": "The question we asked",
  "response": "The AI's main response",
  "suggestions": ["List", "of", "actionable", "suggestions"]
}
```

## Free AI APIs Used

We rotate between different free AI APIs that don't require authentication:

1. **Puter.js** - Provides free access to GPT-4, Claude, Gemini, Llama, and more
   - No API key required
   - Browser-based integration
   - 400+ models available

2. **HuggingFace Public Models** - Open-source model access
   - Various specialized models
   - Community-driven

3. **Other No-Auth APIs** - As discovered through research
   - Continuously updated based on availability
   - Documented in conversation files

## Viewing Conversations

- **GitHub Pages**: Visit [AI Friends Page](https://enufacas.github.io/Chained/ai-friends.html)
- **GitHub Issues**: Each conversation creates an issue with the `ai-friend` label
- **Raw Files**: Browse this directory for JSON conversation data

## Benefits

This "Make a Friend Every Day" approach helps the project:
- 🧠 Get diverse perspectives from different AI architectures
- 💡 Discover new features and improvements
- 🔄 Stay fresh with varied approaches
- 🌐 Learn from the broader AI community
- 📈 Continuously improve based on external feedback

## Integration with Other Systems

Conversations influence:
- **Idea Generation**: Suggestions may inspire new issues
- **Learning System**: Advice is incorporated into project evolution
- **Timeline**: All conversations appear on GitHub Pages
- **Documentation**: Insights update project documentation

## Privacy & Ethics

- Only publicly accessible, free AI APIs are used
- No personal data is shared
- Full attribution to AI models is maintained
- Conversations are transparent and publicly documented

---

**Making friends, one AI at a time!** 🤖❤️🤖
