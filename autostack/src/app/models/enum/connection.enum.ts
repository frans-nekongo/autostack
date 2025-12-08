export enum ConnectionType {
  API_CALL = 'api_call',
  DATA_FLOW = 'data_flow',
  DEPENDENCY = 'dependency',
  AUTHENTICATION = 'authentication',
  MESSAGE_QUEUE = 'message_queue',
  DATABASE_QUERY = 'database_query',
  FILE_TRANSFER = 'file_transfer',
  CACHE_ACCESS = 'cache_access',
  EVENT_STREAM = 'event_stream',
  SYNCHRONOUS = 'synchronous',
  ASYNCHRONOUS = 'asynchronous'
}