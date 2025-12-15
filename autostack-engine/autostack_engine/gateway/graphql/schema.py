import strawberry

from autostack_engine.gateway.graphql.resolvers.ai.ai_mutation import ModelMutation
from autostack_engine.gateway.graphql.resolvers.ai.ai_query import ModelQuery
from autostack_engine.gateway.graphql.resolvers.components.components_mutation import ComponentsMutation
from autostack_engine.gateway.graphql.resolvers.jobs.job_mutation import JobMutation
from autostack_engine.gateway.graphql.resolvers.jobs.job_query import JobQuery
from autostack_engine.gateway.graphql.resolvers.logs.logs_query import ActivityLogQuery
from autostack_engine.gateway.graphql.resolvers.project.project_mutation import ProjectMutuation
from autostack_engine.gateway.graphql.resolvers.project.project_query import ProjectQuery
from autostack_engine.gateway.graphql.subscriptions.project_subscriptions import ProjectSubscription
from autostack_engine.gateway.graphql.resolvers.technologies.technologies_mutation import TechnologiesMutation
from autostack_engine.gateway.graphql.resolvers.user.user_query import UserQuery



@strawberry.type
class Query(ProjectQuery, ModelQuery, JobQuery, UserQuery, ActivityLogQuery):
    pass

@strawberry.type
class Mutation(
    TechnologiesMutation, 
    ProjectMutuation,
    ComponentsMutation,
    ModelMutation
    ):

    pass

@strawberry.type
class Subscription(
    ProjectSubscription
):
    pass