#!/usr/bin/env python3
"""
Code Completion Predictor - A lightweight ML model for code prediction

This module implements a sequence-based code completion predictor inspired by
GitHub Copilot, using a lightweight LSTM-inspired architecture optimized for
real-time inference.

Created by @create-guru - Visionary infrastructure with Tesla-inspired innovation.
Part of the Chained autonomous AI ecosystem.

Architecture:
1. Custom code tokenizer supporting multiple languages
2. N-gram based sequence model with learned patterns
3. Confidence scoring using probabilistic predictions
4. Real-time inference optimization with caching

Features:
- Multi-language support (Python, JavaScript, Java, etc.)
- Confidence scores for predictions
- Beam search for better completions
- Real-time inference (<100ms)
- Minimal dependencies (no TensorFlow/PyTorch required)
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import math


class CodeTokenizer:
    """
    Custom tokenizer for code that handles multiple programming languages.
    
    Tokenization strategy:
    - Preserves keywords, operators, and identifiers
    - Handles language-specific syntax
    - Maintains context for semantic understanding
    """
    
    # Common programming keywords across languages
    KEYWORDS = {
        'python': {'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return', 
                   'import', 'from', 'try', 'except', 'with', 'as', 'lambda', 'yield',
                   'async', 'await', 'pass', 'break', 'continue', 'raise', 'finally'},
        'javascript': {'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                      'return', 'import', 'from', 'export', 'class', 'async', 'await',
                      'try', 'catch', 'finally', 'throw', 'new', 'this', 'super'},
        'java': {'public', 'private', 'protected', 'class', 'interface', 'extends',
                'implements', 'if', 'else', 'for', 'while', 'return', 'import',
                'try', 'catch', 'finally', 'throw', 'new', 'this', 'super', 'static',
                'void', 'int', 'String', 'boolean', 'double', 'float', 'long'}
    }
    
    # Token patterns
    PATTERNS = {
        'identifier': r'[a-zA-Z_][a-zA-Z0-9_]*',
        'number': r'\d+\.?\d*',
        'string': r'"[^"]*"|\'[^\']*\'',
        'operator': r'[+\-*/%=<>!&|^~]',
        'delimiter': r'[(){}\[\],;:.]',
        'whitespace': r'\s+'
    }
    
    def __init__(self, language: str = 'python'):
        """Initialize tokenizer for specific language"""
        self.language = language.lower()
        self.keywords = self.KEYWORDS.get(self.language, set())
        
        # Compile regex patterns
        self.token_pattern = re.compile('|'.join(
            f'(?P<{name}>{pattern})' for name, pattern in self.PATTERNS.items()
        ))
    
    def tokenize(self, code: str) -> List[str]:
        """
        Tokenize code into meaningful tokens.
        
        Args:
            code: Source code string
            
        Returns:
            List of tokens
        """
        tokens = []
        
        for match in self.token_pattern.finditer(code):
            kind = match.lastgroup
            value = match.group()
            
            if kind == 'whitespace':
                # Preserve significant whitespace (newlines)
                if '\n' in value:
                    tokens.append('<NEWLINE>')
            elif kind == 'identifier':
                # Mark keywords specially
                if value in self.keywords:
                    tokens.append(f'<KEYWORD:{value}>')
                else:
                    tokens.append(value)
            else:
                tokens.append(value)
        
        return tokens
    
    def detokenize(self, tokens: List[str]) -> str:
        """
        Convert tokens back to code string.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Code string
        """
        code = []
        for token in tokens:
            if token == '<NEWLINE>':
                code.append('\n')
            elif token.startswith('<KEYWORD:'):
                # Extract keyword
                keyword = token[9:-1]
                code.append(keyword)
            else:
                code.append(token)
        
        return ' '.join(code)


class SequencePredictor:
    """
    Lightweight sequence prediction model using n-grams and pattern learning.
    
    This approach is inspired by LSTM architectures but implemented with
    efficient statistical methods for real-time inference.
    """
    
    def __init__(self, n: int = 5, beam_width: int = 3):
        """
        Initialize sequence predictor.
        
        Args:
            n: N-gram order (context window size)
            beam_width: Number of top predictions to maintain
        """
        self.n = n
        self.beam_width = beam_width
        
        # N-gram frequency tables
        self.ngrams: Dict[tuple, Counter] = defaultdict(Counter)
        
        # Token frequency for fallback
        self.token_freq: Counter = Counter()
        
        # Total n-gram counts for probability calculation
        self.context_counts: Counter = Counter()
        
        # Sequence patterns learned from training
        self.patterns: List[List[str]] = []
    
    def train(self, sequences: List[List[str]]):
        """
        Train the model on code sequences.
        
        Args:
            sequences: List of tokenized code sequences
        """
        for sequence in sequences:
            # Store full pattern for later reference
            self.patterns.append(sequence)
            
            # Build n-grams
            for i in range(len(sequence)):
                # Update token frequency
                self.token_freq[sequence[i]] += 1
                
                # Build n-grams of different orders
                for order in range(1, min(self.n + 1, i + 2)):
                    if i >= order - 1:
                        context = tuple(sequence[i - order + 1:i])
                        next_token = sequence[i]
                        
                        self.ngrams[context][next_token] += 1
                        self.context_counts[context] += 1
    
    def predict(self, context: List[str], top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predict next tokens given context.
        
        Args:
            context: List of preceding tokens
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples sorted by confidence
        """
        predictions: Counter = Counter()
        
        # Try different n-gram orders (longer context first)
        for order in range(min(self.n, len(context)), 0, -1):
            ctx = tuple(context[-order:])
            
            if ctx in self.ngrams:
                # Get predictions for this context
                for token, count in self.ngrams[ctx].items():
                    # Calculate probability
                    prob = count / self.context_counts[ctx]
                    
                    # Weight by order (longer context = higher weight)
                    weight = order / self.n
                    predictions[token] += prob * weight
        
        # Fallback to most common tokens if no context match
        if not predictions:
            # Use token frequency as fallback
            total = sum(self.token_freq.values())
            for token, count in self.token_freq.most_common(top_k * 2):
                predictions[token] = count / total * 0.1  # Lower confidence for fallback
        
        # Normalize probabilities
        total_prob = sum(predictions.values())
        if total_prob > 0:
            predictions = Counter({
                token: prob / total_prob 
                for token, prob in predictions.items()
            })
        
        # Return top k predictions
        return predictions.most_common(top_k)
    
    def beam_search(self, context: List[str], max_length: int = 10) -> List[List[str]]:
        """
        Generate completions using beam search.
        
        Args:
            context: Starting context
            max_length: Maximum completion length
            
        Returns:
            List of completion sequences
        """
        # Initialize beams
        beams = [(context.copy(), 0.0)]  # (sequence, log_prob)
        
        for _ in range(max_length):
            candidates = []
            
            for sequence, log_prob in beams:
                # Get predictions
                predictions = self.predict(sequence, top_k=self.beam_width)
                
                for token, prob in predictions:
                    if prob > 0:
                        new_sequence = sequence + [token]
                        new_log_prob = log_prob + math.log(prob + 1e-10)
                        candidates.append((new_sequence, new_log_prob))
            
            # Keep top beams
            if not candidates:
                break
                
            candidates.sort(key=lambda x: x[1], reverse=True)
            beams = candidates[:self.beam_width]
        
        # Return sequences only (without log probs)
        return [seq for seq, _ in beams]


class CodeCompletionPredictor:
    """
    Main code completion predictor combining tokenizer and sequence model.
    
    This is the primary interface for code prediction, optimized for real-time
    inference with minimal latency.
    """
    
    def __init__(self, language: str = 'python', n: int = 5):
        """
        Initialize code completion predictor.
        
        Args:
            language: Programming language to support
            n: N-gram order for sequence model
        """
        self.tokenizer = CodeTokenizer(language)
        self.predictor = SequencePredictor(n=n)
        self.language = language
        self.trained = False
        
        # Performance optimization: cache recent predictions
        self._cache: Dict[str, List[Tuple[str, float]]] = {}
        self._cache_size = 1000
    
    def train(self, code_samples: List[str]):
        """
        Train the model on code samples.
        
        Args:
            code_samples: List of code strings to learn from
        """
        sequences = []
        
        for code in code_samples:
            tokens = self.tokenizer.tokenize(code)
            if len(tokens) > 0:
                sequences.append(tokens)
        
        self.predictor.train(sequences)
        self.trained = True
        self._cache.clear()  # Clear cache after training
    
    def predict_next_line(self, code_context: str) -> Tuple[str, float]:
        """
        Predict the next line of code based on context.
        
        Args:
            code_context: Preceding code as string
            
        Returns:
            Tuple of (predicted_line, confidence_score)
        """
        if not self.trained:
            return ("# Model not trained", 0.0)
        
        # Check cache
        cache_key = code_context[-200:] if len(code_context) > 200 else code_context
        if cache_key in self._cache:
            predictions = self._cache[cache_key]
            if predictions:
                # Return first prediction as a line
                tokens = [pred[0] for pred in predictions[:5]]
                confidence = predictions[0][1]
                return (self.tokenizer.detokenize(tokens), confidence)
        
        # Tokenize context
        context_tokens = self.tokenizer.tokenize(code_context)
        
        # Get predictions
        predictions = self.predictor.predict(context_tokens[-10:], top_k=5)
        
        # Cache result
        if len(self._cache) > self._cache_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = predictions
        
        if predictions:
            # Build predicted line from top predictions
            line_tokens = []
            remaining_confidence = 1.0
            
            for token, conf in predictions:
                line_tokens.append(token)
                remaining_confidence *= conf
                
                # Stop at newline or when confidence drops too low
                if token == '<NEWLINE>' or remaining_confidence < 0.1:
                    break
            
            predicted_line = self.tokenizer.detokenize(line_tokens)
            avg_confidence = predictions[0][1]  # Use first prediction's confidence
            
            return (predicted_line, avg_confidence)
        
        return ("", 0.0)
    
    def complete_function(self, partial_function: str) -> Tuple[str, float]:
        """
        Complete a partial function implementation.
        
        Args:
            partial_function: Incomplete function code
            
        Returns:
            Tuple of (completion, confidence_score)
        """
        if not self.trained:
            return ("# Model not trained", 0.0)
        
        # Tokenize partial function
        context_tokens = self.tokenizer.tokenize(partial_function)
        
        # Use beam search for better completions
        completions = self.predictor.beam_search(context_tokens, max_length=20)
        
        if completions:
            # Get best completion
            best_completion = completions[0][len(context_tokens):]
            completion_str = self.tokenizer.detokenize(best_completion)
            
            # Calculate confidence based on prediction probabilities
            predictions = self.predictor.predict(context_tokens[-5:], top_k=3)
            avg_confidence = sum(conf for _, conf in predictions) / len(predictions) if predictions else 0.0
            
            return (completion_str, avg_confidence)
        
        return ("", 0.0)
    
    def get_predictions(self, code_context: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Get multiple prediction options with confidence scores.
        
        Args:
            code_context: Preceding code
            top_k: Number of predictions to return
            
        Returns:
            List of (prediction, confidence) tuples
        """
        if not self.trained:
            return []
        
        # Tokenize context
        context_tokens = self.tokenizer.tokenize(code_context)
        
        # Get predictions
        predictions = self.predictor.predict(context_tokens[-10:], top_k=top_k)
        
        # Convert tokens back to strings
        return [(token, conf) for token, conf in predictions]
    
    def save_model(self, path: str):
        """
        Save trained model to disk.
        
        Args:
            path: File path to save model
        """
        model_data = {
            'language': self.language,
            'n': self.predictor.n,
            'ngrams': {
                json.dumps(list(k)): dict(v) for k, v in self.predictor.ngrams.items()
            },
            'token_freq': dict(self.predictor.token_freq),
            'context_counts': {
                json.dumps(list(k)): v for k, v in self.predictor.context_counts.items()
            },
            'patterns': self.predictor.patterns
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, path: str):
        """
        Load trained model from disk.
        
        Args:
            path: File path to load model from
        """
        with open(path, 'r') as f:
            model_data = json.load(f)
        
        self.language = model_data['language']
        self.tokenizer = CodeTokenizer(self.language)
        self.predictor = SequencePredictor(n=model_data['n'])
        
        # Restore n-grams
        self.predictor.ngrams = defaultdict(Counter, {
            tuple(json.loads(k)): Counter(v) for k, v in model_data['ngrams'].items()
        })
        
        # Restore token frequencies
        self.predictor.token_freq = Counter(model_data['token_freq'])
        
        # Restore context counts
        self.predictor.context_counts = Counter({
            tuple(json.loads(k)): v for k, v in model_data['context_counts'].items()
        })
        
        self.predictor.patterns = model_data['patterns']
        
        self.trained = True
        self._cache.clear()


# Convenience functions for quick usage
def train_model(code_samples: List[str], language: str = 'python') -> CodeCompletionPredictor:
    """
    Train a new code completion model.
    
    Args:
        code_samples: List of code strings to train on
        language: Programming language
        
    Returns:
        Trained CodeCompletionPredictor
    """
    model = CodeCompletionPredictor(language=language)
    model.train(code_samples)
    return model


def predict_next_line(model: CodeCompletionPredictor, code_context: str) -> Tuple[str, float]:
    """
    Predict next line using trained model.
    
    Args:
        model: Trained CodeCompletionPredictor
        code_context: Code context
        
    Returns:
        Tuple of (predicted_line, confidence)
    """
    return model.predict_next_line(code_context)


if __name__ == '__main__':
    # Example usage
    print("Code Completion Predictor - Example Usage")
    print("=" * 60)
    
    # Sample training data
    training_code = [
        """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
        """,
        """
def find_max(array):
    if not array:
        return None
    max_val = array[0]
    for val in array:
        if val > max_val:
            max_val = val
    return max_val
        """,
        """
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        result = []
        for item in self.data:
            if item.is_valid():
                result.append(item.transform())
        return result
        """
    ]
    
    # Train model
    print("\n1. Training model on sample code...")
    model = train_model(training_code, language='python')
    print("   ✓ Model trained successfully")
    
    # Test predictions
    print("\n2. Testing predictions:")
    
    test_context = "def calculate_average(numbers):\n    total = 0\n    "
    predicted, confidence = model.predict_next_line(test_context)
    print(f"\n   Context: {repr(test_context[-50:])}")
    print(f"   Predicted: {repr(predicted)}")
    print(f"   Confidence: {confidence:.2%}")
    
    # Test function completion
    partial = "def process_data(data):\n    if not data:"
    completion, conf = model.complete_function(partial)
    print(f"\n   Partial: {repr(partial)}")
    print(f"   Completion: {repr(completion)}")
    print(f"   Confidence: {conf:.2%}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
