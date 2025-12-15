import { ModuleWithProviders, NgModule } from '@angular/core';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { projectReducer } from './project/project.reducer';
import { ProjectEffects } from './project/project.effects';
import { ChatEffects } from './chat/chat.effects';
import { chatReducer } from './chat/chat.reducer';
import { logsReducer } from './logs/logs.reducer';
import { LogEffects } from './logs/logs.effects';

@NgModule()
export class SharedStateModule {
  static forRoot(): ModuleWithProviders<SharedStateModule> {
    return {
      ngModule: SharedStateModule,
      providers: []
    };
  }
}

export const stateConfig = {
  reducers: {
    project: projectReducer,
    chat: chatReducer,
    log: logsReducer
  },
  effects: [
    ProjectEffects,
    ChatEffects,
    LogEffects
  ]
};

export function configureStore() {
  return [
    StoreModule.forRoot(stateConfig.reducers),
    EffectsModule.forRoot(stateConfig.effects),
    StoreDevtoolsModule.instrument({
      maxAge: 25,
      logOnly: true,
    }),
  ];
}