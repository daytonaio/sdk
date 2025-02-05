import { Daytona, Workspace } from '@daytonaio/sdk'

async function basicExec(workspace: Workspace) {
  //  run some python code directly
  const codeResult = await workspace.process.codeRun('console.log("Hello World from code!")')
  if (codeResult.exitCode !== 0) {
    console.error('Error running code:', codeResult.exitCode)
  } else {
    console.log(codeResult.result)
  }

  //  run os command
  const cmdResult = await workspace.process.executeCommand(
    'echo "Hello World from CMD!"',
  )
  if (cmdResult.exitCode !== 0) {
    console.error('Error running code:', cmdResult.exitCode)
  } else {
    console.log(cmdResult.result)
  }
}

async function sessionExec(workspace: Workspace) {
    //  exec session
    //  session allows for multiple commands to be executed in the same context
    await workspace.process.createSession('exec-session-1')

    //  get the session details any time
    const session = await workspace.process.getSession('exec-session-1')
    console.log('session: ', session)

    //  execute a first command in the session
    const command =await workspace.process.executeSessionCommand('exec-session-1', {
      command: 'export FOO=BAR',
    })

    //  get the session details again to see the command has been executed
    const sessionUpdated = await workspace.process.getSession('exec-session-1')
    console.log('sessionUpdated: ', sessionUpdated)

    //  get the command details
    const sessionCommand = await workspace.process.getSessionCommand('exec-session-1', command.cmdId!)
    console.log('sessionCommand: ', sessionCommand)

    //  execute a second command in the session and see that the environment variable is set
    const response = await workspace.process.executeSessionCommand('exec-session-1', {
      command: 'echo $FOO',
    })
    console.log(`FOO=${response.output}`)

    //  we can also get the logs for the command any time after it is executed
    const logs = await workspace.process.getSessionCommandLogs('exec-session-1', response.cmdId!)
    console.log('logs for command: ',logs)

    //  we can also delete the session
    await workspace.process.deleteSession('exec-session-1')
}

async function main() {
  const daytona = new Daytona()

  //  first, create a workspace
  const workspace = await daytona.create({
    language: 'typescript',

  })

  try {
    await basicExec(workspace)
    await sessionExec(workspace)
  
  } catch (error) {
    console.error('Error creating workspace:', error)
  } finally {
    //  cleanup
    await daytona.remove(workspace)
  }
}

main()
