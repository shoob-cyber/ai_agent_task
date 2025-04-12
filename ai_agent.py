import os
import subprocess
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class AITaskAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")  # Correct variable name
        if not self.api_key:
            raise ValueError("API key not found in .env file")
            
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_ai_response(self, prompt):
        try:
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"🚨 API Error: {str(e)}")
            return None

    def run(self):
        print("🔧 AI Task Agent Ready (Ctrl+C to exit)")
        while True:
            try:
                task = input("\nEnter task: ").strip()
                if task.lower() in ["exit", "quit"]:
                    break
                
                response = self.get_ai_response(
                    f"Convert this to executable steps in JSON format: {task}\n"
                    "Output ONLY this JSON structure:\n"
                    "{\"steps\":[{\"action\":\"command\",\"command\":\"valid_command\"}]}"
                )
                
                if not response:
                    print("❌ No response from API")
                    continue
                    
                try:
                    content = response["choices"][0]["message"]["content"]
                    steps = json.loads(content)["steps"]
                    
                    for step in steps:
                        cmd = step.get("command")
                        if not cmd:
                            continue
                            
                        print(f"\n⚡ Executing: {cmd}")
                        try:
                            subprocess.run(cmd, shell=True, check=True, timeout=30)
                        except subprocess.TimeoutExpired:
                            print("⌛ Command timed out")
                            
                    print("\n✅ Task completed!")
                except json.JSONDecodeError:
                    print("❌ Invalid JSON from AI")
                    print("Raw response:", content)
                except KeyError:
                    print("❌ Malformed API response")
                    print("Full response:", response)

            except KeyboardInterrupt:
                print("\n🛑 Exiting safely...")
                break
            except Exception as e:
                print(f"⚠️ Unexpected error: {str(e)}")

if __name__ == "__main__":
    try:
        agent = AITaskAgent()
        agent.run()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")