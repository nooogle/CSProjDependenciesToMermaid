# standalone test

from csproj_dependencies_to_mermaid import generate, Orientation

solution_folder = r'ExampleSolution\Demo'
mermaid_markdown = generate(solution_folder, orientation=Orientation.TOP_DOWN)
print(mermaid_markdown)
