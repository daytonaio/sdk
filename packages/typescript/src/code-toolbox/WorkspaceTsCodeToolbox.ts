import { WorkspaceCodeToolbox } from '../Workspace'

export class WorkspaceTsCodeToolbox implements WorkspaceCodeToolbox {
  public getDefaultImage(): string {
    return 'daytonaio/sdk-typescript:v0.49.0-3'
  }

  public getRunCommand(code: string): string {
    const base64Code = Buffer.from(code).toString('base64')
    return `sh -c 'echo ${base64Code} | base64 --decode | npx ts-node --compiler-options "{\\\"module\\\":\\\"CommonJS\\\"}" 2>&1 | grep -vE "npm notice|npm warn exec"'`
  }
}
