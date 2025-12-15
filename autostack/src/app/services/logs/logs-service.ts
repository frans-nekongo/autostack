import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';

export interface ActivityLogResponse {
  activityType: string;
  createdAt: string;
  projectId: string;
  projectName: string;
  chatId: string;
  details: any;
}

@Injectable({
  providedIn: 'root',
})
export class LogsService {
  private apollo = inject(Apollo);

  private FETCH_ALL_ACTIVITY_LOGS = gql`
    query FetchAllActivityLogs {
      fetchAllActivityLogs {
        activityType
        createdAt
        projectId
        projectName
        chatId
        details
      }
    }
  `;

  fetchAllActivityLogs(): Observable<ActivityLogResponse[]> {
    return this.apollo
      .query<{ fetchAllActivityLogs: ActivityLogResponse[] }>({
        query: this.FETCH_ALL_ACTIVITY_LOGS,
        fetchPolicy: 'network-only',
      })
      .pipe(
        map((result) => {
          const data = result.data?.fetchAllActivityLogs;

          if (!data) return [];
          return Array.isArray(data) ? data : [data];
        })
      );
  }
}
