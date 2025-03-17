import * as path from 'path'
import { Daytona } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()

  //  first, create a sandbox
  const sandbox = await daytona.create()

  try {
    const rootDir = await sandbox.getUserRootDir()
    if (!rootDir) {
      throw new Error('Failed to get sandbox root directory')
    }

    //  list files in the sandbox
    const files = await sandbox.fs.listFiles(rootDir)
    console.log('Files:', files)

    //  create a new directory in the sandbox
    const newDir = path.join(rootDir, 'new-dir')
    await sandbox.fs.createFolder(newDir, '755')

    const filePath = path.join(newDir, 'data.txt')

    //  add a new file to the sandbox
    const fileContent = new File([Buffer.from('Hello, World!')], 'data.txt', {
      type: 'text/plain',
    })
    await sandbox.fs.uploadFile(filePath, fileContent)

    //  search for the file we just added
    const matches = await sandbox.fs.findFiles(rootDir, 'World!')
    console.log('Matches:', matches)

    //  replace the contents of the file
    await sandbox.fs.replaceInFiles(
      [filePath],
      'Hello, World!',
      'Goodbye, World!',
    )

    //  read the file
    const downloadedFile = await sandbox.fs.downloadFile(filePath)
    console.log('File content:', downloadedFile.toString())

    //  change the file permissions
    await sandbox.fs.setFilePermissions(filePath, { mode: '777' })

    //  get file info
    const fileInfo = await sandbox.fs.getFileDetails(filePath)
    console.log('File info:', fileInfo) //  should show the new permissions

    //  move the file to the new location
    await sandbox.fs.moveFiles(filePath, path.join(rootDir, 'moved-data.txt'))

    //  find the file in the new location
    const searchResults = await sandbox.fs.searchFiles(
      rootDir,
      'moved-data.txt',
    )
    console.log('Search results:', searchResults)

    //  delete the file
    await sandbox.fs.deleteFile(path.join(rootDir, 'moved-data.txt'))
  } catch (error) {
    console.error('Error creating sandbox:', error)
  } finally {
    //  cleanup
    await daytona.remove(sandbox)
  }
}

main()
