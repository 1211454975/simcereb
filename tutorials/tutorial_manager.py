# simcereb/tutorials/tutorial_manager.py  
"""  
Tutorial manager for the Learning Edition  
Manages loading and navigating through tutorials  
"""  
  
import os  
import yaml  
import markdown  
from datetime import datetime  
  
class TutorialManager:  
    """  
    Manages tutorials and guided learning tasks  
    """  
      
    def __init__(self, config_manager, progress_manager=None):  
        """  
        Initialize the tutorial manager  
          
        Args:  
            config_manager: ConfigManager instance  
            progress_manager: ProgressManager instance, or None  
        """  
        self.config_manager = config_manager  
        self.progress_manager = progress_manager  
        self.tutorials = self._load_tutorials()  
        self.current_tutorial = None  
        self.current_step_index = 0  
      
    def _load_tutorials(self):  
        """Load all available tutorials"""  
        tutorials = {}  
          
        # Get tutorials from configuration  
        tutorial_configs = self.config_manager.get_value("tutorials", {})  
          
        # Get tutorials directory  
        tutorials_dir = os.path.join(  
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  
            "tutorials"  
        )  
          
        # Load tutorials from files  
        for tutorial_id, config in tutorial_configs.items():  
            tutorial_type = config.get("type", "basic")  
              
            # Determine file path based on tutorial type  
            if tutorial_type == "basic":  
                file_path = os.path.join(tutorials_dir, "basic", f"{tutorial_id}.md")  
            elif tutorial_type == "advanced":  
                file_path = os.path.join(tutorials_dir, "advanced", f"{tutorial_id}.md")  
            else:  
                file_path = os.path.join(tutorials_dir, f"{tutorial_id}.md")  
              
            # Load tutorial content if file exists  
            if os.path.exists(file_path):  
                try:  
                    with open(file_path, 'r', encoding='utf-8') as f:  
                        content = f.read()  
                      
                    # Parse tutorial content  
                    tutorial = self._parse_tutorial_content(tutorial_id, content, config)  
                    tutorials[tutorial_id] = tutorial  
                except Exception as e:  
                    print(f"Error loading tutorial {tutorial_id}: {e}")  
          
        return tutorials  
      
    def _parse_tutorial_content(self, tutorial_id, content, config):  
        """  
        Parse tutorial content from markdown file  
          
        Args:  
            tutorial_id (str): ID of the tutorial  
            content (str): Markdown content of the tutorial  
            config (dict): Tutorial configuration  
              
        Returns:  
            dict: Parsed tutorial data  
        """  
        # Basic tutorial info  
        tutorial = {  
            "id": tutorial_id,  
            "title": config.get("title", tutorial_id),  
            "description": config.get("description", ""),  
            "difficulty": config.get("difficulty", "beginner"),  
            "prerequisites": config.get("prerequisites", []),  
            "steps": []  
        }  
          
        # Split content into steps  
        step_separator = config.get("step_separator", "## Step")  
        step_contents = content.split(step_separator)  
          
        # Parse header (content before first step)  
        if step_contents and not step_contents[0].strip().startswith("#"):  
            header = step_contents[0].strip()  
            if not tutorial["description"] and header:  
                tutorial["description"] = header  
            step_contents = step_contents[1:]  
          
        # Parse steps  
        for i, step_content in enumerate(step_contents):  
            if not step_content.strip():  
                continue  
                  
            # Extract step title  
            lines = step_content.strip().split("\n")  
            title = lines[0].strip().lstrip("#").strip() if lines else f"Step {i+1}"  
            content = "\n".join(lines[1:]).strip()  
              
            # Convert markdown to HTML  
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])  
              
            # Extract simulation configuration if present  
            simulation_config = None  
            if "```simulation" in content and "```" in content.split("```simulation", 1)[1]:  
                sim_content = content.split("```simulation", 1)[1].split("```", 1)[0].strip()  
                try:  
                    simulation_config = yaml.safe_load(sim_content)  
                except Exception as e:  
                    print(f"Error parsing simulation config in tutorial {tutorial_id}, step {i+1}: {e}")  
              
            # Create step data  
            step = {  
                "title": title,  
                "content": html_content,  
                "simulation": simulation_config  
            }  
              
            tutorial["steps"].append(step)  
          
        return tutorial  
      
    def get_available_tutorials(self):  
        """Get list of available tutorial IDs"""  
        return list(self.tutorials.keys())  
      
    def get_tutorial_info(self, tutorial_id):  
        """Get information about a specific tutorial"""  
        if tutorial_id in self.tutorials:  
            tutorial = self.tutorials[tutorial_id]  
            return {  
                "id": tutorial["id"],  
                "title": tutorial["title"],  
                "description": tutorial["description"],  
                "difficulty": tutorial["difficulty"],  
                "steps": len(tutorial["steps"])  
            }  
        return None  
      
    def start_tutorial(self, tutorial_id):  
        """  
        Start a specific tutorial  
          
        Args:  
            tutorial_id (str): ID of the tutorial to start  
              
        Returns:  
            dict: First step of the tutorial, or None if tutorial not found  
        """  
        if tutorial_id in self.tutorials:  
            self.current_tutorial = tutorial_id  
            self.current_step_index = 0  
              
            # Update progress if progress manager is available  
            if self.progress_manager:  
                # Record that the tutorial has been started  
                self.progress_manager.update_tutorial_progress(tutorial_id, 0.01)  
              
            # Return first step  
            return self.get_current_step()  
          
        return None  
      
    def get_current_step(self):  
        """  
        Get the current tutorial step  
          
        Returns:  
            dict: Current step data, or None if no tutorial is active  
        """  
        if not self.current_tutorial:  
            return None  
              
        tutorial = self.tutorials.get(self.current_tutorial)  
        if not tutorial:  
            return None  
              
        steps = tutorial.get("steps", [])  
        if not steps or self.current_step_index >= len(steps):  
            return None  
              
        return steps[self.current_step_index]  
      
    def next_step(self):  
        """  
        Move to the next step in the current tutorial  
          
        Returns:  
            dict: Next step data, or None if at the end of the tutorial  
        """  
        if not self.current_tutorial:  
            return None  
              
        tutorial = self.tutorials.get(self.current_tutorial)  
        if not tutorial:  
            return None  
              
        steps = tutorial.get("steps", [])  
        if not steps or self.current_step_index >= len(steps) - 1:  
            # At the end of the tutorial  
            if self.progress_manager:  
                # Mark tutorial as completed  
                self.progress_manager.update_tutorial_progress(self.current_tutorial, 1.0)  
            return None  
              
        # Move to next step  
        self.current_step_index += 1  
          
        # Update progress if progress manager is available  
        if self.progress_manager:  
            progress = (self.current_step_index + 1) / len(steps)  
            self.progress_manager.update_tutorial_progress(self.current_tutorial, progress)  
          
        return steps[self.current_step_index]  
      
    def previous_step(self):  
        """  
        Move to the previous step in the current tutorial  
          
        Returns:  
            dict: Previous step data, or None if at the beginning of the tutorial  
        """  
        if not self.current_tutorial:  
            return None
        
        tutorial = self.tutorials.get(self.current_tutorial)  
        if not tutorial:  
            return None  
              
        steps = tutorial.get("steps", [])  
        if not steps or self.current_step_index <= 0:  
            # At the beginning of the tutorial  
            return None  
              
        # Move to previous step  
        self.current_step_index -= 1  
          
        # Update progress if progress manager is available  
        if self.progress_manager:  
            progress = (self.current_step_index + 1) / len(steps)  
            self.progress_manager.update_tutorial_progress(self.current_tutorial, progress)  
          
        return steps[self.current_step_index]  
      
    def is_first_step(self):  
        """Check if current step is the first step"""  
        return self.current_step_index == 0  
      
    def is_last_step(self):  
        """Check if current step is the last step"""  
        if not self.current_tutorial:  
            return False  
              
        tutorial = self.tutorials.get(self.current_tutorial)  
        if not tutorial:  
            return False  
              
        steps = tutorial.get("steps", [])  
        return self.current_step_index >= len(steps) - 1  
      
    def get_progress(self):  
        """  
        Get current progress in the tutorial  
          
        Returns:  
            float: Progress value between 0 and 1  
        """  
        if not self.current_tutorial:  
            return 0.0  
              
        tutorial = self.tutorials.get(self.current_tutorial)  
        if not tutorial:  
            return 0.0  
              
        steps = tutorial.get("steps", [])  
        if not steps:  
            return 0.0  
              
        return (self.current_step_index + 1) / len(steps)