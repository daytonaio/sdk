import { Daytona, Sandbox } from '@daytonaio/sdk'
import 'dotenv/config'

async function sessionExec(sandbox: Sandbox) {
  await sandbox.process.createSession('exec-session-1')
  await sandbox.process.getSession('exec-session-1')
  // console.log('session: ', session)

  const command = await sandbox.process.executeSessionCommand('exec-session-1', {
    command: 'counter=1; while (( counter <= 3 )); do echo "Count: $counter"; ((counter++)); sleep 2; done',
    async: true,
  })

  try {
    await sandbox.process.getSessionCommandLogs('exec-session-1', command.cmdId!, (chunk) => {
      console.log('=== chunk: ', chunk)
    })
  } catch (error) {
    console.log('error: ', error)
  }

  const result = await sandbox.process.getSession('exec-session-1')
  console.log('result: ', result)

  const updatedCommand = await sandbox.process.getSessionCommand('exec-session-1', command.cmdId!)
  console.log('updatedCommand: ', updatedCommand)

  const commandLogsSync = await sandbox.process.getSessionCommandLogs('exec-session-1', command.cmdId!)
  console.log('commandLogsSync: ', commandLogsSync)
}

async function main() {
  const daytona = new Daytona({
    apiKey: 'dtn_27573ca37b2bcefc0e3398be68d4dc381f326f3299aa183df6572a8a10144bd1',
    serverUrl: 'https://stage.daytona.work/api',
    target: 'eu',
  })

  //  first, create a sandbox
  const sandbox = await daytona.create({
    language: 'typescript',
  })

  try {
    await sessionExec(sandbox)
  } catch (error) {
    console.error('Error creating sandbox:', error)
  } finally {
    //  cleanup
    console.log('cleanup')
    await daytona.remove(sandbox)
  }
}

main()
