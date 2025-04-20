import os
import subprocess
import json
import platform
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
        self.is_windows = platform.system() == "Windows"
        
        self.safety_settings = {
            "HARM_CATEGORY_DANGEROUS": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE"
        }

    def _translate_command(self, command):
        """Convert between OS-specific commands"""
        if not command:
            return command
            
        if self.is_windows:
            # Linux/macOS to Windows conversions
            if command.startswith("touch "):
                filename = command.split(" ", 1)[1]
                return f"type nul > {filename}"
            elif command.startswith("rm "):
                return f"del {command[3:]}"
            elif command == "ls":
                return "dir"
        else:
            # Windows to Linux/macOS conversions
            if command.startswith("type nul > "):
                filename = command.split("> ", 1)[1]
                return f"touch {filename}"
            elif command.startswith("del "):
                return f"rm {command[4:]}"
            elif command == "dir":
                return "ls"
                
        return command

    def get_ai_response(self, prompt):
        try:
            os_hint = "Windows CMD" if self.is_windows else "Bash"
            response = self.model.generate_content(
                f"""Convert this task to {os_hint} commands in JSON format:
                Task: {prompt}
                
                Respond with ONLY valid JSON:
                {{
                    "steps": [
                        {{
                            "command": "platform_specific_command_here"
                        }}
                    ]
                }}
                """,
                safety_settings=self.safety_settings
            )
            clean_response = response.text.replace('```json', '').replace('```', '').strip()
            return clean_response
        except Exception as e:
            print(f"🚨 Gemini Error: {str(e)}")
            return None

    def run(self):
        print("🔧 Gemini Task Agent Ready (Ctrl+C to exit)")
        print(f"🔹 Detected OS: {'Windows' if self.is_windows else 'Linux/macOS'}")
        
        while True:
            try:
                task = input("\nEnter task: ").strip()
                if task.lower() in ["exit", "quit"]:
                    break
                
                response = self.get_ai_response(task)
                
                if not response:
                    continue
                    
                try:
                    print("\nRaw response:", response)
                    steps = json.loads(response)["steps"]
                    
                    for step in steps:
                        original_cmd = step.get("command", "")
                        translated_cmd = self._translate_command(original_cmd)
                        
                        if translated_cmd:
                            print(f"\n⚡ Executing: {translated_cmd}")
                            try:
                                subprocess.run(translated_cmd, shell=True, check=True)
                            except subprocess.CalledProcessError as e:
                                print(f"⚠️ Command failed (code {e.returncode}): {e.cmd}")
                                print(f"Try manually: {translated_cmd}")
                    
                    print("\n✅ Task completed!")
                except json.JSONDecodeError:
                    print("❌ Invalid JSON. Raw response:")
                    print(response)
                except KeyError:
                    print("❌ Missing 'steps' in response:")
                    print(response)

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