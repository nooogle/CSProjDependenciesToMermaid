import os
import xml.etree.ElementTree as ET
from enum import Enum, auto

class Orientation(Enum):
    TOP_DOWN = auto()
    LEFT_RIGHT = auto()


def _get_project_dependencies(csproj_file: str) -> list[str]:
    """
    Retrieves the project dependencies from a given csproj file.

    Args:
        csproj_file (str): The csproj file name.

    Returns:
        list: A list of project dependencies.
    """
    dependencies = []
    tree = ET.parse(csproj_file)
    root = tree.getroot()
    for item in root.iter('{http://schemas.microsoft.com/developer/msbuild/2003}ProjectReference'):
        reference = item.attrib['Include']
        dependencies.append(reference)
    return dependencies


def _process_csproj(csproj_file: str) -> str:
    """
    Generates Mermaid markdown for a given csproj file.

    Args:
        csproj_file (str): The csproj file name.

    Returns:
        str: The generated Mermaid markdown.
    """
    markdown = ""
    # project name without extension
    project_name = os.path.splitext(csproj_file)[0]
    project_name = os.path.basename(project_name)
    markdown += f"    {project_name};\n"
    dependencies = _get_project_dependencies(csproj_file)
    for dependency in dependencies:
        dependency_name = os.path.splitext(os.path.basename(dependency))[0]
        markdown += f"    {project_name} --> {dependency_name};\n"
    return markdown


def _process_subdirectories_of_this_directory(directory: str) -> str:
    """
    Generates Mermaid markdown for a graph that represents
    the dependencies between csproj files in the subdirectories
    of this directory.
    
    Args:
        directory (str): The path to the directory.
        
    Returns:
        str: The generated Mermaid markdown.
    """
    mermaid_markdown = ""
    sub_directories = [f.path for f in os.scandir(directory) if f.is_dir()]
    for sub_directory in sub_directories:
        mermaid_markdown += _process_recursively(sub_directory)
    return mermaid_markdown


def _process_projects_in_this_directory(directory: str) -> str:
    """
    Generates Mermaid markdown for a graph that represents
    the dependencies between csproj files in this  directory.
    This function does not consider subdirectories.

    Args:
        directory (str): The path to the directory.

    Returns:
        str: The generated Mermaid markdown.
    """
    mermaid_markdown = ""
    for csproj_file in os.listdir(directory):
        if csproj_file.endswith('.csproj'):
            mermaid_markdown += _process_csproj(os.path.join(directory, csproj_file))
    return mermaid_markdown


def _process_recursively(directory: str) -> str:
    """
    Generates Mermaid markdown for a graph that represents 
    the dependencies between csproj files. All csproj files in
    this folder and its subfolders are considered, recursively.

    Args:
        directory (str): The path to the directory.

    Returns:
        str: The generated Mermaid markdown.
    """
    mermaid_markdown = ""
    mermaid_markdown += _process_projects_in_this_directory(directory)
    mermaid_markdown += _process_subdirectories_of_this_directory(directory)
    return mermaid_markdown


def _create_mermaid_header(orientation: Orientation) -> str:
    """
    Creates the Mermaid header.

    Args:
        orientation (Orientation): The orientation of the graph.

    Returns:
        str: The Mermaid header.
    """
    if orientation == Orientation.TOP_DOWN:
        return "```mermaid\ngraph TD;\n"
    elif orientation == Orientation.LEFT_RIGHT:
        return "```mermaid\ngraph LR;\n"
    else:
        raise ValueError("Invalid orientation.")
    

def _create_mermaid_footer() -> str:
    """
    Creates the Mermaid footer.

    Returns:
        str: The Mermaid footer.
    """
    return "```\n"


def generate(directory: str, orientation: Orientation = Orientation.TOP_DOWN) -> str:
    """
    Generates Mermaid markdown for a graph that represents 
    the dependencies between csproj files. All csproj files in
    this folder and its subfolders are considered, recursively.

    Args:
        directory (str): The path to the directory.

    Returns:
        str: The generated Mermaid markdown.
    """
    mermaid_markdown = _create_mermaid_header(orientation)
    mermaid_markdown += _process_recursively(directory)
    mermaid_markdown += _create_mermaid_footer()
    return mermaid_markdown


def parse_orientation(arg: str) -> Orientation:
    """
    Parses the orientation from a string. Returns TOP_DOWN if the
    argument is not recognized.

    Args:
        arg (str): The string to parse. This should be one of "TD" or "LR".

    Returns:
        Orientation: The parsed orientation.
    """
    if arg.upper() == "LR":
        return Orientation.LEFT_RIGHT
    else:  # Default to TOP_DOWN if the argument is not recognized
        return Orientation.TOP_DOWN
    
# test 
if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else r'ExampleSolution\Demo'
    orientation = parse_orientation(sys.argv[2]) if len(sys.argv) > 2 else Orientation.TOP_DOWN    
    print(generate(directory, orientation))
