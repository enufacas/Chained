import os

ARCHIVE_DIR = '.github/agents/archive'
SEARCH_TERMS = [
    'bug', 'hunt', 'investigate', 
    'poet', 'write', 'code',
    'feature', 'architect',
    'perform', 'optimiz', 'accelerat',
    'teach', 'mentor', 'guide',
    'ux', 'design',
    'test', 'assert', 'verify',
    'validate', 'validator'
]

def search():
    files = os.listdir(ARCHIVE_DIR)
    for term in SEARCH_TERMS:
        matches = [f for f in files if term in f]
        if matches:
            print(f"Matches for '{term}': {matches}")

if __name__ == '__main__':
    search()
