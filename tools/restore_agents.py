import os
import shutil

ARCHIVE_DIR = '.github/agents/archive'
AGENTS_DIR = '.github/agents'

RESTORATION_MAP = {
    'investigate-champion.md': 'bug-hunter.md',
    'guide-wizard.md': 'code-poet.md',
    'document-ninja.md': 'doc-master.md',
    'cloud-architect.md': 'feature-architect.md',
    'integrate-specialist.md': 'integration-specialist.md',
    'optimizer-architect.md': 'performance-optimizer.md',
    'refactor-champion.md': 'refactor-wizard.md',
    'secure-ninja.md': 'security-guardian.md',
    'mentor-ace.md': 'teach-wizard.md',
    'assert-specialist.md': 'test-champion.md',
    'designer-chief.md': 'ux-enhancer.md',
    'validator-pro.md': 'validate-pro.md',
    'validator-specialist.md': 'validate-wizard.md',
    'infrastructure-specialist.md': 'infrastructure-specialist.md' # Keeping this one as it seemed standard
}

def restore():
    count = 0
    for src_name, dst_name in RESTORATION_MAP.items():
        src_path = os.path.join(ARCHIVE_DIR, src_name)
        dst_path = os.path.join(AGENTS_DIR, dst_name)
        
        if os.path.exists(src_path):
            print(f"Restoring {src_name} -> {dst_name}")
            shutil.move(src_path, dst_path)
            count += 1
        else:
            print(f"Warning: Source {src_name} not found in archive.")

    print(f"Restored {count} agents.")

if __name__ == '__main__':
    restore()
