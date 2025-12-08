import strawberry
from typing import Optional, List
from autostack_engine.services.environment.services.technologies import TechnologyService
from autostack_engine.services.orchestration.service.orchestration import OrchestrationService
from autostack_engine.utils.schema.models.generic import DeleteResponse
from autostack_engine.utils.schema.models.technologies import TechnologyInput, TechnologyResponse


@strawberry.type
class TechnologiesMutation:
    @strawberry.mutation
    async def add_technologies(self, project_id: str, technologies: List[TechnologyInput]) -> TechnologyResponse:
        try:
            orchestrator = OrchestrationService()
            
            tech_list = [
                {
                    'name': t.name,
                    'category': t.category,
                    'version': t.version,
                    'enabled': t.enabled,
                    'port': t.port,
                    'environment_variables': t.environment_variables,
                    'configuration': t.configuration
                }
                for t in technologies
            ]
            
            success, tech_ids, error = await orchestrator.orchestrate_technologies_only(
                project_id, tech_list
            )
            
            if success:
                return TechnologyResponse(
                    success=True,
                    technology_ids=tech_ids,
                    message=f"Added {len(tech_ids)} technologies"
                )
            else:
                return TechnologyResponse(success=False, error=error)
                
        except Exception as e:
            return TechnologyResponse(success=False, error=str(e))
        
    @strawberry.mutation
    async def update_technology(
        self,
        tech_id: str,
        name: Optional[str] = None,
        version: Optional[str] = None,
        enabled: Optional[bool] = None,
        port: Optional[int] = None
    ) -> TechnologyResponse:
        """Update technology configuration"""
        try:
            service = TechnologyService()
            
            updates = {}
            if name is not None:
                updates['name'] = name
            if version is not None:
                updates['version'] = version
            if enabled is not None:
                updates['enabled'] = enabled
            if port is not None:
                updates['port'] = port
            
            success, error = await service.update_technology(tech_id, updates)
            
            if success:
                return TechnologyResponse(
                    success=True,
                    technology_ids=[tech_id],
                    message="Technology updated successfully"
                )
            else:
                return TechnologyResponse(success=False, error=error)
                
        except Exception as e:
            return TechnologyResponse(success=False, error=str(e))
    
    @strawberry.mutation
    async def delete_technology(self, tech_id: str) -> DeleteResponse:
        """Delete a technology"""
        try:
            service = TechnologyService()
            success, error = await service.delete_technology(tech_id)
            
            if success:
                return DeleteResponse(success=True, message="Technology deleted")
            else:
                return DeleteResponse(success=False, error=error)
                
        except Exception as e:
            return DeleteResponse(success=False, error=str(e))
    