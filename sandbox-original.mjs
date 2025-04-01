// Simple Properties section transformation
    // Find all ### Properties sections
    page.contents = page.contents.replace(
      /### Properties\s*\n\n((?:#### [^\n]+\n\n```ts\n[^\n]+;\n```\n\n(?:[\s\S]*?)(?:\*\*\*\n\n|$))*)/g,
      (match, propertiesContent) => {
        // Extract individual property blocks
        const propertyBlockRegex = /#### ([^\n]+)\n\n```ts\n([^\n]+);\n```\n\n([\s\S]*?)(?=\*\*\*\n\n|#### |$)/g

        let properties = []
        let propMatch

        // Collect all properties from this section
        while ((propMatch = propertyBlockRegex.exec(propertiesContent)) !== null) {
          const [, name, typeLine, description] = propMatch
          properties.push({ name, typeLine, description: description.trim() })
        }

        if (properties.length === 0) {
          return match // No properties found, return unchanged
        }

        // Format the properties section
        let result = '**Properties**:\n\n'

        for (const { name, typeLine, description } of properties) {
          // Extract the type from the typeLine
          const typeMatch = typeLine.match(/:\s*([^;]+)/)
          if (!typeMatch) continue

          let type = typeMatch[1].trim()

          // Remove unnecessary keywords
          type = type.replace(/readonly\s+/, '').trim()
          type = type.replace(/([*_`\[\]()<>|])/g, '\\$1')

          if (description) {
            result += `- \`${name}\` _${type}_ - ${description}\n`
          } else {
            result += `- \`${name}\` _${type}_\n`
          }
        }

        result += '\n'
        return result
      }
    )