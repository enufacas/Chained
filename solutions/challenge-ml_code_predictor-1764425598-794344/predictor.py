import re
import collections
import os

class CodePredictor:
    def __init__(self, n=4):
        """
        Initialize the N-gram predictor.
        :param n: The size of the n-gram (history + 1). 
                  e.g., n=3 means prediction depends on previous 2 tokens.
        """
        self.n = n
        self.model = collections.defaultdict(collections.Counter)
        self.vocabulary = set()


    def tokenize(self, text):
        """
        Tokenize code into words, symbols, and newlines.
        """
        # Matches words, or non-whitespace non-word sequences, or newlines.
        return re.findall(r"\w+|[^\s\w]|\n", text)


    def train(self, code):
        """
        Train the model on a string of code.
        """
        tokens = self.tokenize(code)
        self.vocabulary.update(tokens)
        
        for i in range(len(tokens) - self.n + 1):
            history = tuple(tokens[i:i+self.n-1])
            next_token = tokens[i+self.n-1]
            self.model[history][next_token] += 1


    def train_from_directory(self, directory, extensions=(".py", ".md", ".js", ".ts")):
        """
        Walk a directory and train on all matching files.
        """
        count = 0
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            self.train(f.read())
                            count += 1
                    except Exception:
                        pass # Ignore read errors
        return count


    def predict_next_token(self, context_tokens):
        """
        Predict the next token based on context tokens.
        Returns (token, confidence).
        """
        if not context_tokens:
            return None, 0.0
            
        # Backoff strategy: try N-1 context, then N-2, ...
        for k in range(self.n - 1, 0, -1):
            history = tuple(context_tokens[-k:])
            if history in self.model:
                candidates = self.model[history]
                total = sum(candidates.values())
                if total == 0: continue
                best_token, count = candidates.most_common(1)[0]
                return best_token, count / total
        
        return None, 0.0


    def predict_next_line(self, code_context):
        """
        Predict the next line of code.
        """
        tokens = self.tokenize(code_context)
        generated = []
        current_context = tokens[:]
        
        # Generate until newline or limit
        confidence_sum = 0
        steps = 0
        
        while len(generated) < 50: # Safety limit
            next_token, conf = self.predict_next_token(current_context)
            if not next_token:
                break
                
            generated.append(next_token)
            current_context.append(next_token)
            confidence_sum += conf
            steps += 1
            
            if next_token == "\n":
                break
        
        # Reconstruct string
        # Simple heuristic: join with spaces, but remove space before newline
        result = " ".join(generated).replace(" \n", "").strip()
        avg_conf = confidence_sum / steps if steps > 0 else 0.0
        
        return result, avg_conf


    def complete_function(self, partial_code):
        """
        Attempt to complete a function (generate multiple lines).
        """
        tokens = self.tokenize(partial_code)
        generated = []
        current_context = tokens[:]
        
        # Generate lines until we see a closing brace (heuristic) or limit
        for _ in range(10): # Max 10 lines
            line_tokens = []
            while len(line_tokens) < 20:
                next_token, _ = self.predict_next_token(current_context)
                if not next_token:
                    break
                line_tokens.append(next_token)
                current_context.append(next_token)
                if next_token == "\n":
                    break
            
            generated.extend(line_tokens)
            if not line_tokens:
                break
            
        return " ".join(generated).replace(" \n", "\n").strip()


if __name__ == "__main__":
    # Simple demo
    predictor = CodePredictor(n=3)
    
    # Train on itself
    with open(__file__, "r") as f:
        predictor.train(f.read())
        
    print("Training complete.")
    
    context = "def predict_"
    prediction, conf = predictor.predict_next_line(context)
    print(f"Context: {context}")
    print(f"Prediction: {prediction}")
    print(f"Confidence: {conf:.2f}")

