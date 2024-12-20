import { WorkspaceCodeToolbox } from '../Workspace'

export class WorkspaceTsCodeToolbox implements WorkspaceCodeToolbox {
  public getDefaultImage(): string {
    return 'daytonaio/sdk-typescript:v0.49.0-3'
  }

  public getRunCommand(code: string): string {
    const base64Code = Buffer.from(code).toString('base64')
    return `python3 -c "exec(__import__('base64').b64decode('${base64Code}').decode())"`
  }
}
