"""Generate virtual files for mkdocs."""

import mkdocs_gen_files


def docs_stub(module_name):
    return f"::: notionsci.{module_name}\
        \n\trendering:\n\t\tshow_root_heading: true\n\t\tshow_source: true"


virtual_files = {
    "index.md": "--8<-- 'README.md'",
    # "reference/config.md": docs_stub("config"),
    "contributing.md": "--8<-- '.github/CONTRIBUTING.md'",
    "license.md": "```text\n--8<-- 'LICENSE'\n```",
    "reference/sync.md": docs_stub("sync"),
    "reference/connections/notion.md": docs_stub("connections.notion"),
    "reference/connections/notion_unofficial.md": docs_stub(
        "connections.notion_unofficial"
    ),
    "reference/connections/zotero.md": docs_stub("connections.zotero"),
}

for file_name, content in virtual_files.items():
    with mkdocs_gen_files.open(file_name, "w") as file:
        print(content, file=file)
