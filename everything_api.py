import ctypes, os
from pathlib import Path

# Load the Everything DLL
everything_dll = ctypes.WinDLL(os.path.abspath(Path('Everything64.dll')))

def search(query: str) -> list:
    directory = Path.home()
    # Prepend the directory and a wildcard to the search query
    query = f"{directory}\\*{query}*"

    # Set the search query
    everything_dll.Everything_SetSearchW(query)

    # Execute the query
    everything_dll.Everything_QueryW(True)

    # Get the number of results
    num_results = everything_dll.Everything_GetNumResults()

    results = []
    for i in range(num_results):
        # Get the result's full path and file name
        result = ctypes.create_unicode_buffer(260)  # MAX_PATH = 260
        everything_dll.Everything_GetResultFullPathNameW(i, result, len(result))
        results.append(result.value)
    
    return results
