export interface GeneratedProject {
  name: string;
  author: string;
  description: string;
  version?: string;
}

export interface GeneratedTechnology {
  name: string;
  type: string;
  version?: string;
  environment_variables?: string;
}

export interface GeneratedComponent {
  component_id: string;
  name: string;
  technology: string;
  framework: string;
  port?: number;
  environment_variables?: Record<string, string>;
  dependencies?: string[];
  type: string
}

export interface GeneratedConnection {
  source: string;
  target: string;
  type?: string;
  port?: number;
}

export interface GeneratedSchema {
  project: GeneratedProject;
  technologies?: GeneratedTechnology[];
  components?: GeneratedComponent[];
  connections?: GeneratedConnection[];
}

export enum TECHNOLOGY_CATEGORY {
    RUNTIME = "runtime" ,
    DATABASE = "database",        
    CACHE = "cache",     
    QUEUE = "queue",          
    SERVICE = "service" 
}

export enum COMPONENT_TYPE {
    DATABASE = "database",
    CACHE = "cache",
    API = "api",
    WEB = "web",
    GATEWAY = "gateway",
    EXTERNAL = "external"
}