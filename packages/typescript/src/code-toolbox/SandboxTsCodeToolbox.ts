import { CodeRunParams } from '../Process'

export class SandboxTsCodeToolbox {
  public static getRunCommand(code: string, params?: CodeRunParams): string {
    const base64Code = Buffer.from(code).toString('base64')
    const envVars = params?.env
      ? Object.entries(params.env)
          .map(([key, value]) => `${key}='${value}'`)
          .join(' ')
      : ''
    const argv = params?.argv ? params.argv.join(' ') : ''

    return `sh -c 'echo ${base64Code} | base64 --decode | ${envVars} npx ts-node -O "{\\\"module\\\":\\\"CommonJS\\\"}" -e "$(cat)" x ${argv} 2>&1 | grep -vE "npm notice|npm warn exec"'`
  }
}
