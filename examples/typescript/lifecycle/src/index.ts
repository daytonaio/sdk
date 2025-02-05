import { Daytona } from '@daytonaio/sdk'
import { inspect } from 'util'

async function main() {
  const daytona = new Daytona()

  console.log("Creating workspace")
  const workspace = await daytona.create()
  console.log("Workspace created")

  await workspace.setLabels({
    'public': 'true',
  })

  console.log("Stopping workspace")
  await workspace.stop()
  console.log("Workspace stopped")

  console.log("Starting workspace")
  await workspace.start()
  console.log("Workspace started")

  console.log("Getting existing workspace")
  const existingWorkspace = await daytona.get(workspace.id)
  console.log("Got existing workspace")

  const response = await existingWorkspace.process.executeCommand(
    'echo "Hello World from exec!"',
    "/home/daytona",
    10
  )
  if (response.exitCode !== 0) {
    console.error(`Error: ${response.exitCode} ${response.result}`)
  } else {
    console.log(response.result)
  }

  const workspaces = await daytona.list()
  console.log("Total workspaces count:", workspaces.length)
  // Use util.inspect to pretty print the workspace info like Python's pprint
  console.log(inspect(await workspaces[0].info(), { depth: null, colors: true }))

  console.log("Removing workspace")
  await workspace.delete()
  console.log("Workspace removed")
}

main().catch(console.error)
