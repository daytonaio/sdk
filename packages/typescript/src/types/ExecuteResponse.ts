import { ExecuteResponse as ClientExecuteResponse } from '@daytonaio/api-client';
import { Chart } from './Chart';

/**
 * Execution artifacts extracted from command output
 */
export interface ExecutionArtifacts {
  /**
   * Standard output from the command
   */
  stdout: string;
  
  /**
   * Charts extracted from the output
   */
  charts?: Chart[];
}

/**
 * Enhanced execution response that includes artifacts
 */
export interface ExecuteResponse extends ClientExecuteResponse {
  /**
   * Artifacts extracted from the command output
   */
  artifacts?: ExecutionArtifacts;
} 