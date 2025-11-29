import os

ARCHIVE_DIR = '.github/agents/archive'
KEYWORDS = {
    'bug': 'bug-hunter',
    'poet': 'code-poet',
    'doc': 'doc-master',
    'feature': 'feature-architect',
    'integrate': 'integration-specialist',
    'perform': 'performance-optimizer',
    'refactor': 'refactor-wizard',
    'secur': 'security-guardian',
    'teach': 'teach-wizard',
    'test': 'test-champion',
    'ux': 'ux-enhancer',
    'validate': 'validate-pro',
    'validator': 'validate-wizard' # ambiguous
}

def find_candidates():
    files = os.listdir(ARCHIVE_DIR)
    candidates = {}
    
    for k, target in KEYWORDS.items():
        candidates[target] = []
        for f in files:
            if k in f:
                candidates[target].append(f)
    
    for target, matches in candidates.items():
        print(f"{target}: {matches}")

if __name__ == '__main__':
    find_candidates()
