import { WorkspaceCodeToolbox } from '../Workspace'

export class WorkspacePythonCodeToolbox implements WorkspaceCodeToolbox {
  public getDefaultImage(): string {
    return 'daytonaio/sdk-python:v0.49.0-2'
  }

  public getRunCommand(code: string): string {
    const base64Code = Buffer.from(code).toString('base64')
    return `python3 -c "exec(__import__('base64').b64decode('${base64Code}').decode())"`
  }
}
