import { WorkspaceCodeToolbox } from '../Workspace'
import { CodeRunParams } from '../Process'

export class WorkspacePythonCodeToolbox implements WorkspaceCodeToolbox {
  public getDefaultImage(): string {
    return 'daytonaio/sdk-python:v0.49.0-2'
  }

  public getRunCommand(code: string, params?: CodeRunParams): string {
    const base64Code = Buffer.from(code).toString('base64')
    const envVars = params?.env ? Object.entries(params.env).map(([key, value]) => `${key}='${value}'`).join(' ') : ''
    const argv = params?.argv ? params.argv.join(' ') : ''

    return `sh -c '${envVars} python3 -c "exec(__import__(\\\"base64\\\").b64decode(\\\"${base64Code}\\\").decode())" ${argv}'`
  }
}
