import strawberry
from typing import  Optional, List

from autostack_engine.services.component.services.components import ComponentService
from autostack_engine.services.orchestration.service.orchestration import OrchestrationService
from autostack_engine.utils.schema.models.components import ComponentInput, ComponentResponse, ConnectionInput
from autostack_engine.utils.schema.models.generic import DeleteResponse

    
@strawberry.type
class ComponentsMutation:
    
    @strawberry.mutation
    async def add_components(
        self, 
        project_id: str, 
        components: List[ComponentInput], 
        connections: Optional[List[ConnectionInput]] = None
    ) -> ComponentResponse:
        try:
            orchestrator = OrchestrationService()
            
            comp_list = [
                {
                    'component_id': c.component_id,
                    'name': c.name,
                    'type': c.type,
                    'technology': c.technology,
                    'framework': c.framework,
                    'port': c.port,
                    'environment_variables': c.environment_variables,
                    'volumes': c.volumes or [],
                    'dependencies': c.dependencies or []
                }
                for c in components
            ]
            
            conn_list = None
            if connections:
                conn_list = [
                    {
                        'from_component': conn.from_component,
                        'to_component': conn.to_component,
                        'protocol': conn.protocol,
                        'description': conn.description,
                        'port': conn.port
                    }
                    for conn in connections
                ]
            
            success, comp_ids, error = await orchestrator.orchestrate_components_only(
                project_id, comp_list, conn_list
            )
            
            if success:
                return ComponentResponse(
                    success=True,
                    component_ids=comp_ids,
                    message=f"Added {len(comp_ids)} components"
                )
            else:
                return ComponentResponse(success=False, error=error)
                
        except Exception as e:
            return ComponentResponse(success=False, error=str(e))
        
        
    @strawberry.mutation
    async def update_component(
        self,
        component_id: str,
        name: Optional[str] = None,
        port: Optional[int] = None,
        environment_variables: Optional[str] = None
    ) -> ComponentResponse:
        """Update component configuration"""
        try:
            service = ComponentService()
            
            updates = {}
            if name is not None:
                updates['name'] = name
            if port is not None:
                updates['port'] = port
            if environment_variables is not None:
                updates['environment_variables'] = environment_variables
            
            success, error = await service.update_component(component_id, updates)
            
            if success:
                return ComponentResponse(
                    success=True,
                    component_ids=[component_id],
                    message="Component updated successfully"
                )
            else:
                return ComponentResponse(success=False, error=error)
                
        except Exception as e:
            return ComponentResponse(success=False, error=str(e))
    
    @strawberry.mutation
    async def delete_component(
        self,
        component_id: str,
        delete_files: bool = False
    ) -> DeleteResponse:
        """Delete a component"""
        try:
            service = ComponentService()
            success, error = await service.delete_component(component_id, delete_files)
            
            if success:
                return DeleteResponse(success=True, message="Component deleted")
            else:
                return DeleteResponse(success=False, error=error)
                
        except Exception as e:
            return DeleteResponse(success=False, error=str(e))
    