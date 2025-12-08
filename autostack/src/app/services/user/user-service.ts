import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';

export interface UserResults {
  fullname: string;
}

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private apollo = inject(Apollo);

  fetchUserDetails(): Observable<UserResults | null | undefined> {
    const FETCH_USER_DETAILS = gql`
      query FetchUserDetails {
        fetchUserDetails {
          fullname
        }
      }
    `;

    return this.apollo
      .query<{ fetchUserDetails: UserResults | null | undefined }>({
              query: FETCH_USER_DETAILS,
              fetchPolicy: 'network-only'
            })
            .pipe(
              map(result => result.data?.fetchUserDetails)
            );
  }
}
