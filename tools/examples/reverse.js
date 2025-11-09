#!/usr/bin/env node
/**
 * String reverser
 * Reverses a string in multiple ways
 */

function reverseString(text) {
    /**
     * Reverse a string using built-in methods
     * 
     * @param {string} text - The string to reverse
     * @returns {string} The reversed string
     */
    
    // Convert to array, reverse, and join back
    return text.split('').reverse().join('');
}

function reverseStringManual(text) {
    /**
     * Reverse a string manually using a loop
     * 
     * @param {string} text - The string to reverse
     * @returns {string} The reversed string
     */
    
    // Initialize empty result
    let result = '';
    
    // Loop through string backwards
    for (let i = text.length - 1; i >= 0; i--) {
        result = result + text[i];
    }
    
    return result;
}

// Test the functions
if (require.main === module) {
    const testStrings = ['hello', 'world', 'JavaScript', 'Code Golf'];
    
    testStrings.forEach(function(testString) {
        const reversed = reverseString(testString);
        console.log(`"${testString}" reversed: "${reversed}"`);
    });
}

module.exports = { reverseString, reverseStringManual };
