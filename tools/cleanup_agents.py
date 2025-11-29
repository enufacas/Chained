import os
import shutil

AGENTS_DIR = '.github/agents'
ARCHIVE_DIR = os.path.join(AGENTS_DIR, 'archive')

CORE_AGENTS = {
    'a2a-coordinator.md',
    'bug-hunter.md',
    'code-poet.md',
    'coordinate-wizard.md',
    'create-guru.md',
    'doc-master.md',
    'engineer-master.md',
    'engineer-wizard.md',
    'feature-architect.md',
    'integration-specialist.md',
    'meta-coordinator-system.md',
    'performance-optimizer.md',
    'refactor-wizard.md',
    'security-guardian.md',
    'teach-wizard.md',
    'test-champion.md',
    'troubleshoot-expert.md',
    'ux-enhancer.md',
    'validate-pro.md',
    'validate-wizard.md'
}

def cleanup():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    files = [f for f in os.listdir(AGENTS_DIR) if f.endswith('.md') and f != 'README.md']
    
    moved_count = 0
    for f in files:
        if f not in CORE_AGENTS:
            src = os.path.join(AGENTS_DIR, f)
            dst = os.path.join(ARCHIVE_DIR, f)
            print(f"Archiving {f}...")
            shutil.move(src, dst)
            moved_count += 1
    
    print(f"Moved {moved_count} agents to archive.")

if __name__ == '__main__':
    cleanup()
