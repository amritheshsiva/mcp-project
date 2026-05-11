from server.github_client import (
    GitHubError,
    GitHubFile,
    read_multiple_files,
    read_repository_file,
)


def read_file(file_path: str) -> dict:
    """
    Read a single file from the repository.

    Returns a dict with keys: name, path, content
    On failure, returns a dict with keys: error, status_code, path
    """
    result = read_repository_file(file_path)

    if isinstance(result, GitHubError):
        return {
            "error": result.message,
            "status_code": result.status_code,
            "path": file_path,
        }

    return {
        "name": result.name,
        "path": result.path,
        "content": result.content,
    }


def read_files(file_paths: list[str]) -> list[dict]:
    """
    Read multiple files from the repository in one call.

    Returns a list of result dicts (same shape as read_file).
    """
    results = read_multiple_files(file_paths)

    output = []
    for path, result in results.items():
        if isinstance(result, GitHubError):
            output.append({
                "error": result.message,
                "status_code": result.status_code,
                "path": path,
            })
        else:
            output.append({
                "name": result.name,
                "path": result.path,
                "content": result.content,
            })

    return output