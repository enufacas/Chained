#!/bin/bash
# Quick examples of AI Code Golf Optimizer usage

echo "=== Example 1: Basic Python Optimization ==="
cat << 'EOF' | python3 code-golf-optimizer.py -l python
# Simple function
def greet(name):
    """Greet someone"""
    message = "Hello, " + name
    return message
EOF

echo ""
echo "=== Example 2: JavaScript with Statistics ==="
python3 code-golf-optimizer.py -l javascript --stats << 'EOF'
// Check if even
function isEven(x) {
    // Return true if even
    return x % 2 === 0 ? true : false;
}
EOF

echo ""
echo "=== Example 3: JSON Output ==="
python3 code-golf-optimizer.py -l python --format json << 'EOF' | jq -r '.reduction_percentage'
x = True  # comment
y = False # another
EOF

echo ""
echo "=== Example 4: Bash Script Optimization ==="
cat << 'EOF' | python3 code-golf-optimizer.py -l bash
#!/bin/bash
# Deploy script
# Initialize variables
HOST="server.com"

# Deploy application
echo "Deploying to $HOST"
ssh user@$HOST "cd /app && ./deploy.sh"
EOF
