# Example: Python file with some anti-patterns

import os

# TODO: Refactor this function
def process_data(data):
    """Process the data"""
    try:
        # Debug output
        print("debug: processing data")
        
        # Bare except - catches everything!
        result = None
        try:
            result = data * 2
        except:
            pass
        
        return result
    except:
        return None


# Hardcoded secret - bad practice
api_key = "sk_test_1234567890abcdefghijklmnop"

def query_database(user_input):
    """Query database - SQL injection risk"""
    query = "SELECT * FROM users WHERE name = '%s'" % user_input
    # execute(query)  # Potential SQL injection
    pass


if __name__ == "__main__":
    data = [1, 2, 3]
    result = process_data(data)
    print(result)
