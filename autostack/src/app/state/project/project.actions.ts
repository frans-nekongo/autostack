import { props, createActionGroup, emptyProps } from "@ngrx/store";
import { GitInfo, ProjectMetadata } from "../../services/project/project-service";

export const ProjectActions = createActionGroup({
    source: 'Project',
    events: {
        'Set Project': props<{
            id: string;
            name: string;
            author?: string | null;
            description?: string | null;
            version: string;
            status?: string | null;
            metadata?: ProjectMetadata | null;
            git_info?: GitInfo | null;
        }>(),
    }
})