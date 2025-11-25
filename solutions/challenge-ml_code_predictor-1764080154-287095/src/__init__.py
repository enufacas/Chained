"""
Code Completion Predictor Package

A lightweight ML model that predicts code completions based on context.
Created by @create-guru with Tesla-inspired visionary design.

Challenge ID: challenge-ml_code_predictor-1764080154-287095
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
__author__ = '@create-guru'
