#!/usr/bin/env python3
"""
Code Completion Predictor - A lightweight ML model for code prediction

This module implements a sequence-based code completion predictor inspired by
GitHub Copilot, using a visionary LSTM-inspired architecture optimized for
real-time inference.

Created by @create-botter - Visionary infrastructure with Tesla-inspired innovation.
Part of the Chained autonomous AI ecosystem.

Architecture:
1. Custom code tokenizer supporting multiple languages
2. N-gram based sequence model with learned patterns
3. Confidence scoring using probabilistic predictions
4. Real-time inference optimization with caching
5. Beam search for multiple completion candidates

Features:
- Multi-language support (Python, JavaScript, Java, C++, Go)
- Confidence scores for predictions
- Beam search for better completions
- Real-time inference (<100ms target)
- Minimal dependencies (no TensorFlow/PyTorch required)
- Model persistence for save/load
"""

import re
import json
import pickle
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path
import math
from functools import lru_cache


class CodeTokenizer:
    """
    Custom tokenizer for code that handles multiple programming languages.
    
    Tokenization strategy inspired by compiler design:
    - Preserves keywords, operators, and identifiers
    - Handles language-specific syntax
    - Maintains context for semantic understanding
    - Optimized for code completion tasks
    """
    
    # Comprehensive programming keywords across languages
    KEYWORDS = {
        'python': {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return', 
            'import', 'from', 'try', 'except', 'with', 'as', 'lambda', 'yield',
            'async', 'await', 'pass', 'break', 'continue', 'raise', 'finally',
            'in', 'is', 'not', 'and', 'or', 'True', 'False', 'None'
        },
        'javascript': {
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'return', 'import', 'from', 'export', 'class', 'async', 'await',
            'try', 'catch', 'finally', 'throw', 'new', 'this', 'super',
            'extends', 'static', 'get', 'set', 'typeof', 'instanceof',
            'null', 'undefined', 'true', 'false'
        },
        'java': {
            'public', 'private', 'protected', 'class', 'interface', 'extends',
            'implements', 'if', 'else', 'for', 'while', 'return', 'import',
            'try', 'catch', 'finally', 'throw', 'throws', 'new', 'this', 'super',
            'static', 'void', 'int', 'String', 'boolean', 'double', 'float',
            'long', 'short', 'byte', 'char', 'true', 'false', 'null',
            'abstract', 'final', 'synchronized', 'volatile', 'transient'
        },
        'cpp': {
            'class', 'struct', 'namespace', 'using', 'if', 'else', 'for',
            'while', 'return', 'include', 'try', 'catch', 'throw', 'new',
            'delete', 'this', 'public', 'private', 'protected', 'virtual',
            'static', 'const', 'void', 'int', 'double', 'float', 'char',
            'bool', 'true', 'false', 'nullptr', 'auto', 'template'
        },
        'go': {
            'func', 'package', 'import', 'if', 'else', 'for', 'range',
            'return', 'var', 'const', 'type', 'struct', 'interface',
            'defer', 'go', 'chan', 'select', 'case', 'default', 'switch',
            'break', 'continue', 'fallthrough', 'true', 'false', 'nil'
        }
    }
    
    # Token patterns using regex
    PATTERNS = {
        'identifier': r'[a-zA-Z_][a-zA-Z0-9_]*',
        'number': r'\d+\.?\d*[eE]?[+-]?\d*',
        'string': r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
        'operator': r'[+\-*/%=<>!&|^~]+',
        'delimiter': r'[(){}\[\],;:.]',
        'whitespace': r'\s+',
        'comment': r'//.*?$|/\*.*?\*/|#.*?$'
    }
    
    def __init__(self, language: str = 'python'):
        """
        Initialize tokenizer for specific language.
        
        Args:
            language: Programming language ('python', 'javascript', 'java', 'cpp', 'go')
        """
        self.language = language.lower()
        self.keywords = self.KEYWORDS.get(self.language, set())
        
        # Compile regex patterns for efficiency
        self.token_pattern = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.PATTERNS.items()),
            re.MULTILINE
        )
    
    def tokenize(self, code: str) -> List[str]:
        """
        Tokenize code into meaningful tokens.
        
        Args:
            code: Source code string
            
        Returns:
            List of tokens with special markers for keywords/newlines
        """
        tokens = []
        
        for match in self.token_pattern.finditer(code):
            kind = match.lastgroup
            value = match.group()
            
            if kind == 'whitespace':
                # Preserve significant whitespace (newlines for context)
                if '\n' in value:
                    tokens.append('<NEWLINE>')
            elif kind == 'comment':
                # Keep comments as context markers
                tokens.append('<COMMENT>')
            elif kind == 'identifier':
                # Mark keywords specially for better pattern recognition
                if value in self.keywords:
                    tokens.append(f'<KEYWORD:{value}>')
                else:
                    tokens.append(value)
            elif kind == 'string':
                # Normalize strings to preserve structure
                tokens.append('<STRING>')
            elif kind == 'number':
                # Normalize numbers
                tokens.append('<NUMBER>')
            else:
                # Operators and delimiters
                tokens.append(value)
        
        return tokens
    
    def detokenize(self, tokens: List[str]) -> str:
        """
        Convert tokens back to code (approximate reconstruction).
        
        Args:
            tokens: List of tokens
            
        Returns:
            Reconstructed code string
        """
        code = []
        for token in tokens:
            if token == '<NEWLINE>':
                code.append('\n')
            elif token == '<COMMENT>':
                code.append('# comment')
            elif token == '<STRING>':
                code.append('""')
            elif token == '<NUMBER>':
                code.append('0')
            elif token.startswith('<KEYWORD:'):
                # Extract keyword from marker
                keyword = token[9:-1]
                code.append(keyword)
            else:
                code.append(token)
        
        return ' '.join(code)


class SequencePredictor:
    """
    N-gram based sequence predictor with learned patterns.
    
    This implements a lightweight alternative to LSTM/Transformer models,
    using statistical methods for real-time inference. Inspired by classic
    NLP n-gram models but optimized for code structure.
    """
    
    def __init__(self, n: int = 3, max_vocab_size: int = 10000):
        """
        Initialize the sequence predictor.
        
        Args:
            n: N-gram size (context window)
            max_vocab_size: Maximum vocabulary size for efficiency
        """
        self.n = n
        self.max_vocab_size = max_vocab_size
        
        # N-gram frequency counts: (context) -> {next_token: count}
        self.ngrams: Dict[Tuple, Counter] = defaultdict(Counter)
        
        # Vocabulary for tracking token frequencies
        self.vocab: Counter = Counter()
        
        # Cache for performance
        self._prediction_cache = {}
    
    def train(self, token_sequences: List[List[str]]) -> None:
        """
        Train the model on tokenized code sequences.
        
        Args:
            token_sequences: List of token sequences from training code
        """
        # Build vocabulary
        for tokens in token_sequences:
            self.vocab.update(tokens)
        
        # Limit vocabulary to most frequent tokens
        if len(self.vocab) > self.max_vocab_size:
            most_common = dict(self.vocab.most_common(self.max_vocab_size))
            self.vocab = Counter(most_common)
        
        # Build n-grams
        for tokens in token_sequences:
            for i in range(len(tokens) - self.n):
                context = tuple(tokens[i:i + self.n])
                next_token = tokens[i + self.n]
                
                # Only track if token in vocabulary
                if next_token in self.vocab:
                    self.ngrams[context][next_token] += 1
        
        # Clear cache after training
        self._prediction_cache.clear()
    
    @lru_cache(maxsize=1000)
    def predict_next(
        self,
        context: Tuple[str, ...],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Predict next token given context with confidence scores.
        
        Args:
            context: Tuple of recent tokens (context window)
            top_k: Number of top predictions to return
            
        Returns:
            List of (token, confidence) tuples sorted by confidence
        """
        # Ensure context is proper length
        context = tuple(context[-self.n:])
        
        # Try full context first
        predictions = self.ngrams.get(context, Counter())
        
        # Backoff to shorter context if no matches
        if not predictions and len(context) > 1:
            for i in range(1, len(context)):
                short_context = context[i:]
                predictions = self.ngrams.get(short_context, Counter())
                if predictions:
                    break
        
        if not predictions:
            # Fall back to most common tokens
            predictions = self.vocab
        
        # Calculate probabilities
        total = sum(predictions.values())
        if total == 0:
            return []
        
        results = [
            (token, count / total)
            for token, count in predictions.most_common(top_k)
        ]
        
        return results
    
    def beam_search(
        self,
        context: List[str],
        num_tokens: int = 1,
        beam_width: int = 3
    ) -> List[Tuple[List[str], float]]:
        """
        Generate multiple completion candidates using beam search.
        
        Args:
            context: Initial context tokens
            num_tokens: Number of tokens to generate
            beam_width: Number of candidates to maintain
            
        Returns:
            List of (token_sequence, cumulative_confidence) tuples
        """
        # Initialize with context
        beams = [(context.copy(), 1.0)]
        
        for _ in range(num_tokens):
            candidates = []
            
            for sequence, score in beams:
                # Get next token predictions
                ctx = tuple(sequence[-self.n:])
                predictions = self.predict_next(ctx, top_k=beam_width)
                
                for token, prob in predictions:
                    new_seq = sequence + [token]
                    new_score = score * prob
                    candidates.append((new_seq, new_score))
            
            # Keep top beam_width candidates
            beams = sorted(candidates, key=lambda x: x[1], reverse=True)[:beam_width]
        
        return beams
    
    def save(self, path: Path) -> None:
        """Save model to disk."""
        with open(path, 'wb') as f:
            pickle.dump({
                'n': self.n,
                'max_vocab_size': self.max_vocab_size,
                'ngrams': dict(self.ngrams),
                'vocab': dict(self.vocab)
            }, f)
    
    def load(self, path: Path) -> None:
        """Load model from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.n = data['n']
            self.max_vocab_size = data['max_vocab_size']
            self.ngrams = defaultdict(Counter, {
                k: Counter(v) for k, v in data['ngrams'].items()
            })
            self.vocab = Counter(data['vocab'])
        
        self._prediction_cache.clear()


class CodeCompletionPredictor:
    """
    Main interface for code completion prediction.
    
    Combines tokenizer and sequence predictor with optimizations
    for real-time inference and caching.
    """
    
    def __init__(
        self,
        language: str = 'python',
        n: int = 3,
        max_vocab_size: int = 10000
    ):
        """
        Initialize the code completion predictor.
        
        Args:
            language: Programming language
            n: N-gram size for context
            max_vocab_size: Maximum vocabulary size
        """
        self.tokenizer = CodeTokenizer(language)
        self.predictor = SequencePredictor(n, max_vocab_size)
        self.language = language
        
        # Performance cache
        self._completion_cache = {}
    
    def train(self, code_samples: List[str]) -> None:
        """
        Train the model on code samples.
        
        Args:
            code_samples: List of code strings for training
        """
        # Tokenize all samples
        token_sequences = [
            self.tokenizer.tokenize(code)
            for code in code_samples
        ]
        
        # Train predictor
        self.predictor.train(token_sequences)
        
        # Clear cache
        self._completion_cache.clear()
    
    def predict_next_line(
        self,
        code_context: str,
        num_predictions: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Predict the next line of code with confidence scores.
        
        Args:
            code_context: Previous lines of code for context
            num_predictions: Number of predictions to return
            
        Returns:
            List of (predicted_line, confidence) tuples
        """
        # Check cache
        cache_key = (code_context, num_predictions)
        if cache_key in self._completion_cache:
            return self._completion_cache[cache_key]
        
        # Tokenize context
        tokens = self.tokenizer.tokenize(code_context)
        
        # If very few tokens, just predict next tokens directly
        if len(tokens) < self.predictor.n:
            # Use simple prediction for short contexts
            ctx = tuple(tokens[-self.predictor.n:]) if tokens else ()
            predictions = self.predictor.predict_next(ctx, top_k=num_predictions * 2)
            
            results = []
            for token, confidence in predictions[:num_predictions]:
                # Create simple one-token predictions
                line = self.tokenizer.detokenize([token])
                results.append((line, confidence))
            
            self._completion_cache[cache_key] = results
            return results
        
        # Use beam search to generate line completions
        beams = self.predictor.beam_search(
            tokens,
            num_tokens=10,  # Generate up to 10 tokens
            beam_width=num_predictions * 2
        )
        
        # Convert token sequences to code lines
        results = []
        seen_lines = set()
        
        for sequence, score in beams:
            # Extract new tokens (after context)
            new_tokens = sequence[len(tokens):]
            
            # Stop at newline or take all tokens
            line_tokens = []
            for token in new_tokens:
                if token == '<NEWLINE>':
                    break
                line_tokens.append(token)
            
            if line_tokens:
                # Detokenize
                line = self.tokenizer.detokenize(line_tokens)
                
                # Avoid duplicates
                if line not in seen_lines:
                    results.append((line, score))
                    seen_lines.add(line)
                
                if len(results) >= num_predictions:
                    break
        
        # If no results from beam search, try simple prediction
        if not results:
            ctx = tuple(tokens[-self.predictor.n:])
            predictions = self.predictor.predict_next(ctx, top_k=num_predictions)
            for token, confidence in predictions:
                line = self.tokenizer.detokenize([token])
                results.append((line, confidence))
        
        # Cache result
        self._completion_cache[cache_key] = results
        
        return results
    
    def complete_function(
        self,
        partial_function: str,
        num_completions: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Complete a partial function definition.
        
        Args:
            partial_function: Incomplete function code
            num_completions: Number of completions to generate
            
        Returns:
            List of (completion, confidence) tuples
        """
        # Use predict_next_line but generate more tokens
        tokens = self.tokenizer.tokenize(partial_function)
        
        beams = self.predictor.beam_search(
            tokens,
            num_tokens=20,  # Generate more tokens for function body
            beam_width=num_completions * 2
        )
        
        results = []
        for sequence, score in beams:
            new_tokens = sequence[len(tokens):]
            completion = self.tokenizer.detokenize(new_tokens)
            results.append((completion, score))
            
            if len(results) >= num_completions:
                break
        
        return results
    
    def save(self, path: Path) -> None:
        """Save model to disk."""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save predictor
        self.predictor.save(save_path)
        
        # Save metadata
        meta_path = save_path.with_suffix('.json')
        with open(meta_path, 'w') as f:
            json.dump({
                'language': self.language,
                'n': self.predictor.n,
                'max_vocab_size': self.predictor.max_vocab_size,
                'vocab_size': len(self.predictor.vocab)
            }, f, indent=2)
    
    def load(self, path: Path) -> None:
        """Load model from disk."""
        load_path = Path(path)
        
        # Load predictor
        self.predictor.load(load_path)
        
        # Load metadata
        meta_path = load_path.with_suffix('.json')
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                self.language = meta.get('language', self.language)
        
        # Clear caches
        self._completion_cache.clear()


def train_model(
    code_samples: List[str],
    language: str = 'python',
    n: int = 3,
    max_vocab_size: int = 10000
) -> CodeCompletionPredictor:
    """
    Convenience function to train a new model.
    
    Args:
        code_samples: List of code strings for training
        language: Programming language
        n: N-gram size
        max_vocab_size: Maximum vocabulary size
        
    Returns:
        Trained CodeCompletionPredictor instance
    """
    model = CodeCompletionPredictor(language, n, max_vocab_size)
    model.train(code_samples)
    return model
