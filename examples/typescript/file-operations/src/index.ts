import * as path from 'path'
import { Daytona } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()

  //  first, create a workspace
  const workspace = await daytona.create()

  try {
    const rootDir = await workspace.getWorkspaceRootDir()
    if (!rootDir) {
      throw new Error('Failed to get workspace root directory')
    }

    //  list files in the workspace
    const files = await workspace.fs.listFiles(rootDir)
    console.log('Files:', files)

    //  create a new directory in the workspace
    const newDir = path.join(rootDir, 'new-dir')
    await workspace.fs.createFolder(newDir, '755')

    const filePath = path.join(newDir, 'data.txt')

    //  add a new file to the workspace
    const fileContent = new File([Buffer.from('Hello, World!')], 'data.txt', {
      type: 'text/plain',
    })
    await workspace.fs.uploadFile(filePath, fileContent)

    //  search for the file we just added
    const matches = await workspace.fs.findFiles(rootDir, 'World!')
    console.log('Matches:', matches)

    //  replace the contents of the file
    await workspace.fs.replaceInFiles(
      [filePath],
      'Hello, World!',
      'Goodbye, World!',
    )

    //  read the file
    const downloadedFile = await workspace.fs.downloadFile(filePath)
    console.log('File content:', downloadedFile.toString())

    //  change the file permissions
    await workspace.fs.setFilePermissions(filePath, { mode: '777' })

    //  get file info
    const fileInfo = await workspace.fs.getFileDetails(filePath)
    console.log('File info:', fileInfo) //  should show the new permissions

    //  move the file to the new location
    await workspace.fs.moveFiles(filePath, path.join(rootDir, 'moved-data.txt'))

    //  find the file in the new location
    const searchResults = await workspace.fs.searchFiles(
      rootDir,
      'moved-data.txt',
    )
    console.log('Search results:', searchResults)

    //  delete the file
    await workspace.fs.deleteFile(path.join(rootDir, 'moved-data.txt'))
  } catch (error) {
    console.error('Error creating workspace:', error)
  } finally {
    //  cleanup
    await daytona.remove(workspace)
  }
}

main()
