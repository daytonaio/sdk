import { Daytona } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()
  const volume = await daytona.volume.get('test-volume-ts') // daytona.volume.create('test-volume-ts')
  const sandbox1 = await daytona.create({
    volumes: [
      {
        volumeId: volume.id,
        mountPath: '/home/daytona/volume-dir',
      },
    ],
  })
  const sandbox2 = await daytona.create({
    volumes: [
      {
        volumeId: volume.id,
        mountPath: '/home/daytona/other-volume-dir',
      },
    ],
  })
  try {
    await sandbox1.process.executeCommand(
      'cd /home/daytona/volume-dir && echo "Hello World from exec in TS!" > test.txt'
    )

    const response = await sandbox2.process.executeCommand('cd /home/daytona/other-volume-dir && cat test.txt')
    console.log(response.artifacts!.stdout)
  } catch (error) {
    console.error('Error executing commands:', error)
  } finally {
    //  cleanup
    await daytona.delete(sandbox1)
    await daytona.delete(sandbox2)
    await daytona.volume.delete(volume)
  }
}

main()
