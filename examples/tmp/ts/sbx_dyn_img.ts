import { Daytona, Image } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()

  const image = Image.base('python:3.13.2-slim-bookworm')
    .pipInstall(['ruff', 'black', 'isort', 'mypy'])
    .pipInstallFromPyproject('packages/python/pyproject.toml', {
      optionalDependencies: ['dev'],
    })
    .runCommands('mkdir -p /home/daytona/ws')
    .workdir('/home/daytona/ws')
    // .addLocalFile('packages/python/pyproject.toml', '/home/daytona/ws/pyproject.toml')
    // .addLocalDir('packages/python', '/home/daytona/ws/python-pkg')

  const sandbox = await daytona.create(
    {
      image,
      autoStopInterval: 0,
    },
    {
      onImageBuildLogs: console.log,
      timeout: 0,
    }
  )

  const response = await sandbox.process.executeCommand('ls -la')
  console.log('command: ls -la')
  console.log(response.result)

  const response2 = await sandbox.process.executeCommand('pwd')
  console.log('command: pwd')
  console.log(response2.result)

  const response3 = await sandbox.process.executeCommand('whoami')
  console.log('command: whoami')
  console.log(response3.result)

  const response4 = await sandbox.process.executeCommand('ls -la python-pkg')
  console.log('command: ls -la python-pkg')
  console.log(response4.result)

  const response5 = await sandbox.process.executeCommand('cat pyproject.toml')
  console.log('command: cat pyproject.toml')
  console.log(response5.result)

  await daytona.remove(sandbox)
}

main()
