import { Injectable, NgZone } from '@angular/core';
import { Observable } from 'rxjs';
import { createClient } from '@connectrpc/connect'
import { createConnectTransport } from '@connectrpc/connect-web';
import { Transport } from '@connectrpc/connect';
import { create } from "@bufbuild/protobuf";

import {
  DemoService as DemoServiceRef,
  GetDemoDataRequestSchema,
  GetDemoDataResponse
} from '../../generated/autostack/v1/demo_pb';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DemoService {
  private transport: Transport = createConnectTransport({
    baseUrl: environment.grpcServerUrl
  })
  private client = createClient(DemoServiceRef, this.transport)

  constructor(private ngZone: NgZone) { }

  getDemoData(requestId: string): Observable<GetDemoDataResponse> {
    const request = create(GetDemoDataRequestSchema, { requestId });

    return new Observable<GetDemoDataResponse>(observer => {
      const abortController = new AbortController();

      const processStream = async () => {
        try {
          const stream = this.client.getDemoData(request, {
            signal: abortController.signal
          });

          // Iterate over the stream responses
          for await (const response of stream) {
            // observer.next(response);
            this.ngZone.run(() => observer.next(response))
          }
          this.ngZone.run(() => observer.complete())

          observer.complete();

        } catch (error) {
          if (!observer.closed) {
            this.ngZone.run(() => {
              observer.error(error);
            });
            console.error('Error in stream:', error);
          }
        }
      };

      processStream();

      return () => {
        abortController.abort();
      };
    });
  }
}