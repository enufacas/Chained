"""
Code Completion Predictor Package

A lightweight ML model for code completion by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766931267-134357

Main components:
    - CodeTokenizer: Language-aware code tokenization
    - SequencePredictor: N-gram based sequence prediction
    - CodeCompletionPredictor: Main interface with caching

Example:
    >>> from src.code_completion_predictor import CodeCompletionPredictor
    >>> model = CodeCompletionPredictor(language='python', n=5)
    >>> model.train(['def add(a, b): return a + b'])
    >>> line, conf = model.predict_next_line('def subtract(a, b): ')
    >>> print(f"{line} (confidence: {conf:.0%})")
"""

from .code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor
)

__version__ = '1.0.0'
__author__ = '@create-botter'
__challenge_id__ = 'challenge-ml_code_predictor-1766931267-134357'

__all__ = [
    'CodeTokenizer',
    'SequencePredictor',
    'CodeCompletionPredictor'
]
