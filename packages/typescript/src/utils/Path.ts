import * as _path from 'path'

export function prefixRelativePath(prefix: string, path?: string) {
  let result = path
  if (!result || result === '~') {
    result = prefix
  } else if (path && path.startsWith(prefix.replace(/^\/+/, ''))) {
    result = path
  } else if (path && !_path.isAbsolute(path)) {
    result = _path.join(prefix, path)
  }
  return result
}
