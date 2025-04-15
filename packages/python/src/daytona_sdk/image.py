import os
import re
import glob
import shlex
from pathlib import Path
from typing import Union

class Image():
    _name: str = None
    _dockerfile: str = None
    _propagate: bool = False
    _contexts: list[tuple[str, str]] = []

    def name(self) -> str:
        return self._name

    def dockerfile(self) -> str:
        return self._dockerfile

    def propagate(self) -> bool:
        return self._propagate

    def set_name(self, name: str) -> "Image":
        self._name = name
        return self

    def set_propagate(self, propagate: bool = True) -> "Image":
        self._propagate = propagate
        return self

    @staticmethod
    def from_dockerfile(path: Union[str, Path]) -> "Image":
        path = Path(path)
        dockerfile = path.read_text()
        img = Image()
        img._dockerfile = dockerfile

        # remove dockerfile filename from path
        pure_path = str(path).removesuffix(path.name)

        for context_path in Image._extract_copy_sources(dockerfile, pure_path):
            arcname = context_path.removeprefix(pure_path)
            img._contexts.append((context_path, arcname))

        return img

    @staticmethod
    def _extract_copy_sources(dockerfile_content, path_prefix="") -> list[str]:
        """
        Extracts all source paths from COPY commands in a Dockerfile.
        
        Args:
            dockerfile_content (str): The Dockerfile content as a string
            path_prefix (str): Prefix to add to relative paths (not added to absolute paths)
            
        Returns:
            list: All source file paths that match the patterns in COPY commands
        """
        sources = []
        
        # Split the Dockerfile into lines
        lines = dockerfile_content.split('\n')
        
        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Check if the line contains a COPY command (at the beginning of the line)
            if re.match(r'^\s*COPY\s', line):
                # Extract the sources from the COPY command
                command_parts = Image._parse_copy_command(line)
                
                if command_parts:
                    # Get source paths from the parsed command parts
                    for source in command_parts['sources']:
                        # Handle absolute and relative paths differently
                        if source.startswith('/'):
                            # Absolute path - use as is
                            full_path_pattern = source
                        else:
                            # Relative path - add prefix
                            full_path_pattern = os.path.join(path_prefix, source)
                        
                        # Handle glob patterns
                        matching_files = glob.glob(full_path_pattern)
                        
                        if matching_files:
                            sources.extend(matching_files)
                        else:
                            # If no files match, include the pattern anyway
                            sources.append(full_path_pattern)
        
        return sources

    @staticmethod
    def _parse_copy_command(line):
        """
        Parses a COPY command line and extracts the source and destination parts.
        
        Args:
            line (str): A line containing a COPY command
            
        Returns:
            dict: A dictionary with 'sources' and 'dest' keys or None if parsing fails
        """
        # Remove initial "COPY" and strip whitespace
        parts = line.strip()[4:].strip()
        
        # Handle JSON array format: COPY ["src1", "src2", "dest"]
        if parts.startswith('['):
            try:
                # Parse the JSON-like array format
                elements = shlex.split(parts.replace('[', '').replace(']', ''))
                if len(elements) < 2:
                    return None
                    
                return {
                    'sources': elements[:-1],
                    'dest': elements[-1]
                }
            except:
                return None
        
        # Handle regular format with possible flags
        parts = shlex.split(parts)
        
        # Extract flags like --chown, --chmod, --from
        sources_start_idx = 0
        for i, part in enumerate(parts):
            if part.startswith('--'):
                # Skip the flag and its value if it has one
                if '=' not in part and i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                    sources_start_idx = i + 2
                else:
                    sources_start_idx = i + 1
            else:
                break
        
        # After skipping flags, we need at least one source and one destination
        if len(parts) - sources_start_idx < 2:
            return None
            
        return {
            'sources': parts[sources_start_idx:-1],
            'dest': parts[-1]
        }
