import json
import os
import threading
import subprocess
import better_exceptions
import structlog


from autostack_engine.utils.database.models.project.models import Project
from autostack_engine.utils.database.models.technologies.models import Technology
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.kafka.base_topic import BaseTopic
from autostack_engine.utils.schema.models.technologies import TechnologyManager

better_exceptions.hook()
logger = structlog.get_logger()

class DevelopmentCreateTopic(BaseTopic):
    topic_name = "environment.development.create"
    
    async def create_technologies(self, project_id, technologies):
        try:
            db = DatabaseManager()
            await db.connect([Project, Technology])

            existing_project = await Project.get(project_id)
            if not existing_project:
                logger.error(f"[ENVIRONMENT] Project with ID '{project_id}' does not exist.")
                return False

            # Creating the technologies
            tech_configs = []
            for tech_data in technologies:
                # Convert environment_variables from list to dict
                if tech_data.get('environment_variables') and isinstance(tech_data['environment_variables'], list):
                    env_vars = {}
                    for env_var in tech_data['environment_variables']:
                        env_vars[env_var['name']] = env_var['value']
                    tech_data['environment_variables'] = env_vars
                elif tech_data.get('environment_variables') == []:
                    tech_data['environment_variables'] = None
                
                if tech_data.get('configuration') == []:
                    tech_data['configuration'] = None

                if tech_data.get('configuration') and isinstance(tech_data['configuration'], str):
                    try:
                        tech_data['configuration'] = json.loads(tech_data['configuration'])
                    except json.JSONDecodeError:
                        logger.warning(f"[ENVIRONMENT] Invalid JSON in configuration for {tech_data.get('name')}, setting to None")
                        tech_data['configuration'] = None

                tech_config = Technology(**tech_data)
                tech_configs.append(tech_config)

            await Technology.insert_many(tech_configs)
            await self.initialise_development_environment(project_directory=existing_project.metadata.directory, technologies=tech_configs)
            return True
        except Exception as e:
            logger.error("environment.create_tech_error",
            project_id=project_id,
            error=str(e),
            exc_info=True)
            return False
            
            
    async def initialise_development_environment(self, project_directory, technologies):
        try:
            
            project_directory = os.path.abspath(project_directory)
        
            print(project_directory)
            # Check if devbox.json exists, if not initialize
            devbox_json_path = os.path.join(project_directory, "devbox.json")
            if not os.path.exists(devbox_json_path):
                logger.info("Initializing devbox in project directory")
                init_result = subprocess.run(
                    ["devbox", "init"], 
                    cwd=project_directory, 
                    capture_output=True, 
                    text=True
                )
                if init_result.returncode != 0:
                    logger.error(f'Error initializing devbox: {init_result.stderr}')
                    return None
            
            # Get the technologies and add them to devbox
            package_specs = TechnologyManager.get_devbox_technologies(technologies)
            
            def run_devbox_async():
                result = subprocess.run(
                    ["devbox", "add"] + package_specs, 
                    cwd=project_directory, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    logger.info("Devbox packages installed successfully")
                else:
                    logger.error(f'Error adding packages: {result.stderr}')
            
            # Run in background thread
            threading.Thread(target=run_devbox_async, daemon=True).start()
            
            return True  # Return immediately
        
        except Exception as e:
            logger.error("environment.create_tech_error", 
                error=str(e),
                exc_info=True
            )
            return None
   
    async def process_message(self, key, value):
        try:
            data = json.loads(value) if value else {}
            
            
            logger.info(f"[ENVIRONMENT] Creating development environment for: {key}")
            
            await self.create_technologies(project_id=key, technologies=data)
            
            logger.info(f"[ENVIRONMENT] Created development environment for: {key}")

        except Exception as e:
            logger.error(
                f"[ENVIRONMENT] Error creating environment",
                error=str(e),
                exc_info=True
            )