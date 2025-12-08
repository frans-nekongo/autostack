import { Injectable, inject } from "@angular/core";
import { Store } from "@ngrx/store";
import { Observable, map } from "rxjs";

import { ProjectActions } from "./project.actions";
import * as ProjectSelectors from './project.selectors';
import { GitInfo, ProjectMetadata } from "../../services/project/project-service";

@Injectable({
    providedIn: 'root'
})
export class ProjectFacade {
    private readonly store = inject(Store);

    project$ = this.store.select(ProjectSelectors.selectProject);
    loading$ = this.store.select(ProjectSelectors.selectProjectLoading);
    error$ = this.store.select(ProjectSelectors.selectProjectError);

    hasError$ = this.error$.pipe(
        map(error => !!error)
    );

    setProject(
        id: string,
        name: string,
        author: string | null = null,
        description: string | null = null,
        version: string,
        status: string | null = null,
        metadata: ProjectMetadata | null = null,
        git_info: GitInfo | null = null
    ): void {
        this.store.dispatch(ProjectActions.setProject({
            id,
            name,
            author,
            description,
            version,
            status,
            metadata,
            git_info
        }))
    }
}