import { Injectable } from "@angular/core";
import { ProjectEffects } from "../project/project.effects";
import { ChatEffects } from "../chat/chat.effects";

@Injectable()
export class AppEffects {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    constructor() {}
}

export const appEffects = [
    ProjectEffects,
    ChatEffects
]