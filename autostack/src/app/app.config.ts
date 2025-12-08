import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection, isDevMode, inject } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';
import { provideStoreDevtools } from '@ngrx/store-devtools';
import { reducers } from './state/app/app.reducers';
import { appEffects } from './state/app/app.effects';
import { providePersistStore, localStorageStrategy  } from '@ngrx-addons/persist-state';
import { BeforeAppInit } from '@ngrx-addons/common';
import { PROJECT_FEATURE_KEY } from './state/project/project.reducer';
import { provideHttpClient } from '@angular/common/http';
import { provideApollo } from 'apollo-angular';
import { HttpLink } from 'apollo-angular/http';
import { InMemoryCache } from '@apollo/client';
import { CHAT_FEATURE_KEY } from './state/chat/chat.reducer';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideStore(reducers),
    provideEffects(appEffects),
    providePersistStore({
      states: [
        {key: PROJECT_FEATURE_KEY, storage: localStorageStrategy},
        {key: CHAT_FEATURE_KEY, storage: localStorageStrategy}
      ],
      strategy: BeforeAppInit
    }),
    provideStoreDevtools({ maxAge: 25, logOnly: !isDevMode() }), provideHttpClient(), provideApollo(() => {
      const httpLink = inject(HttpLink);

      return {
        link: httpLink.create({
          uri: '<%= endpoint %>',
        }),
        cache: new InMemoryCache(),
      };
    }),
    provideHttpClient(),
    provideApollo(() => {
      const httpLink = inject(HttpLink);

      return {
        link: httpLink.create({uri: "http://localhost:8020/graphql"}),
        cache: new InMemoryCache()
      }
    })
]
};
