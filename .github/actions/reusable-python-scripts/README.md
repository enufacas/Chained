# Python Script Executor Action

**Enhanced by @create-guru** ⚡

Execute Python scripts with automatic environment setup, dependency management, and comprehensive error handling.

## Features

- 🐍 **Flexible execution**: Inline code or script files
- 📦 **Auto setup**: Python environment configured automatically
- 🔧 **Dependencies**: Install from requirements.txt or list
- 🌍 **Environment vars**: Pass custom variables as JSON
- ⏱️ **Timeout handling**: Prevent runaway scripts
- 📝 **Output capture**: Separate stdout/stderr
- 📂 **Working directory**: Execute in specific location
- ⚠️ **Error handling**: Configurable failure behavior

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `script` | Python script path or inline code | Yes | - |
| `python-version` | Python version to use | No | `3.11` |
| `requirements` | Dependencies to install | No | - |
| `args` | Arguments to pass to script | No | - |
| `working-directory` | Working directory | No | `.` |
| `inline` | Whether script is inline code | No | `false` |
| `output-file` | Capture stdout to file | No | - |
| `env-vars` | Environment variables as JSON | No | - |
| `timeout` | Script timeout in seconds | No | `300` |
| `fail-on-error` | Exit on script failure | No | `true` |

## Outputs

| Output | Description |
|--------|-------------|
| `stdout` | Script standard output |
| `stderr` | Script standard error |
| `exit-code` | Script exit code |
| `success` | Whether script succeeded |

## Usage Examples

### Execute Inline Python
```yaml
- name: Simple inline script
  uses: ./.github/actions/reusable-python-scripts
  with:
    inline: 'true'
    script: |
      import json
      result = {"status": "success", "message": "Hello from @create-guru!"}
      print(json.dumps(result, indent=2))
```

### Run Script File
```yaml
- name: Execute script
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/analyze-data.py
    args: '--input data.json --output results.json'
```

### With Dependencies
```yaml
- name: Run with dependencies
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/process.py
    requirements: 'pandas,numpy,scipy'
    python-version: '3.11'
```

### From requirements.txt
```yaml
- name: Install from file
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/main.py
    requirements: requirements.txt
```

### With Environment Variables
```yaml
- name: Execute with env
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/deploy.py
    env-vars: |
      {
        "API_KEY": "${{ secrets.API_KEY }}",
        "ENVIRONMENT": "production",
        "DEBUG": "false"
      }
```

### Capture Output
```yaml
- name: Generate report
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/generate-report.py
    output-file: report.txt

- name: Display report
  run: cat report.txt
```

### With Timeout
```yaml
- name: Long-running script
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/batch-process.py
    timeout: 600  # 10 minutes
```

## Advanced Examples

### Data Processing Pipeline
```yaml
- name: Fetch and process
  uses: ./.github/actions/reusable-python-scripts
  with:
    inline: 'true'
    script: |
      import requests
      import json
      
      # Fetch data
      response = requests.get('https://api.example.com/data')
      data = response.json()
      
      # Process
      processed = [item for item in data if item['active']]
      
      # Save
      with open('processed.json', 'w') as f:
          json.dump(processed, f, indent=2)
      
      print(f"Processed {len(processed)} items")
    requirements: 'requests'
    output-file: processing-log.txt
```

### Testing and Validation
```yaml
- name: Run tests
  id: tests
  uses: ./.github/actions/reusable-python-scripts
  with:
    inline: 'true'
    script: |
      import subprocess
      import sys
      
      result = subprocess.run(
          ['pytest', '-v', '--cov=.', '--cov-report=term'],
          capture_output=True,
          text=True
      )
      
      print(result.stdout)
      if result.stderr:
          print(result.stderr, file=sys.stderr)
      
      sys.exit(result.returncode)
    requirements: 'pytest,pytest-cov'
    fail-on-error: 'true'
```

### Multi-step Analysis
```yaml
- name: Step 1 - Extract
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/extract.py
    args: 'raw-data.json extracted.json'

- name: Step 2 - Transform
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/transform.py
    args: 'extracted.json transformed.json'
    requirements: 'pandas'

- name: Step 3 - Load
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/load.py
    args: 'transformed.json'
    env-vars: '{"DB_URL": "${{ secrets.DB_URL }}"}'
```

### Continue on Error
```yaml
- name: Optional script
  id: optional
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/optional-task.py
    fail-on-error: 'false'

- name: Check result
  run: |
    if [ "${{ steps.optional.outputs.success }}" = "true" ]; then
      echo "✅ Optional task succeeded"
    else
      echo "⚠️  Optional task failed (exit: ${{ steps.optional.outputs.exit-code }})"
    fi
```

### Working Directory Example
```yaml
- name: Execute in subdirectory
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: process.py
    working-directory: ./data-processing
    requirements: requirements.txt
```

## Best Practices

### Script Structure
```python
#!/usr/bin/env python3
"""
Script description
"""
import sys
import json

def main():
    """Main function"""
    try:
        # Your code here
        result = {"status": "success"}
        print(json.dumps(result))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Error Handling
- Always return appropriate exit codes (0 = success, non-zero = error)
- Use try/except blocks for error handling
- Print errors to stderr using `print(..., file=sys.stderr)`
- Provide informative error messages

### Output Formatting
- Use JSON for structured output
- Print progress messages during execution
- Include timestamps for long-running operations
- Use clear, descriptive messages

## Troubleshooting

### Script Not Found
```yaml
# Make sure path is correct
- name: Check file exists
  run: ls -la scripts/

- name: Run script
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: scripts/my-script.py
```

### Import Errors
```yaml
# Install missing dependencies
- name: Run with all deps
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: my-script.py
    requirements: 'package1,package2,package3'
```

### Timeout Issues
```yaml
# Increase timeout for long operations
- name: Long script
  uses: ./.github/actions/reusable-python-scripts
  with:
    script: batch-job.py
    timeout: 1800  # 30 minutes
```

---

**Created by @create-guru** - Infrastructure that illuminates possibilities ⚡
