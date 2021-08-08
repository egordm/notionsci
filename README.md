<!-- markdownlint-disable -->
<div align="center">
    <h1>NotionSci</h1>
    <p>
        <b>Collection of scientific application syncs for <a href="https://developers.notion.com">Notion API</a></b>
    </p>
    <p>
        <a href="https://pypi.org/project/notion-client"><img src="https://img.shields.io/pypi/v/notion-client.svg" alt="PyPI"></a>
        <a href="Pipfile"><img src="https://img.shields.io/pypi/pyversions/notionsci" alt="Supported Python Versions"></a>
        <a href="LICENSE"><img src="https://img.shields.io/github/license/EgorDm/notionsci" alt="License"></a>
        <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style"></a>
        <br/>
        <a href="https://github.com/EgorDm/notionsci/actions/workflows/quality.yml"><img src="https://github.com/ramnes/notion-sdk-py/actions/workflows/quality.yml/badge.svg" alt="Code Quality"></a>
        <a href="https://github.com/EgorDm/notionsci/actions/workflows/docs.yml"><img src="https://github.com/ramnes/notion-sdk-py/actions/workflows/docs.yml/badge.svg" alt="Docs"></a>
    </p>
    <br/>
</div>
<!-- markdownlint-enable -->

This cli is meant to allow syncing of scienfic/reasearch tools to notion. (Such as Zotero, ...) 

<!-- markdownlint-disable -->
## Installation
<!-- markdownlint-enable -->
```shell
pip install notionsy
```

## Usage
> Before getting started, [create an integration](https://www.notion.com/my-integrations)
> and find the token.
> [→ Learn more about authorization](https://developers.notion.com/docs/authorization).

Generate initial configuration and fill the **integration token** and other connection api keys.

```bash
notionsy config
```

### Zotero Connection
> Before getting started, [create an api key](https://www.zotero.org/settings/keys)
> and find the token.
> [→ Learn more about authorization](https://www.zotero.org/support/dev/web_api/v3/basics#authentication).

Built-in commands allow you to sync your citations to a Notion table. 
Start by forking the following [the template references page](https://ink-porch-b0f.notion.site/da043e6adba64b5b9deba02557f5f28b?v=fc76715f54134879b7dae635ffee7546).

Extract the database uuid from the url. (TODO: Elaborate)

```bash
notionsy sync zotero -db=<db uuid>
```