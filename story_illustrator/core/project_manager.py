"""Project management - save and load story projects"""
import json
from pathlib import Path
from datetime import datetime
import re


class ProjectManager:
    """Manages story projects"""

    def __init__(self, projects_folder=None):
        if projects_folder is None:
            projects_folder = Path.cwd() / "projects"
        self.projects_folder = Path(projects_folder)
        self.projects_folder.mkdir(exist_ok=True)

    @staticmethod
    def sanitize_filename(name):
        """Remove invalid filename characters"""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        return name[:50]  # Limit length

    def save_project(self, project_name, sections):
        """
        Save a project with sections

        Args:
            project_name: Name of the project
            sections: List of section dicts with 'title', 'text', 'folder'

        Returns:
            Path to saved project file
        """
        if not sections:
            return None

        project_file = self.projects_folder / f"{project_name}.json"

        project_data = {
            'name': project_name,
            'created': datetime.now().isoformat(),
            'sections': []
        }

        for section in sections:
            section_data = {
                'title': section['title'],
                'text': section['text'],
                'folder': str(section.get('folder', ''))
            }
            project_data['sections'].append(section_data)

        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            return project_file
        except Exception as e:
            print(f"Failed to save project: {e}")
            return None

    def load_project(self, project_name):
        """
        Load a project by name

        Args:
            project_name: Name of the project (without .json extension)

        Returns:
            Dictionary with 'name' and 'sections' list, or None if failed
        """
        project_file = self.projects_folder / f"{project_name}.json"

        if not project_file.exists():
            return None

        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Convert section data back to section objects
            sections = []
            for section_data in project_data['sections']:
                section = {
                    'title': section_data['title'],
                    'text': section_data['text'],
                    'folder': Path(section_data['folder']) if section_data.get('folder') else None
                }
                sections.append(section)

            return {
                'name': project_data['name'],
                'created': project_data.get('created'),
                'sections': sections
            }

        except Exception as e:
            print(f"Failed to load project: {e}")
            return None

    def list_projects(self):
        """
        Get list of all projects sorted by modification time (newest first)

        Returns:
            List of project names (without .json extension)
        """
        if not self.projects_folder.exists():
            return []

        project_files = sorted(
            self.projects_folder.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return [f.stem for f in project_files]

    def delete_project(self, project_name):
        """Delete a project"""
        project_file = self.projects_folder / f"{project_name}.json"
        if project_file.exists():
            project_file.unlink()
            return True
        return False

    def generate_project_name(self, first_section_title):
        """Generate a unique project name from section title"""
        sanitized = self.sanitize_filename(first_section_title)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{sanitized}_{timestamp}"
