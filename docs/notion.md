# Notion
The library provides a collection of useful utilities to manage your Notion workspace.

## Setting up Connection
The main goal of this application is to use the [Official Notion API](https://developers.notion.com) whereever
possible. Unfortunately, is still in beta and misses various functions required for task automation.

Therefore, we currently use both API's, though if you do not want to use the Unofficial API it is optional.
All functions using the Unofficial API are marked as such and should in this case be avoided.

### Official API
Configuring the Official API is quite straightforward.

1. [Create an _internal_ integration](https://www.notion.com/my-integrations) for the desired workspace and find the API token.
2. [Give access](https://www.notion.so/Add-and-manage-integrations-with-the-API-910ac902372042bc9da38d48171269cd) to your integration for the desired pages within your workspace.

Update the configuration with the obtained credentials:
```yaml
...
connections:
  ...
  notion:
    token: 'your api token goes here'
```

> [→ Learn more about authorization](https://developers.notion.com/docs/authorization).

> [→ Managing intergrations](https://www.notion.so/Add-and-manage-integrations-with-the-API-910ac902372042bc9da38d48171269cd).


### Unofficial API
Configuring Unofficial Notion API requires obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so.

Update the configuration with the obtained credentials:
```yaml
...
connections:
  ...
  notion_unofficial:
    token_v2: 'your api token goes here'
```

## Duplicating Pages
It is possible to duplicate a page from the CLI which is useful for setup automation. 
This can be done by specifying source page url and target parent page url.

Example:
```bash
notionsci notion duplicate <source page url or id> <parent page url of id>
```

```bash
Usage: python -m notionsci notion duplicate [OPTIONS] SOURCE PARENT

  Duplicates given SOURCE page into a PARENT page as a child page.

  SOURCE: Source page ID or url PARENT: Destination parent page ID or url

  Requires unofficial notion api

Options:
  --target_id TEXT  Unique ID for the resulting page
  --help            Show this message and exit.
```

## Cleaning Workspace Trash
When you or the connection delete the page, it is archived and placed in the trash. 
Cleaning it manually is slow, therefore the following command can be used te permanently delete all pages in the 
trash bin of the given workspace.

Example:
```bash
notionsci notion clear-trash <workspace name>
```

```bash
Usage: python -m notionsci notion clear-trash [OPTIONS] [WORKSPACE]

  Permanently deleted all _deleted_/_trashed_ pages in a workspace

  WORKSPACE: Workspace id or name to clean. If not specified a selection
  dialog is prompted.

  Requires unofficial notion api

Options:
  --help  Show this message and exit.
```