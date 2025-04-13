import os
import subprocess
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AITaskAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        self.safety_settings = {
            "HARM_CATEGORY_DANGEROUS": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE"
        }

    def get_ai_response(self, prompt):
        try:
            response = self.model.generate_content(
                f"""Convert this task to terminal commands in JSON format:
                Task: {prompt}
                
                Respond with ONLY valid JSON in this exact format:
                {{
                    "steps": [
                        {{
                            "command": "actual_terminal_command"
                        }}
                    ]
                }}
                No additional text or markdown formatting.
                """,
                safety_settings=self.safety_settings
            )
            # Remove markdown code blocks if present
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            return clean_response
        except Exception as e:
            print(f"🚨 Gemini Error: {str(e)}")
            return None

    def run(self):
        print("🔧 Gemini Task Agent Ready (Ctrl+C to exit)")
        while True:
            try:
                task = input("\nEnter task: ").strip()
                if task.lower() in ["exit", "quit"]:
                    break
                
                response = self.get_ai_response(task)
                
                if not response:
                    continue
                    
                try:
                    # Debug print to see raw response
                    print("\nRaw response for debugging:", response)
                    
                    steps = json.loads(response)["steps"]
                    
                    for step in steps:
                        cmd = step.get("command")
                        if cmd:
                            print(f"\n⚡ Executing: {cmd}")
                            subprocess.run(cmd, shell=True, check=True)
                    
                    print("\n✅ Task completed!")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {str(e)}")
                    print("Problematic response:", response)
                except KeyError:
                    print("❌ Missing 'steps' in response")
                    print("Full response:", response)

            except KeyboardInterrupt:
                print("\n🛑 Exiting safely...")
                break
            except Exception as e:
                print(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    try:
        agent = AITaskAgent()
        agent.run()
    except ValueError as e:
        print(f"❌ Setup error: {e}")