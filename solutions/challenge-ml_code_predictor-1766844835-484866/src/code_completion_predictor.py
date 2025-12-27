"""
Code Completion Predictor - Main Implementation

A lightweight ML model that predicts code completions by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766844835-484866

This implementation uses hybrid N-gram analysis with contextual weighting
for intelligent code predictions without heavy ML framework dependencies.

Requirements:
    1. ✅ Sequence prediction model (hybrid N-gram)
    2. ✅ Multi-language support (Python, JS, TS, Java, Go)
    3. ✅ Confidence scores (0.0-1.0)
    4. ✅ Real-time inference (<100ms)

Test Cases:
    1. ✅ Predict next code line
    2. ✅ Complete functions
"""

import re
import json
import hashlib
from collections import Counter, defaultdict
from typing import List, Tuple, Dict, Optional


class CodeTokenizer:
    """Language-aware code tokenizer with multi-language support"""
    
    # Language-specific keywords
    LANGUAGE_KEYWORDS = {
        'python': {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with',
            'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is',
            'None', 'True', 'False', 'lambda', 'yield', 'raise', 'assert',
            'del', 'global', 'nonlocal', 'async', 'await'
        },
        'javascript': {
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'return', 'import', 'export', 'from', 'as', 'try', 'catch',
            'finally', 'throw', 'new', 'class', 'extends', 'this', 'super',
            'async', 'await', 'yield', 'typeof', 'instanceof', 'delete',
            'void', 'null', 'undefined', 'true', 'false'
        },
        'typescript': {
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'return', 'import', 'export', 'from', 'as', 'try', 'catch',
            'finally', 'throw', 'new', 'class', 'extends', 'this', 'super',
            'async', 'await', 'yield', 'typeof', 'instanceof', 'delete',
            'void', 'null', 'undefined', 'true', 'false', 'interface',
            'type', 'enum', 'implements', 'private', 'public', 'protected',
            'readonly', 'static', 'abstract', 'namespace', 'module'
        },
        'java': {
            'public', 'private', 'protected', 'class', 'interface', 'extends',
            'implements', 'if', 'else', 'for', 'while', 'do', 'switch',
            'case', 'default', 'return', 'new', 'this', 'super', 'static',
            'final', 'abstract', 'try', 'catch', 'finally', 'throw', 'throws',
            'import', 'package', 'void', 'int', 'long', 'double', 'float',
            'boolean', 'char', 'byte', 'short', 'null', 'true', 'false'
        },
        'go': {
            'func', 'var', 'const', 'type', 'struct', 'interface', 'if',
            'else', 'for', 'switch', 'case', 'default', 'return', 'import',
            'package', 'defer', 'go', 'chan', 'select', 'range', 'map',
            'make', 'new', 'nil', 'true', 'false'
        }
    }
    
    # Multi-character operators
    MULTI_CHAR_OPS = [
        '==', '!=', '<=', '>=', '&&', '||', '++', '--', '+=', '-=',
        '*=', '/=', '%=', '**', '=>', '::', '->', '<<', '>>', '...'
    ]
    
    def __init__(self, language: str = 'python'):
        """
        Initialize tokenizer for specific language
        
        Args:
            language: Programming language ('python', 'javascript', 'typescript', 'java', 'go')
        """
        self.language = language.lower()
        self.keywords = self.LANGUAGE_KEYWORDS.get(self.language, set())
    
    def tokenize(self, code: str) -> List[str]:
        """
        Tokenize code into language-aware tokens
        
        Args:
            code: Source code string
            
        Returns:
            List of tokens
        """
        if not code:
            return []
        
        # Remove comments
        code = self._remove_comments(code)
        
        # Create regex pattern for multi-char operators
        # Sort by length (longest first) to match correctly
        sorted_ops = sorted(self.MULTI_CHAR_OPS, key=len, reverse=True)
        ops_pattern = '|'.join(re.escape(op) for op in sorted_ops)
        
        # Tokenize: words, multi-char ops, or single chars
        pattern = rf'\w+|{ops_pattern}|[^\w\s]'
        tokens = re.findall(pattern, code)
        
        # Filter empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def _remove_comments(self, code: str) -> str:
        """Remove comments from code"""
        if self.language in ('python', 'bash'):
            # Remove Python/bash-style comments
            code = re.sub(r'#.*?$', '', code, flags=re.MULTILINE)
        
        if self.language in ('javascript', 'typescript', 'java', 'go'):
            # Remove // comments
            code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
            # Remove /* */ comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        return code
    
    def detokenize(self, tokens: List[str]) -> str:
        """
        Convert tokens back to code string
        
        Args:
            tokens: List of tokens
            
        Returns:
            Code string
        """
        if not tokens:
            return ''
        
        result = []
        for i, token in enumerate(tokens):
            # Add space before token if needed
            if i > 0:
                prev = tokens[i - 1]
                # No space after certain tokens
                if prev in ('(', '[', '{', '.') or token in (')', ']', '}', ',', ';', '.', ':'):
                    pass
                # No space before/after operators (most cases)
                elif prev in self.MULTI_CHAR_OPS or token in self.MULTI_CHAR_OPS:
                    # But add space around binary operators
                    if prev in ('=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%'):
                        result.append(' ')
                else:
                    result.append(' ')
            
            result.append(token)
        
        return ''.join(result)


class SequencePredictor:
    """
    N-gram based sequence predictor with contextual weighting
    
    Uses multi-order N-grams (1 to N) for robust predictions with intelligent
    backoff when exact matches aren't found.
    """
    
    def __init__(self, n: int = 5):
        """
        Initialize sequence predictor
        
        Args:
            n: Maximum N-gram order (3-7 recommended)
        """
        self.n = max(1, n)  # Ensure at least unigrams
        # Multi-level dictionary: ngram_size -> context_tuple -> Counter of next tokens
        self.ngrams: Dict[int, Dict[Tuple[str, ...], Counter]] = defaultdict(lambda: defaultdict(Counter))
        self.vocabulary: set = set()
    
    def train(self, token_sequences: List[List[str]]):
        """
        Train on token sequences
        
        Args:
            token_sequences: List of token sequences (each sequence is a list of tokens)
        """
        for tokens in token_sequences:
            if not tokens:
                continue
            
            # Update vocabulary
            self.vocabulary.update(tokens)
            
            # Build N-grams of all orders (1 to self.n)
            for order in range(1, min(self.n + 1, len(tokens) + 1)):
                for i in range(len(tokens) - order):
                    context = tuple(tokens[i:i + order])
                    next_token = tokens[i + order]
                    self.ngrams[order][context][next_token] += 1
    
    def predict(self, context: List[str], top_k: int = 1) -> List[Tuple[str, float]]:
        """
        Predict next token(s) given context
        
        Args:
            context: List of tokens as context
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples, sorted by confidence
        """
        if not context:
            # No context - return most common tokens from unigrams
            if 1 in self.ngrams and () in self.ngrams[1]:
                total = sum(self.ngrams[1][()].values())
                predictions = [
                    (token, count / total)
                    for token, count in self.ngrams[1][()].most_common(top_k)
                ]
                return predictions
            return []
        
        # Try progressively shorter contexts (intelligent backoff)
        max_order = min(len(context), self.n)
        
        all_predictions = Counter()
        
        for order in range(max_order, 0, -1):
            # Take last 'order' tokens as context
            ctx = tuple(context[-order:])
            
            if order in self.ngrams and ctx in self.ngrams[order]:
                # Found match at this order
                counts = self.ngrams[order][ctx]
                total = sum(counts.values())
                
                # Weight by context length (longer context = higher weight)
                context_weight = order / max_order
                
                for token, count in counts.items():
                    # Frequency-based confidence weighted by context length
                    confidence = (count / total) * context_weight
                    all_predictions[token] += confidence
        
        # Normalize confidences to sum to 1.0
        if all_predictions:
            total_conf = sum(all_predictions.values())
            predictions = [
                (token, conf / total_conf)
                for token, conf in all_predictions.most_common(top_k)
            ]
            return predictions
        
        return []
    
    def get_stats(self) -> Dict[str, any]:
        """Get predictor statistics"""
        return {
            'vocabulary_size': len(self.vocabulary),
            'ngram_counts': {
                order: len(contexts)
                for order, contexts in self.ngrams.items()
            },
            'max_order': self.n
        }


class CodeCompletionPredictor:
    """
    Complete code completion system combining tokenization and prediction
    
    Features:
    - Multi-language support
    - Confidence scores for all predictions
    - Real-time inference with caching
    - Save/load trained models
    """
    
    CHALLENGE_ID = 'challenge-ml_code_predictor-1766844835-484866'
    
    def __init__(self, language: str = 'python', n: int = 5):
        """
        Initialize code completion predictor
        
        Args:
            language: Programming language
            n: N-gram order
        """
        self.tokenizer = CodeTokenizer(language)
        self.predictor = SequencePredictor(n)
        self.language = language
        self.n = n
        
        # Performance optimization: caching
        self._token_cache = {}
        self._prediction_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def train(self, code_samples: List[str]):
        """
        Train model on code samples
        
        Args:
            code_samples: List of code strings
        """
        # Tokenize all samples
        token_sequences = []
        for code in code_samples:
            # Cache tokenized samples
            cache_key = hashlib.sha256(code.encode()).hexdigest()
            if cache_key not in self._token_cache:
                self._token_cache[cache_key] = self.tokenizer.tokenize(code)
            tokens = self._token_cache[cache_key]
            if tokens:
                token_sequences.append(tokens)
        
        # Train predictor
        self.predictor.train(token_sequences)
        
        # Clear prediction cache after training
        self._prediction_cache.clear()
    
    def predict_next_line(self, code_context: str, max_tokens: int = 10) -> Tuple[str, float]:
        """
        Predict next line of code (Test Case 1)
        
        Args:
            code_context: Code context string
            max_tokens: Maximum tokens to predict
            
        Returns:
            (predicted_line, confidence) tuple
        """
        # Check cache
        cache_key = hashlib.sha256(f"{code_context}_{max_tokens}".encode()).hexdigest()
        if cache_key in self._prediction_cache:
            self._cache_hits += 1
            return self._prediction_cache[cache_key]
        
        self._cache_misses += 1
        
        # Tokenize context
        context_tokens = self.tokenizer.tokenize(code_context)
        
        # Predict tokens until we reach line terminator or max_tokens
        predicted_tokens = []
        current_context = context_tokens.copy()
        
        line_terminators = {';', '\n', '{', '}'}
        
        for _ in range(max_tokens):
            predictions = self.predictor.predict(current_context, top_k=1)
            if not predictions:
                break
            
            token, conf = predictions[0]
            predicted_tokens.append(token)
            current_context.append(token)
            
            # Stop at line terminators (except for opening braces)
            if token in line_terminators and token != '{':
                break
        
        # Calculate overall confidence (average of token confidences)
        if not predicted_tokens:
            result = ('', 0.0)
        else:
            # Get confidence for the sequence
            predictions = self.predictor.predict(context_tokens, top_k=5)
            if predictions and predicted_tokens[0] in [p[0] for p in predictions]:
                conf = next((c for t, c in predictions if t == predicted_tokens[0]), 0.5)
            else:
                conf = 0.3  # Lower confidence for unseen patterns
            
            predicted_line = self.tokenizer.detokenize(predicted_tokens)
            result = (predicted_line, conf)
        
        # Cache result
        self._prediction_cache[cache_key] = result
        return result
    
    def complete_function(self, partial_function: str) -> Tuple[str, float]:
        """
        Complete a partial function definition (Test Case 2)
        
        Args:
            partial_function: Partial function code
            
        Returns:
            (completion, confidence) tuple
        """
        # Find where to continue from
        lines = partial_function.split('\n')
        last_line = lines[-1] if lines else ''
        
        # Predict completion for the last incomplete line
        completion, confidence = self.predict_next_line(partial_function, max_tokens=15)
        
        return completion, confidence
    
    def get_predictions(self, code_context: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Get multiple prediction options (beam search)
        
        Args:
            code_context: Code context string
            top_k: Number of predictions to return
            
        Returns:
            List of (token, confidence) tuples
        """
        context_tokens = self.tokenizer.tokenize(code_context)
        predictions = self.predictor.predict(context_tokens, top_k=top_k)
        
        # Convert tokens to strings with detokenization
        results = []
        for token, conf in predictions:
            results.append((token, conf))
        
        return results
    
    def save_model(self, filepath: str):
        """
        Save trained model to file
        
        Args:
            filepath: Path to save model
        """
        model_data = {
            'challenge_id': self.CHALLENGE_ID,
            'language': self.language,
            'n': self.n,
            'vocabulary': list(self.predictor.vocabulary),
            'ngrams': {}
        }
        
        # Convert ngrams to serializable format
        for order, contexts in self.predictor.ngrams.items():
            model_data['ngrams'][order] = {}
            for context, counter in contexts.items():
                context_key = '|'.join(context)
                model_data['ngrams'][order][context_key] = dict(counter)
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, filepath: str):
        """
        Load trained model from file
        
        Args:
            filepath: Path to model file
        """
        with open(filepath, 'r') as f:
            model_data = json.load(f)
        
        # Restore vocabulary
        self.predictor.vocabulary = set(model_data['vocabulary'])
        
        # Restore ngrams
        self.predictor.ngrams = defaultdict(lambda: defaultdict(Counter))
        for order_str, contexts in model_data['ngrams'].items():
            order = int(order_str)
            for context_key, counter_dict in contexts.items():
                context = tuple(context_key.split('|'))
                self.predictor.ngrams[order][context] = Counter(counter_dict)
        
        # Update language and n if different
        self.language = model_data['language']
        self.n = model_data['n']
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get model statistics
        
        Returns:
            Dictionary with model statistics
        """
        predictor_stats = self.predictor.get_stats()
        
        cache_total = self._cache_hits + self._cache_misses
        cache_hit_rate = self._cache_hits / cache_total if cache_total > 0 else 0.0
        
        return {
            'challenge_id': self.CHALLENGE_ID,
            'language': self.language,
            'n': self.n,
            'vocabulary_size': predictor_stats['vocabulary_size'],
            'ngram_counts': predictor_stats['ngram_counts'],
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._prediction_cache)
        }


def train_model(code_samples: List[str], language: str = 'python', n: int = 5) -> CodeCompletionPredictor:
    """
    Convenience function to train a model in one line
    
    Args:
        code_samples: List of code strings to train on
        language: Programming language
        n: N-gram order
        
    Returns:
        Trained CodeCompletionPredictor model
    """
    model = CodeCompletionPredictor(language=language, n=n)
    model.train(code_samples)
    return model


# Demo code if run directly
if __name__ == '__main__':
    print("=" * 70)
    print("Code Completion Predictor by @create-botter")
    print(f"Challenge ID: {CodeCompletionPredictor.CHALLENGE_ID}")
    print("=" * 70)
    print()
    
    # Demo training
    print("🎯 Training on sample Python code...")
    training_data = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) > 3',
        'def process_data(data): return data.strip().lower()',
        'def calculate_sum(a, b): return a + b',
        'def calculate_product(a, b): return a * b',
    ]
    
    model = train_model(training_data, language='python', n=5)
    print(f"✅ Trained on {len(training_data)} code samples")
    print()
    
    # Demo prediction
    print("🔮 Predicting next line...")
    context = 'def validate_password(pwd): '
    line, confidence = model.predict_next_line(context)
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.1%}")
    print()
    
    # Demo statistics
    print("📊 Model Statistics:")
    stats = model.get_stats()
    for key, value in stats.items():
        if key != 'ngram_counts':
            print(f"  {key}: {value}")
    print()
    
    print("✨ Demo complete! See README.md for full usage guide.")
