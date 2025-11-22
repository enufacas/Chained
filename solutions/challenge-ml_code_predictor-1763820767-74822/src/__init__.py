"""
Code Completion Predictor Package

A lightweight ML-powered code completion system by @create-guru.
"""

from .code_completion_predictor import (
    CodeCompletionPredictor,
    CodeTokenizer,
    SequencePredictor,
    train_model
)

__all__ = [
    'CodeCompletionPredictor',
    'CodeTokenizer',
    'SequencePredictor',
    'train_model'
]

__version__ = '1.0.0'
__author__ = '@create-guru'
