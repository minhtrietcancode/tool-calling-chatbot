import re
import math

def calculator_tool(expression):
    """
    Simple calculator tool for LLM chatbot
    
    Args:
        expression (str): Mathematical expression like "83478 * 990" or "2 + 3 * 4"
    
    Returns:
        dict: {
            "result": float/int or None,
            "error": str or None,
            "expression": str (the input expression)
        }
    """
    
    try:
        # Clean the expression - remove extra spaces
        expression = expression.strip()
        
        # Basic security check - only allow safe characters
        allowed_pattern = r'^[0-9+\-*/().\s^]+$'
        if not re.match(allowed_pattern, expression):
            return {
                "result": None,
                "error": "Invalid characters in expression. Only numbers and +, -, *, /, (, ), ^ allowed.",
                "expression": expression
            }
        
        # Replace ^ with ** for Python power operator
        expression = expression.replace('^', '**')
        
        # Evaluate the expression safely
        # Using eval with restricted builtins for safety
        allowed_names = {
            "__builtins__": {
                "abs": abs,
                "round": round,
                "pow": pow,
                "max": max,
                "min": min
            },
            "math": math
        }
        
        result = eval(expression, allowed_names)
        
        # Convert to int if it's a whole number for cleaner output
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        return {
            "result": result,
            "error": None,
            "expression": expression
        }
        
    except ZeroDivisionError:
        return {
            "result": None,
            "error": "Division by zero",
            "expression": expression
        }
    except Exception as e:
        return {
            "result": None,
            "error": f"Invalid expression: {str(e)}",
            "expression": expression
        }

# Test various expressions
def test_calculator():
    """Test the calculator with various inputs"""
    
    test_cases = [
        "83478 * 990",
        "2 + 3 * 4",
        "100 / 4",
        "(5 + 3) * 2",
        "2^3",  # Power operation
        "sqrt(16)",  # This will fail - not supported
        "10 / 0",   # Division by zero
        "5 + hello", # Invalid expression
    ]
    
    print("TESTING CALCULATOR TOOL:")
    print("-" * 40)
    
    for expr in test_cases:
        result = calculator_tool(expr)
        print(f"Input: '{expr}'")
        if result["error"]:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Result: {result['result']}")
        print()


if __name__ == "__main__":    
    # Run tests
    test_calculator()
    
    # Interactive mode
    print("\nTRY IT YOURSELF:")
    while True:
        expr = input("Enter math expression (or 'quit'): ")
        if expr.lower() == 'quit':
            break
        
        result = calculator_tool(expr)
        if result["error"]:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ {result['result']}")
        print()