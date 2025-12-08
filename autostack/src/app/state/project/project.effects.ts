import { Injectable, inject } from "@angular/core";
import { createEffect, Actions, ofType } from "@ngrx/effects";
import { switchMap, of, tap, map } from "rxjs";
import { ProjectActions } from "./project.actions";

@Injectable()
export class ProjectEffects {
    private actions$ = inject(Actions);

    // setProject = createEffect(() => 
    //     this.actions$.pipe(
    //         ofType(ProjectActions.setProject),
    //         switchMap(() => {

    //         })
    //     )
    // )
}