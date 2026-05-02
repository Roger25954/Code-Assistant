# test_agent.py
from agent import get_explanation, get_tests

code = """
def suma(a, b):
    return a + b
"""

print("=== EXPLICACIÓN ===")
print(get_explanation(code))

print("\n=== TESTS ===")
print(get_tests(code))