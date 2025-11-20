"""
Code Completion Predictor Package

A lightweight ML model for code completion predictions.

Usage:
    from src.code_completion_predictor import train_model
    
    model = train_model(['def foo(): return 42'], 'python')
    line, conf = model.predict_next_line('def bar(): ')
    print(f"{line} ({conf:.0%})")
"""

from .code_completion_predictor import (
    CodeCompletionPredictor,
    CodeTokenizer,
    SequencePredictor,
    train_model
)

__version__ = '1.0.0'
__author__ = '@docs-tech-lead'

__all__ = [
    'CodeCompletionPredictor',
    'CodeTokenizer',
    'SequencePredictor',
    'train_model'
]
