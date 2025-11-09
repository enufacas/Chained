#!/usr/bin/env node
/**
 * Simple calculator in JavaScript
 */

function add(a, b) {
    // Add two numbers
    return a + b;
}

function subtract(a, b) {
    // Subtract b from a
    return a - b;
}

function multiply(a, b) {
    // Multiply two numbers
    return a * b;
}

function divide(a, b) {
    // Divide a by b
    if (b === 0) {
        return null;
    }
    return a / b;
}

// Main execution
let x = 10;
let y = 5;

console.log(`Addition: ${x} + ${y} = ${add(x, y)}`);
console.log(`Subtraction: ${x} - ${y} = ${subtract(x, y)}`);
console.log(`Multiplication: ${x} * ${y} = ${multiply(x, y)}`);
console.log(`Division: ${x} / ${y} = ${divide(x, y)}`);
