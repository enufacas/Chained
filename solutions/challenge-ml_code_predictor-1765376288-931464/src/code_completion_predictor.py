#!/usr/bin/env python3
"""
Code Completion Predictor - A lightweight ML model for code prediction

This module implements a sequence-based code completion predictor inspired by
GitHub Copilot, using a lightweight N-gram statistical architecture optimized for
real-time inference.

Created by @create-botter - Visionary infrastructure with Tesla-inspired innovation.
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
        Convert tokens back to code.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Reconstructed code string
        """
        result = []
        
        for token in tokens:
            if token == '<NEWLINE>':
                result.append('\n')
            elif token.startswith('<KEYWORD:'):
                # Extract keyword from marker
                keyword = token[9:-1]
                result.append(keyword)
            else:
                result.append(token)
        
        return ' '.join(result)


class SequencePredictor:
    """
    N-gram based sequence predictor with learned patterns.
    
    Uses traditional statistical language modeling for sequence prediction:
    - Learns from token sequences
    - Builds n-gram frequency tables
    - Provides confidence scores
    - Supports beam search for better predictions
    """
    
    def __init__(self, n: int = 5, beam_width: int = 3):
        """
        Initialize sequence predictor.
        
        Args:
            n: N-gram order (context length)
            beam_width: Number of alternatives to consider in beam search
        """
        self.n = n
        self.beam_width = beam_width
        
        # N-gram frequency tables
        self.ngrams: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        
        # Total counts for probability calculation
        self.context_counts: Dict[Tuple[str, ...], int] = defaultdict(int)
        
        # Prediction cache for performance
        self.cache: Dict[str, List[Tuple[str, float]]] = {}
        self.max_cache_size = 1000
    
    def train(self, sequences: List[List[str]]):
        """
        Train the model on token sequences.
        
        Args:
            sequences: List of token sequences
        """
        for sequence in sequences:
            # Build n-grams of various orders
            for i in range(len(sequence)):
                # Try different context lengths (1 to n)
                for context_len in range(1, min(self.n + 1, i + 1)):
                    context = tuple(sequence[i - context_len:i])
                    
                    if i < len(sequence):
                        next_token = sequence[i]
                        self.ngrams[context][next_token] += 1
                        self.context_counts[context] += 1
    
    def predict(self, context: List[str], top_k: int = 1) -> List[Tuple[str, float]]:
        """
        Predict next token(s) given context.
        
        Args:
            context: List of previous tokens
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples
        """
        # Check cache
        cache_key = '|'.join(context[-self.n:])
        if cache_key in self.cache:
            return self.cache[cache_key][:top_k]
        
        predictions = []
        
        # Try different context lengths (longest first)
        for context_len in range(min(self.n, len(context)), 0, -1):
            ctx = tuple(context[-context_len:])
            
            if ctx in self.ngrams:
                # Calculate probabilities for all possible next tokens
                total = self.context_counts[ctx]
                
                for token, count in self.ngrams[ctx].most_common(top_k):
                    # Confidence based on frequency and context length
                    base_confidence = count / total
                    
                    # Weight by context length (longer context = more confident)
                    length_weight = context_len / self.n
                    confidence = base_confidence * (0.5 + 0.5 * length_weight)
                    
                    predictions.append((token, confidence))
                
                break
        
        # Default prediction if no match
        if not predictions:
            predictions = [('<UNKNOWN>', 0.1)]
        
        # Update cache
        if len(self.cache) < self.max_cache_size:
            self.cache[cache_key] = predictions
        
        return predictions[:top_k]
    
    def beam_search(self, context: List[str], max_length: int = 10) -> List[Tuple[List[str], float]]:
        """
        Use beam search to generate multiple completion sequences.
        
        Args:
            context: Initial context
            max_length: Maximum completion length
            
        Returns:
            List of (sequence, confidence) tuples
        """
        beams = [(context.copy(), 1.0)]
        
        for _ in range(max_length):
            candidates = []
            
            for seq, score in beams:
                predictions = self.predict(seq, top_k=self.beam_width)
                
                for token, conf in predictions:
                    if token != '<UNKNOWN>':
                        new_seq = seq + [token]
                        new_score = score * conf
                        candidates.append((new_seq, new_score))
            
            # Keep top beam_width candidates
            if candidates:
                beams = sorted(candidates, key=lambda x: x[1], reverse=True)[:self.beam_width]
            else:
                break
        
        return beams
    
    def save(self, filepath: str):
        """Save model to file"""
        model_data = {
            'n': self.n,
            'beam_width': self.beam_width,
            'ngrams': {
                '|'.join(k): dict(v) for k, v in self.ngrams.items()
            },
            'context_counts': {
                '|'.join(k): v for k, v in self.context_counts.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f)
    
    def load(self, filepath: str):
        """Load model from file"""
        with open(filepath, 'r') as f:
            model_data = json.load(f)
        
        self.n = model_data['n']
        self.beam_width = model_data['beam_width']
        
        # Reconstruct n-grams
        self.ngrams = defaultdict(Counter)
        for k, v in model_data['ngrams'].items():
            context = tuple(k.split('|'))
            self.ngrams[context] = Counter(v)
        
        # Reconstruct context counts
        self.context_counts = defaultdict(int)
        for k, v in model_data['context_counts'].items():
            context = tuple(k.split('|'))
            self.context_counts[context] = v


class CodeCompletionPredictor:
    """
    Main code completion predictor combining tokenizer and sequence model.
    
    Provides high-level API for code prediction with:
    - Multi-language support
    - Confidence scores
    - Real-time inference
    - Model persistence
    """
    
    def __init__(self, language: str = 'python', n: int = 5):
        """
        Initialize code completion predictor.
        
        Args:
            language: Programming language to target
            n: N-gram order for sequence model
        """
        self.language = language
        self.tokenizer = CodeTokenizer(language)
        self.predictor = SequencePredictor(n=n)
        self.trained = False
    
    def train(self, code_samples: List[str]):
        """
        Train the model on code samples.
        
        Args:
            code_samples: List of code strings
        """
        sequences = []
        
        for code in code_samples:
            tokens = self.tokenizer.tokenize(code)
            if tokens:
                sequences.append(tokens)
        
        self.predictor.train(sequences)
        self.trained = True
    
    def predict_next_line(self, code_context: str) -> Tuple[str, float]:
        """
        Predict the next line of code.
        
        Args:
            code_context: Code context string
            
        Returns:
            (predicted_line, confidence_score)
        """
        if not self.trained:
            return "# Model not trained", 0.0
        
        # Tokenize context
        tokens = self.tokenizer.tokenize(code_context)
        
        # Get predictions
        predictions = self.predictor.predict(tokens, top_k=1)
        
        if predictions:
            next_token, confidence = predictions[0]
            
            # Build predicted line from token
            if next_token == '<NEWLINE>':
                predicted_line = '\n'
            elif next_token.startswith('<KEYWORD:'):
                predicted_line = next_token[9:-1]
            else:
                predicted_line = next_token
            
            return predicted_line, confidence
        
        return "# Unable to predict", 0.0
    
    def complete_function(self, partial_function: str) -> Tuple[str, float]:
        """
        Complete a partial function using beam search.
        
        Args:
            partial_function: Partial function code
            
        Returns:
            (completion, confidence_score)
        """
        if not self.trained:
            return "# Model not trained", 0.0
        
        # Tokenize context
        tokens = self.tokenizer.tokenize(partial_function)
        
        # Use beam search for better completions
        beams = self.predictor.beam_search(tokens, max_length=5)
        
        if beams:
            best_seq, confidence = beams[0]
            # Extract completion (tokens after original context)
            completion_tokens = best_seq[len(tokens):]
            completion = self.tokenizer.detokenize(completion_tokens)
            return completion, confidence
        
        return "# Unable to complete", 0.0
    
    def get_predictions(self, code_context: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Get multiple prediction options.
        
        Args:
            code_context: Code context string
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples
        """
        if not self.trained:
            return [("# Model not trained", 0.0)]
        
        tokens = self.tokenizer.tokenize(code_context)
        predictions = self.predictor.predict(tokens, top_k=top_k)
        
        # Convert to readable format
        results = []
        for token, confidence in predictions:
            if token.startswith('<KEYWORD:'):
                readable = token[9:-1]
            elif token == '<NEWLINE>':
                readable = '\\n'
            else:
                readable = token
            results.append((readable, confidence))
        
        return results
    
    def save_model(self, filepath: str):
        """
        Save trained model to disk.
        
        Args:
            filepath: Path to save model
        """
        self.predictor.save(filepath)
    
    def load_model(self, filepath: str):
        """
        Load trained model from disk.
        
        Args:
            filepath: Path to load model from
        """
        self.predictor.load(filepath)
        self.trained = True


def train_model(code_samples: List[str], language: str = 'python', n: int = 5) -> CodeCompletionPredictor:
    """
    Convenience function to train a model.
    
    Args:
        code_samples: List of code strings to train on
        language: Programming language
        n: N-gram order
        
    Returns:
        Trained CodeCompletionPredictor
    """
    model = CodeCompletionPredictor(language=language, n=n)
    model.train(code_samples)
    return model


if __name__ == '__main__':
    # Demo usage
    print("Code Completion Predictor - @create-botter")
    print("=" * 50)
    
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
        def calculate_average(numbers):
            total = 0
            count = 0
            for num in numbers:
                total += num
                count += 1
            return total / count
        """,
        """
        def process_items(items):
            result = []
            for item in items:
                result.append(item)
            return result
        """
    ]
    
    # Train model
    print("\nTraining model on sample code...")
    model = train_model(training_code, language='python')
    
    # Test prediction
    print("\nTest 1: Predict next line")
    context = "def calculate_average(numbers):\n    total = 0\n    "
    predicted, confidence = model.predict_next_line(context)
    print(f"Context: {context!r}")
    print(f"Predicted: {predicted!r}")
    print(f"Confidence: {confidence:.1%}")
    
    # Test completion
    print("\nTest 2: Complete function")
    partial = "def process_data(items):\n    result = []\n    for item in items:\n        "
    completion, confidence = model.complete_function(partial)
    print(f"Partial: {partial!r}")
    print(f"Completion: {completion!r}")
    print(f"Confidence: {confidence:.1%}")
    
    print("\n✅ Demo complete!")
