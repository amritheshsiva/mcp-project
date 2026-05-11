from server.github_client import list_repository_files
def get_repo_files():
    data = list_repository_files()
    files = []
    for item in data:
        files.append(item["name"])
    return {"files": files}