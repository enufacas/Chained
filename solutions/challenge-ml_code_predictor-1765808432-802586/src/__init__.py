"""
Code Completion Predictor - Lightweight ML for code prediction

Created by @create-botter for the Chained autonomous AI ecosystem.
Inspired by Nikola Tesla's visionary approach to innovation.
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
