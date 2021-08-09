<!-- markdownlint-disable -->
<div align="center">
    <h1>NotionSci</h1>
    <p>
        <b>Collection of scientific app/tool syncs for <a href="https://developers.notion.com">Notion API</a></b>
    </p>
    <p>
        <a href="https://pypi.org/project/notionsci"><img src="https://img.shields.io/pypi/v/notionsci.svg" alt="PyPI"></a>
        <a href="Pipfile"><img src="https://img.shields.io/pypi/pyversions/notionsci" alt="Supported Python Versions"></a>
        <a href="LICENSE"><img src="https://img.shields.io/github/license/EgorDm/notionsci" alt="License"></a>
        <a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style"></a>
        <br/>
        <a href="https://github.com/EgorDm/notionsci/actions/workflows/test.yml"><img src="https://github.com/EgorDm/notionsci/actions/workflows/test.yml/badge.svg" alt="Test"></a>
    </p>
    <br/>
</div>
<!-- markdownlint-enable -->

This cli is meant to allow syncing of scienfic/reasearch tools to notion. (Such as Zotero, ...) 

<!-- markdownlint-disable -->
## Installation
<!-- markdownlint-enable -->
```shell
pip install notionsci
```

## Usage
> Before getting started, [create an integration](https://www.notion.com/my-integrations)
> and find the token.
> [→ Learn more about authorization](https://developers.notion.com/docs/authorization).

Generate initial configuration and fill the **integration token** and other connection api keys.

```bash
notionsci config
```

The config.yml should be created at `~/.config/notionsci` (linux) 
and `/Library/Application Support/notionsci` (Mac OS X).

```yaml
connections:
  notion:
    token: 'token'
  zotero:
    library_id: '123456'
    library_type: 'user'
    token: 'token'
```

### Zotero Connection
> Before getting started, [create an api key](https://www.zotero.org/settings/keys)
> and find the token.
> [→ Learn more about authorization](https://www.zotero.org/support/dev/web_api/v3/basics#authentication).

Built-in commands allow you to sync your citations to a Notion table. 
Start by forking the following [the template references page](https://ink-porch-b0f.notion.site/da043e6adba64b5b9deba02557f5f28b?v=fc76715f54134879b7dae635ffee7546).

Extract the database uuid from the url. (TODO: Elaborate)

```bash
notionsci sync zotero -db=<db uuid>
```