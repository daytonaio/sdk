import * as path from 'path'
import { Daytona } from '@daytonaio/sdk'

async function main() {
  const daytona = new Daytona()

  //  first, create a workspace
  const workspace = await daytona.create({
    language: 'typescript'
  })

  try {
    const rootDir = await workspace.getWorkspaceRootDir()
    if (!rootDir) {
      throw new Error('Failed to get workspace root directory')
    }

    const projectDir = path.join(rootDir, 'learn-typescript')
    
    //  clone the repository
    await workspace.git.clone(
      'https://github.com/panaverse/learn-typescript',
      projectDir,
      'master',
    )

    //  search for the file we want to work on
    const matches = await workspace.fs.findFiles(
      projectDir,
      'var obj1 = new Base();',
    )
    console.log('Matches:', matches)

    //  start the language server
    const lsp = workspace.createLspServer('typescript', projectDir)
    await lsp.start()

    //  notify the language server of the document we want to work on
    await lsp.didOpen(matches[0].file!)

    //  get symbols in the document
    const symbols = await lsp.documentSymbols(matches[0].file!)
    console.log('Symbols:', symbols)

    //  fix the error in the document
    await workspace.fs.replaceInFiles(
      [matches[0].file!],
      'var obj1 = new Base();',
      'var obj1 = new E();',
    )

    //  notify the language server of the document change
    await lsp.didClose(matches[0].file!)
    await lsp.didOpen(matches[0].file!)

    //  get completions at a specific position
    const completions = await lsp.completions(matches[0].file!, {
      line: 12,
      character: 18,
    })
    console.log('Completions:', completions)
  } catch (error) {
    console.error('Error creating workspace:', error)
  } finally {
    //  cleanup
    await daytona.remove(workspace)
  }
}

main()
