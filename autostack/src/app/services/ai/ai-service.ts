import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';
export enum JobStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export interface JobResult {
  id: string;
  status: JobStatus;
  result?: string;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface JobCreated {
  jobId: string;
  message: string;
}

const CREATE_PROJECT_DESCRIPTION = gql`
  mutation CreateProjectDescription($userInput: String!) {
    createProjectDescription(userInput: $userInput) {
      jobId
      message
    }
  }
`;

const GET_JOB = gql`
  query GetJob($jobId: String!) {
    getJob(jobId: $jobId) {
      id
      status
      result
      error
      createdAt
      completedAt
    }
  }
`;

const SUBSCRIBE_TO_JOB = gql`
  subscription SubscribeToJob($jobId: String!) {
    subscribeToJob(jobId: $jobId) {
      id
      status
      result
      error
      createdAt
      completedAt
    }
  }
`;

@Injectable({
  providedIn: 'root'
})
export class AiService {
  private apollo = inject(Apollo)

  createProjectDescription(userInput: string): Observable<JobCreated> {
    return this.apollo
      .mutate<{ createProjectDescription: JobCreated }>({
        mutation: CREATE_PROJECT_DESCRIPTION,
        variables: { userInput }
      })
      .pipe(
        map(result => result.data!.createProjectDescription)
      );
  }

  getJob(jobId: string): Observable<JobResult | null | undefined> {
    return this.apollo
      .query<{ getJob: JobResult | null | undefined }>({
        query: GET_JOB,
        variables: { jobId },
        fetchPolicy: 'network-only'
      })
      .pipe(
        map(result  => result.data?.getJob)
      );
  }

  subscribeToJob(jobId: string): Observable<JobResult> {
    return this.apollo
      .subscribe<{ subscribeToJob: JobResult }>({
        query: SUBSCRIBE_TO_JOB,
        variables: { jobId }
      })
      .pipe(
        map(result => result.data!.subscribeToJob)
      );
  }
}
