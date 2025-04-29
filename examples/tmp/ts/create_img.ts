import { Daytona, Image } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()

  const image = Image.base('python:3.13.2-slim-bookworm')
    .runCommands('pip install uuid black')
    .pipInstallFromPyproject('packages/python/pyproject.toml', {
      optionalDependencies: ['dev'],
    })
    .addLocalDir('packages/python', '/home/daytona/ws/python-pkg')
    .addLocalFile('.devcontainer/devcontainer.json', '/home/daytona/.devcontainer/devcontainer.json')

  await daytona.createImage('test-image:0.0.25', image, { verbose: true })
}

main()
