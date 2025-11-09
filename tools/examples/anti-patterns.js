#!/usr/bin/env node
// JavaScript anti-patterns example

// TODO: Optimize this function
function processData(data) {
    // Using var instead of let/const
    var result = [];
    
    // Console.log in production code
    console.log("Processing data:", data);
    
    // Loose equality operator
    for (var i = 0; i < data.length; i++) {
        if (data[i] == null) {  // Should use ===
            continue;
        }
        result.push(data[i] * 2);
    }
    
    return result;
}

// Using eval - dangerous!
function dynamicCode(code) {
    return eval(code);
}

// Export
module.exports = { processData, dynamicCode };
