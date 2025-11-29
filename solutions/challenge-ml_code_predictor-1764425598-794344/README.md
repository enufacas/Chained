# Code Completion Predictor

A lightweight N-gram based Machine Learning model for code prediction and completion.

## Features
- **Language Agnostic:** Works with any programming language.
- **Lightweight:** Uses an efficient N-gram statistical model.
- **Real-time:** Fast inference suitable for real-time completion.
- **Confidence Scores:** Returns probability-based confidence for predictions.

## Files
- `predictor.py`: The main implementation of the `CodePredictor` class.
- `test_predictor.py`: Unit tests ensuring correctness.

## Usage

```python
from predictor import CodePredictor

# Initialize
predictor = CodePredictor(n=3)

# Train
predictor.train("def hello():\n    print('Hello')")

# Predict Next Token
token, confidence = predictor.predict_next_token(['def', 'hello', '(', ')', ':', '\n'])
print(f"Next token: {token} ({confidence:.2f})")

# Predict Next Line
line, confidence = predictor.predict_next_line("def hello():\n")
print(f"Next line: {line}")
```

## Running Tests

```bash
python3 test_predictor.py
```

## Approach
The solution uses an N-gram model which predicts the next token based on the history of the previous N-1 tokens. It handles code tokenization by splitting words and symbols, allowing it to learn structural patterns (like indentation blocks, function definitions, etc.) from the training data.

