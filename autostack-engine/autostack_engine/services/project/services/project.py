from datetime import datetime
import os
import platform
from pathlib import Path
import traceback
from typing import Any, Dict, Optional
from uuid import UUID

from autostack_engine.utils.database.models.ai.models import ProjectChat
from autostack_engine.utils.database.models.project.models import Project, ProjectMetadata
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.orchestration.models import BaseService


class ProjectService(BaseService):
    """Service for managing project creation, updates, and deletion"""
    
    service_name = "PROJECT"
    
    def get_documents_path(self):
        """Return the documents folder based on the operating system"""
        system = platform.system().lower()
        
        if system == "windows":
            user_profile = os.environ.get('USERPROFILE')
            return Path(user_profile) / "Documents" if user_profile else Path.home() / "Documents"
        elif system == "darwin":
            return Path.home() / "Documents"
        elif system == "linux":
            xdg_documents = os.environ.get('XDG_DOCUMENTS_DIR')
            return Path(xdg_documents) if xdg_documents else Path.home() / "Documents"
        
        return Path.home() / "Documents"
    
    def create_project_directory(self, project_name: str) -> Optional[str]:
        """Create the project directory structure."""
        try:
            documents_path = self.get_documents_path()
            project_dir = documents_path / "projects" / "autostack" / "created" / project_name.replace(" ", "_").lower()
            project_dir.mkdir(parents=True, exist_ok=True)
            
            self.log_info(f"Created directory: {project_dir}")
            return str(project_dir)
        except Exception as e:
            self.log_error(f"Error creating directory for project '{project_name}': {e}")
            return None
    
    async def create_project(self, project_data: Dict[str, Any], chat_id: Optional[str] = None ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new project.
        
        Args:
            project_data: Dict containing project information
            
        Returns:
            tuple: (success: bool, project_id: Optional[str], error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([Project, ProjectChat])
            
            project_name = project_data.get("name")
            if not project_name:
                return False, None, "Project name is required"
            
            # Check if project already exists
            existing_count = await Project.find({"name": project_name}).count()
            if existing_count > 0:
                error_msg = f"Project '{project_name}' already exists, delete it or rename the project"
                self.log_error(error_msg)
                return False, None, error_msg
            
            # Create project directory
            project_directory = self.create_project_directory(project_name)
            if not project_directory:
                return False, None, f"Failed to create directory for project '{project_name}'"
            
            # Create metadata
            metadata = ProjectMetadata(
                created_date=datetime.now().isoformat(),
                directory=project_directory,
                last_modified=datetime.now().isoformat(),
                tags=project_data.get("metadata", {}).get("tags", []),
                environment=project_data.get("metadata", {}).get("environment", "development")
            )
            
            # Create project
            project = Project(
                id=project_data.get("id"),
                name=project_name,
                author=project_data.get("author", "Unknown"),
                description=project_data.get("description", ""),
                version=project_data.get("version", "1.0.0"),
                metadata=metadata,
                chat_id=UUID(chat_id) if chat_id else None
            )
            
            
            await project.insert()
            if chat_id:
                project_chat = await ProjectChat.find_one(ProjectChat.id == chat_id)
                project_chat.chat_title = f'{project_name} schema generation'
                await project_chat.save()
            
            self.log_info(f"Created project '{project_name}' with ID: {project.id}")
            return True, str(project.id), None
            
        except Exception as e:
            error_msg = f"Error creating project: {traceback.format_exc()}"
            self.log_error(error_msg)
            return False, None, str(e)
    
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Update an existing project.
        
        Args:
            project_id: The project ID to update
            updates: Dict containing fields to update
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([Project])
            
            project = await Project.get(project_id)
            if not project:
                return False, f"Project '{project_id}' not found"
            
            # Update allowed fields
            if "name" in updates:
                project.name = updates["name"]
            if "author" in updates:
                project.author = updates["author"]
            if "description" in updates:
                project.description = updates["description"]
            if "version" in updates:
                project.version = updates["version"]
            
            # Update metadata
            if "metadata" in updates:
                if "tags" in updates["metadata"]:
                    project.metadata.tags = updates["metadata"]["tags"]
                if "environment" in updates["metadata"]:
                    project.metadata.environment = updates["metadata"]["environment"]
            
            project.metadata.last_modified = datetime.now().isoformat()
            await project.save()
            
            self.log_info(f"Updated project '{project_id}'")
            return True, None
            
        except Exception as e:
            error_msg = f"Error updating project: {str(e)}"
            self.log_error(error_msg)
            return False, error_msg
    
    async def delete_project(self, project_id: str, delete_files: bool = False) -> tuple[bool, Optional[str]]:
        """
        Delete a project.
        
        Args:
            project_id: The project ID to delete
            delete_files: Whether to delete the project directory
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([Project])
            
            project = await Project.get(project_id)
            if not project:
                return False, f"Project '{project_id}' not found"
            
            project_name = project.name
            project_directory = project.metadata.directory
            
            # Delete from database
            await project.delete()
            
            # Optionally delete files
            if delete_files and project_directory:
                try:
                    import shutil
                    project_path = Path(project_directory)
                    if project_path.exists():
                        shutil.rmtree(project_path)
                        self.log_info(f"Deleted project directory: {project_directory}")
                except Exception as e:
                    self.log_warning(f"Could not delete project directory: {e}")
            
            self.log_info(f"Deleted project '{project_name}' (ID: {project_id})")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting project: {str(e)}"
            self.log_error(error_msg)
            return False, error_msg
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        try:
            db = DatabaseManager()
            await db.connect([Project])
            return await Project.get(project_id)
        except Exception as e:
            self.log_error(f"Error fetching project: {e}")
            return None
        
    async def get_project_by_chat(self, chat_id: str) -> Optional[Project]:
        """Get a project by its associated chat ID"""
        try:
            db = DatabaseManager()
            await db.connect([Project])
            
            project = await Project.find_one({"chat_id": UUID(chat_id)})
            if project:
                self.log_info(f"Found project for chat: {chat_id}")
            else:
                self.log_info(f"No project found for chat: {chat_id}")
            
            return project
        except Exception as e:
            self.log_error(f"Error fetching project by chat: {e}")
            return None
    
    async def list_projects(self) -> list[Project]:
        """List all projects"""
        try:
            db = DatabaseManager()
            await db.connect([Project])
            return await Project.find_all().to_list()
        except Exception as e:
            self.log_error(f"Error listing projects: {e}")
            return []
