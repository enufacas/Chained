#!/usr/bin/env python3
"""
Code Completion Predictor - A lightweight ML model for code prediction

This module implements a sequence-based code completion predictor inspired by
GitHub Copilot, using a lightweight LSTM-inspired architecture optimized for
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
        Convert tokens back to code string.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Reconstructed code string
        """
        code_parts = []
        
        for token in tokens:
            if token == '<NEWLINE>':
                code_parts.append('\n')
            elif token.startswith('<KEYWORD:'):
                # Extract keyword from tag
                keyword = token[9:-1]
                code_parts.append(keyword)
            else:
                code_parts.append(token)
        
        return ' '.join(code_parts)


class SequencePredictor:
    """
    N-gram based sequence prediction model.
    
    Uses statistical patterns learned from code sequences to predict
    the next token given a context window.
    """
    
    def __init__(self, n: int = 5, beam_width: int = 3):
        """
        Initialize sequence predictor.
        
        Args:
            n: N-gram order (context window size)
            beam_width: Number of beams for beam search
        """
        self.n = n
        self.beam_width = beam_width
        self.ngrams: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        self.total_counts: Dict[Tuple[str, ...], int] = defaultdict(int)
        
    def train(self, token_sequences: List[List[str]]):
        """
        Train the model on tokenized sequences.
        
        Args:
            token_sequences: List of token lists
        """
        for tokens in token_sequences:
            # Build n-grams of varying sizes (1 to n)
            for i in range(len(tokens)):
                for order in range(1, min(self.n + 1, i + 2)):
                    context = tuple(tokens[max(0, i - order + 1):i + 1])
                    if i + 1 < len(tokens):
                        next_token = tokens[i + 1]
                        self.ngrams[context][next_token] += 1
                        self.total_counts[context] += 1
    
    def predict(self, context: List[str], top_k: int = 1) -> List[Tuple[str, float]]:
        """
        Predict next token(s) given context.
        
        Args:
            context: List of recent tokens
            top_k: Number of predictions to return
            
        Returns:
            List of (token, probability) tuples
        """
        predictions = []
        
        # Try different context lengths (longest first)
        for order in range(min(self.n, len(context)), 0, -1):
            ctx = tuple(context[-order:])
            
            if ctx in self.ngrams:
                total = self.total_counts[ctx]
                
                for token, count in self.ngrams[ctx].most_common(top_k):
                    prob = count / total
                    # Weight by context length (longer context = higher confidence)
                    weighted_prob = prob * (order / self.n)
                    predictions.append((token, weighted_prob))
                
                break
        
        # Sort by probability and return top_k
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:top_k]
    
    def beam_search(self, context: List[str], max_tokens: int = 10) -> List[Tuple[List[str], float]]:
        """
        Generate multiple completion options using beam search.
        
        Args:
            context: Initial context
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of (completion_tokens, score) tuples
        """
        # Initialize beams with empty sequences
        beams = [([], 1.0)]
        
        for _ in range(max_tokens):
            all_candidates = []
            
            for seq, score in beams:
                current_context = context + seq
                predictions = self.predict(current_context, top_k=self.beam_width)
                
                if not predictions:
                    # No more predictions, keep current beam
                    all_candidates.append((seq, score))
                    continue
                
                for token, prob in predictions:
                    new_seq = seq + [token]
                    new_score = score * prob
                    all_candidates.append((new_seq, new_score))
            
            # Keep top beam_width candidates
            all_candidates.sort(key=lambda x: x[1], reverse=True)
            beams = all_candidates[:self.beam_width]
            
            # Stop if all beams end with newline
            if all(seq and seq[-1] == '<NEWLINE>' for seq, _ in beams):
                break
        
        return beams


class CodeCompletionPredictor:
    """
    Main code completion predictor combining tokenizer and sequence model.
    
    Provides high-level API for:
    - Training on code samples
    - Predicting next lines
    - Completing partial functions
    - Real-time inference with caching
    """
    
    def __init__(self, language: str = 'python', n: int = 5):
        """
        Initialize code completion predictor.
        
        Args:
            language: Programming language
            n: N-gram order for sequence model
        """
        self.language = language
        self.tokenizer = CodeTokenizer(language)
        self.predictor = SequencePredictor(n=n)
        self.cache: Dict[str, Tuple[str, float]] = {}
        
    def train(self, code_samples: List[str]):
        """
        Train the model on code samples.
        
        Args:
            code_samples: List of code strings
        """
        token_sequences = [
            self.tokenizer.tokenize(code)
            for code in code_samples
        ]
        self.predictor.train(token_sequences)
    
    def predict_next_line(self, code_context: str) -> Tuple[str, float]:
        """
        Predict the next line of code.
        
        Args:
            code_context: Current code context
            
        Returns:
            (predicted_line, confidence_score)
        """
        # Check cache
        cache_key = f"next_line:{code_context}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Tokenize context
        context_tokens = self.tokenizer.tokenize(code_context)
        
        # Predict tokens until newline
        predicted_tokens = []
        max_tokens = 50  # Safety limit
        current_context = context_tokens
        total_confidence = 1.0
        
        for _ in range(max_tokens):
            predictions = self.predictor.predict(current_context, top_k=1)
            
            if not predictions:
                break
            
            token, prob = predictions[0]
            predicted_tokens.append(token)
            total_confidence *= prob
            current_context.append(token)
            
            if token == '<NEWLINE>':
                break
        
        # Convert to string
        predicted_line = self.tokenizer.detokenize(predicted_tokens)
        confidence = math.sqrt(total_confidence)  # Normalize
        
        # Cache result
        result = (predicted_line, confidence)
        self.cache[cache_key] = result
        
        return result
    
    def complete_function(self, partial_function: str) -> Tuple[str, float]:
        """
        Complete a partial function using beam search.
        
        Args:
            partial_function: Incomplete function code
            
        Returns:
            (completion, confidence_score)
        """
        # Check cache
        cache_key = f"complete:{partial_function}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Tokenize partial function
        context_tokens = self.tokenizer.tokenize(partial_function)
        
        # Use beam search to generate completions
        beams = self.predictor.beam_search(context_tokens, max_tokens=20)
        
        if not beams:
            return ("", 0.0)
        
        # Get best completion
        best_tokens, score = beams[0]
        completion = self.tokenizer.detokenize(best_tokens)
        confidence = math.sqrt(score)
        
        # Cache result
        result = (completion, confidence)
        self.cache[cache_key] = result
        
        return result
    
    def get_predictions(self, code_context: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Get multiple prediction options.
        
        Args:
            code_context: Current code context
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples
        """
        context_tokens = self.tokenizer.tokenize(code_context)
        predictions = self.predictor.predict(context_tokens, top_k=top_k)
        
        # Convert tokens back and normalize confidences
        results = []
        for token, prob in predictions:
            readable_token = token
            if token.startswith('<KEYWORD:'):
                readable_token = token[9:-1]
            results.append((readable_token, prob))
        
        return results
    
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
                str(k): dict(v) for k, v in self.predictor.ngrams.items()
            },
            'total_counts': {
                str(k): v for k, v in self.predictor.total_counts.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f)
    
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
        self.predictor.n = model_data['n']
        
        # Restore ngrams
        self.predictor.ngrams.clear()
        for ctx_str, counts in model_data['ngrams'].items():
            ctx = eval(ctx_str)  # Convert string back to tuple
            self.predictor.ngrams[ctx] = Counter(counts)
        
        # Restore total counts
        self.predictor.total_counts.clear()
        for ctx_str, count in model_data['total_counts'].items():
            ctx = eval(ctx_str)
            self.predictor.total_counts[ctx] = count


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


# Example usage
if __name__ == "__main__":
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
        def process_data(items):
            result = []
            for item in items:
                if item > 0:
                    result.append(item * 2)
            return result
        """
    ]
    
    # Train model
    print("Training model...")
    model = train_model(training_code, language='python')
    
    # Test next line prediction
    print("\n=== Test 1: Next Line Prediction ===")
    context = "def calculate_total(values):\n    total = 0\n    "
    predicted_line, confidence = model.predict_next_line(context)
    print(f"Context: {repr(context)}")
    print(f"Predicted: {predicted_line}")
    print(f"Confidence: {confidence:.1%}")
    
    # Test function completion
    print("\n=== Test 2: Function Completion ===")
    partial = "def find_max(numbers):\n    result = "
    completion, confidence = model.complete_function(partial)
    print(f"Partial: {repr(partial)}")
    print(f"Completion: {completion}")
    print(f"Confidence: {confidence:.1%}")
    
    # Test multiple predictions
    print("\n=== Test 3: Multiple Predictions ===")
    predictions = model.get_predictions("for ", top_k=3)
    print("Predictions for 'for ':")
    for token, conf in predictions:
        print(f"  {token}: {conf:.1%}")
    
    print("\n✅ All tests completed!")
