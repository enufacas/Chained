#!/usr/bin/env node
/**
 * Factorial calculator
 * Calculates the factorial of a number
 */

function factorial(number) {
    /**
     * Calculate factorial of a number
     * 
     * @param {number} number - The number to calculate factorial for
     * @returns {number} The factorial result
     */
    
    // Base case: factorial of 0 or 1 is 1
    if (number <= 1) {
        return 1;
    }
    
    // Recursive case: n! = n * (n-1)!
    return number * factorial(number - 1);
}

// Iterative version for comparison
function factorialIterative(number) {
    // Initialize result
    let result = 1;
    
    // Multiply all numbers from 2 to n
    for (let i = 2; i <= number; i++) {
        result = result * i;
    }
    
    return result;
}

// Test the functions
if (require.main === module) {
    const testNumbers = [0, 1, 5, 10];
    
    testNumbers.forEach(function(testNumber) {
        const result = factorial(testNumber);
        console.log(`Factorial of ${testNumber} = ${result}`);
    });
}

module.exports = { factorial, factorialIterative };
