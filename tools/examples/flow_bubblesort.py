#!/usr/bin/env python3
"""
Example: Bubble Sort
Demonstrates nested loops and conditional swapping
"""

def bubble_sort(arr):
    """Sort an array using bubble sort algorithm"""
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        swapped = False
        
        # Last i elements are already sorted
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if arr[j] > arr[j + 1]:
                # Swap if they are in wrong order
                temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
                swapped = True
        
        # If no swaps occurred, array is sorted
        if not swapped:
            break
    
    return arr


def main():
    """Test the bubble sort function"""
    numbers = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original array: {numbers}")
    
    sorted_numbers = bubble_sort(numbers.copy())
    print(f"Sorted array: {sorted_numbers}")
    
    return sorted_numbers


if __name__ == "__main__":
    main()
