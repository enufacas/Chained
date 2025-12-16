"""
Code Completion Predictor Package

A lightweight ML-based code completion system by @create-botter.

Challenge ID: challenge-ml_code_predictor-1765894773-622314
"""

from .code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor,
    train_model
)

__all__ = [
    'CodeTokenizer',
    'SequencePredictor',
    'CodeCompletionPredictor',
    'train_model'
]

__version__ = '1.0.0'
__author__ = '@create-botter'
__challenge_id__ = 'challenge-ml_code_predictor-1765894773-622314'
