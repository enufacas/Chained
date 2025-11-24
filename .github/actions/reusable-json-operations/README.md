# JSON Operations Action

**Enhanced by @create-guru** ⚡

Powerful JSON processing action with query, validate, merge, transform, and prettify operations using jq.

## Features

- 🔍 **Query**: Extract data using jq query syntax
- ✅ **Validate**: Check JSON syntax with detailed error reporting
- 🔀 **Merge**: Intelligently combine multiple JSON files
- 🔄 **Transform**: Apply jq transformations to modify structure
- 🎨 **Prettify**: Format JSON with proper indentation
- 📦 Automatic jq installation
- 💾 Output to file or stdout
- 🔒 Comprehensive error handling

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `operation` | Operation to perform: query, validate, merge, transform, prettify | Yes | - |
| `input-file` | Path to input JSON file | No* | - |
| `input-json` | JSON string to process | No* | - |
| `query` | JQ query (for query operation) | No | - |
| `output-file` | Path to save output | No | stdout |
| `merge-files` | Comma-separated JSON files (for merge) | No | - |
| `transform-script` | JQ expression (for transform) | No | - |
| `fail-on-error` | Exit with error on validation failure | No | `true` |

*Either `input-file` or `input-json` must be provided (except for merge operation).

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Operation result or transformed JSON |
| `valid` | Whether JSON is valid (for validate operation) |
| `error` | Error message if operation failed |

## Usage Examples

### Query JSON Data
```yaml
- name: Extract agent names
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: query
    input-file: agents.json
    query: '.agents[] | select(.score > 0.85) | .name'
```

### Validate JSON
```yaml
- name: Validate configuration
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: validate
    input-file: config.json
    fail-on-error: 'true'
```

### Merge Multiple Files
```yaml
- name: Merge configurations
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: merge
    merge-files: 'base-config.json,env-config.json,user-config.json'
    output-file: final-config.json
```

### Transform JSON Structure
```yaml
- name: Add computed field
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: transform
    input-file: stats.json
    transform-script: '.total = (.agents + .workflows + .actions)'
    output-file: enhanced-stats.json
```

### Prettify JSON
```yaml
- name: Format JSON
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: prettify
    input-file: minified.json
    output-file: formatted.json
```

### Use with Inline JSON
```yaml
- name: Process inline JSON
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: query
    input-json: '{"agents": [{"name": "create-guru", "active": true}]}'
    query: '.agents[] | .name'
```

## Advanced Examples

### Extract and Use in Next Step
```yaml
- name: Get version
  id: version
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: query
    input-file: package.json
    query: '.version'

- name: Use version
  run: echo "Version is ${{ steps.version.outputs.result }}"
```

### Conditional Processing
```yaml
- name: Validate before deploying
  id: validate
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: validate
    input-file: deployment-config.json
    fail-on-error: 'false'

- name: Deploy if valid
  if: steps.validate.outputs.valid == 'true'
  run: ./deploy.sh
```

### Complex Transformations
```yaml
- name: Restructure data
  uses: ./.github/actions/reusable-json-operations
  with:
    operation: transform
    input-file: raw-data.json
    transform-script: |
      {
        summary: {
          total: (.items | length),
          active: ([.items[] | select(.status == "active")] | length)
        },
        items: [.items[] | {name, status, created: .created_at}]
      }
    output-file: processed-data.json
```

## Error Handling

The action provides detailed error messages for common issues:

- **File not found**: Clear message with file path
- **Invalid JSON**: Syntax error details from jq
- **Missing query**: Helpful reminder of required inputs
- **Merge failures**: Identifies which file caused the issue

## JQ Query Reference

Quick reference for common jq queries:

- Select field: `.field`
- Array access: `.items[0]`
- Filter array: `.items[] | select(.active == true)`
- Map array: `.items[] | {name, id}`
- Count items: `.items | length`
- Add field: `. + {new_field: "value"}`
- Merge objects: `. * {overrides}`

For full jq documentation: https://stedolan.github.io/jq/manual/

---

**Created by @create-guru** - Infrastructure that illuminates possibilities ⚡
