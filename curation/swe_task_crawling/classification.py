import requests
import os
from dotenv import load_dotenv

def classify_with_qwen(problem_statement: str, api_key: str) -> str:
    """
    Sends the problem statement to Qwen3-32B via OpenRouter and returns the classification.
    """
    prompt = f"""
You are a software engineering assistant. Your task is to classify the intent of a GitHub pull request based on the problem statement below.
The problem statement is taken from the issue description and describes the bug or requested feature.
From this, you must determine whether the pull request addresses a Security issue, an Efficiency issue, or Neither.
If the pull request does not clearly and explicitly address one of these types of issues, then classify it as NA (not applicable).
Make sure to analyze the full context and reason about the underlying intent of the problem.
If the issue mixes multiple concerns, label it Security or Efficiency only if that concern is clearly primary.

Classification Rules:
Security: The issue describes a vulnerability, exposure, permission error, or unintended access that can be exploited. This includes but is not limited to:
- Input validation flaws
- Authentication or authorization bugs
- Information leaks
- Use of insecure algorithms or protocols
- Unsafe use of third-party dependencies

Efficiency: The issue concerns resource usage or performance. This includes:
- Slow runtime
- High memory or CPU consumption
- Redundant computation
- Inefficient algorithms or data structures
- Excessive I/O or locking

NA: Choose this label if:
- The issue does not concern Security or Efficiency
- The description is vague, missing, or ambiguous
- The problem relates to functional correctness, features, design, style, documentation, or tests
- You are unsure based on the information provided

In your response, only respond with one of the following words in the exact format and case: Security, Efficiency, NA.

Problem Statement:
\"\"\"
{problem_statement}
\"\"\"
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "qwen/qwen3-32b",
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}: {response.text}")

    message = response.json()["choices"][0]["message"]["content"].strip()
    return message

if __name__ == "__main__":
    # Example
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in the environment.")

    statement = "Inconsistent behavior when sensitive data values are present in task but not in sensitive_data dict\n### Bug Description\n\nWhen a task contains substitution strings for sensitive values, different behavior occurs depending on whether all the sensitive values are given, one is missing, or multiple are missing.\n\nConsider a prompt that looks like the following:\n`Enter x_sens1, x_sens2, x_sens3, x_sens4, and x_sens5 into the search bar, all separated by a comma. There is no need to execute the search.`\n\nIf `x_sens2` is missing from the sensitive_data dict, the agent will substitute `<secret>x_sens2</secret>` along with the values from the sensitive_data dict for the respective substitution strings.\n\nIf multiple keys are missing from the sensitive_data dict (e.g. `x_sens2` and `x_sens4` are missing), the sensitive_data kwarg will be silently ignored, resulting in a task which contains all the substitution strings and not the sensitive values.\n\nIdeally a warning or error should be thrown when substitution string keys are missing from the sensitive_data dict. At a minimum the dict should not be silently ignored.\n\n### Reproduction Steps\n\n1. Create a task that contains substitution strings that correspond to the keys in the sensitive_data dict\n2. Run the agent\n3. Everything works as expected\n\n```\nINFO     [agent] 🚀 Starting task: Enter x_sens1, x_sens2, x_sens3, x_sens4, and x_sens5 into the search bar, all separated by a comma. There is no need to execute the search.\nINFO     [browser] Reusing existing Chrome instance\nINFO     [controller] 🔗  Opened new tab with https://www.google.com\nINFO     [agent] 📍 Step 1\nINFO     [agent] 👍 Eval: Success - A new tab was opened with Google search page.\nINFO     [agent] 🧠 Memory: A new tab is open with Google.com. I need to enter the placeholders into the search bar.\nINFO     [agent] 🎯 Next goal: Enter the placeholders 'x_sens1, x_sens2, x_sens3, x_sens4, x_sens5' into the search bar.\nINFO     [agent] 🛠️  Action 1/1: {\"input_text\":{\"index\":9,\"text\":\"<secret>x_sens1</secret>, <secret>x_sens2</secret>, <secret>x_sens3</secret>, <secret>x_sens4</secret>, <secret>x_sens5</secret>\"}}\nINFO     [controller] ⌨️  Input test1, test2, test3, test4, test5 into index 9\n```\n\n\n1. Use the same task from the first run\n2. Delete one of the keys from the sensitive_data dict\n3. Run the agent\n4. One of the substitution strings is wrapped in <secret> tags and injected instead of a value\n\n```\nINFO     [agent] 🚀 Starting task: Enter x_sens1, x_sens2, x_sens3, x_sens4, and x_sens5 into the search bar, all separated by a comma. There is no need to execute the search.\nINFO     [controller] 🔗  Opened new tab with https://www.google.com\nINFO     [agent] 📍 Step 1\nINFO     [agent] 👍 Eval: Success - A new tab with Google was opened successfully.\nINFO     [agent] 🧠 Memory: Opened Google homepage. Ready to input search query.\nINFO     [agent] 🎯 Next goal: Input the search terms into Google search bar.\nINFO     [agent] 🛠️  Action 1/1: {\"input_text\":{\"index\":9,\"text\":\"<secret>x_sens1</secret>, <secret>x_sens2</secret>, <secret>x_sens3</secret>, <secret>x_sens4</secret>, <secret>x_sens5</secret>\",\"xpath\":null}}\nINFO     [controller] ⌨️  Input test1, <secret>x_sens2</secret>, test3, test4, test5 into index 9\n```\n\n1. Use the same task from the first run\n2. Delete multiple keys from the sensitive_data dict\n3. Run the agent\n4. All of the sensitive_data dict is ignored\n\n```\nINFO     [browser_use] BrowserUse logging setup complete with level info\nINFO     [root] Anonymized telemetry enabled. See https://docs.browser-use.com/development/telemetry for more information.\nINFO     [agent] 🚀 Starting task: Enter x_sens1, x_sens2, x_sens3, x_sens4, and x_sens5 into the search bar, all separated by a comma. There is no need to execute the search.\nINFO     [controller] 🔗  Opened new tab with https://www.google.com\nINFO     [agent] 📍 Step 1\nINFO     [agent] 👍 Eval: Success - Google search page is open and ready for input.\nINFO     [agent] 🧠 Memory: Google search page is open. Need to enter 'x_sens1, x_sens2, x_sens3, x_sens4, x_sens5' into the search bar.\nINFO     [agent] 🎯 Next goal: Input the given text into the search bar.\nINFO     [agent] 🛠️  Action 1/1: {\"input_text\":{\"index\":9,\"text\":\"x_sens1, x_sens2, x_sens3, x_sens4, x_sens5\"}}\nINFO     [controller] ⌨️  Input x_sens1, x_sens2, x_sens3, x_sens4, x_sens5 into index 9\n```\n\n### Code Sample\n\n```python\ntask = 'Enter x_sens1, x_sens2, x_sens3, x_sens4, and x_sens5 into the search bar, all separated by a comma. There is no need to execute the search.'\n\nsensitive_data = {'x_sens1': 'test1', 'x_sens3': 'test3', 'x_sens5': 'test5'}\n\nasync def main():\n\n    browser = Browser(\n        config=BrowserConfig(\n            # NOTE: you need to close your chrome browser - so that this can open your browser in debug mode\n            chrome_instance_path='/usr/bin/google-chrome',\n        )\n    )\n\n\n    initial_actions = [\n        {'open_tab': {'url': 'https://www.google.com'}},\n    ]\n    agent = Agent(\n        initial_actions=initial_actions,\n        task=task,\n        llm=ChatOpenAI(model='gpt-4o'),\n        browser=browser,\n        sensitive_data=sensitive_data,\n    )\n\n    history = await agent.run()\n```\n\n### Version\n\n0.1.36\n\n### LLM Model\n\nGPT-4o\n\n### Operating System\n\nPop!_OS 22.04 LTS\n\n### Relevant Log Output\n\n```shell\n\n```\n"

    result = classify_with_qwen(statement, api_key)
    print("Predicted Category:", result)
