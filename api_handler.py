"""
api_handler.py — Groq API Integration (FREE - 14,400 requests/day)
NLP BASED CODE INTERPRETER v2.0
"""

from groq import Groq


class APIHandler:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    def _call_api(self, prompt: str, max_tokens: int = 1024) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ API Error: {str(e)}"

    def explain_code(self, code: str, language: str) -> str:
        return self._call_api(f"""You are a coding tutor. Explain this {language} code in simple plain English for a beginner.
- State the main purpose in one sentence first
- Explain step by step
- Use simple analogies
Code:
{code}""")

    def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        return self._call_api(f"""Translate this {source_lang} code to {target_lang}.
            - Preserve exact same logic
            - Use idiomatic {target_lang} style
            - Add comments explaining key differences
            {source_lang} Code:
            {code}
            Provide ONLY the translated {target_lang} code.""")

    def analyze_complexity(self, code: str, language: str) -> str:
        return self._call_api(f"""Analyze time and space complexity of this {language} code.
Code:
{code}
Format:
## Time Complexity
Current: O(?) - Reason: ...
## Space Complexity
Current: O(?) - Reason: ...
## Bottleneck
...
## Optimized Version
(write optimized code here)
## After Optimization
Time: O(?) - Improvement: ...""")

    def detect_bugs(self, code: str, language: str) -> str:
        return self._call_api(f"""Review this {language} code for bugs and bad practices.
Code:
{code}
Format:
## Critical Bugs
...
## Warnings
...
## Suggestions
...
## Fixed Code
(write fixed code here)""")

    def generate_test_cases(self, code: str, language: str) -> str:
        return self._call_api(f"""Generate test cases for this {language} code.
Code:
{code}
Format:
## Normal Cases
...
## Edge Cases
...
## Error Cases
...
## Test Code
(write actual test code here)""")

    def generate_pseudocode(self, code: str, language: str) -> str:
        """SEPARATED: Generates ONLY pseudocode"""
        return self._call_api(f"""Convert this {language} code into clean pseudocode only.
Use plain English steps that a non-programmer can understand.
Code:
{code}
Format:
BEGIN
  Step 1: ...
  Step 2: ...
  Step 3: ...
  ...
END
Use simple language. No code syntax.""")

    def generate_algorithm(self, code: str, language: str) -> str:
        """SEPARATED: Generates ONLY algorithm name and explanation"""
        return self._call_api(f"""Analyze this {language} code and identify the algorithm.
Code:
{code}
Format:
## Algorithm Name
(e.g. Bubble Sort, Binary Search, Fibonacci, etc. or "Custom Algorithm")

## How the Algorithm Works
(Explain the concept in 3-5 sentences simply)

## Time Complexity
O(?) - Brief reason

## Space Complexity
O(?) - Brief reason

## Best Use Case
(When should this algorithm be used?)""")

    def generate_approaches(self, code: str, language: str) -> str:
        return self._call_api(f"""Provide 3 different approaches to solve the same problem as this {language} code:
Code:
{code}
Format:
## Problem Being Solved
(One sentence)

## Approach 1: Brute Force
**Complexity:** O(?)
**When to use:** ...
```{language}
(code here)
```

## Approach 2: Optimized
**Complexity:** O(?)
**When to use:** ...
```{language}
(code here)
```

## Approach 3: Best Solution
**Complexity:** O(?)
**When to use:** ...
```{language}
(code here)
```

## Recommendation
(Which to use and why)""", max_tokens=1500)

    def chat_about_code(self, code: str, language: str, messages: list) -> str:
        """Continuous AI chat with full conversation history"""
        try:
            system_msg = {
                "role": "system",
                "content": f"""You are an expert coding assistant. The user has pasted this {language} code:

```{language}
{code}
```

Answer all questions specifically about this code. Be clear, concise and helpful.
If asked something unrelated to the code, gently redirect to the code."""
            }
            full_messages = [system_msg] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Chat Error: {str(e)}"
