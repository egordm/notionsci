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

## Features
* [Zotero Synchronization](zotero.md)
    * [References Sync (One Way)](zotero.md#references-sync-one-way)
    * [Collections Sync (One Way)](zotero.md#collections-sync-one-way)
* [Useful Notion Tools](notion.md)
    * [Page Duplication](notion.md#duplicating-pages)
    * [Workspace Trash Cleaning](notion.md#cleaning-workspace-trash)

## Quick Start
> Before getting started, configure [Notion intergration](notion.md#setting-up-connection)
> and [Zotero integration](zotero.md#setting-up-connection).

Duplicate the [Zotero Library Template](https://www.notion.so/Zotero-Library-dd4b26a3b11d46518b70b5031aee8989)
and synchronize the Zotero Collections with:

```bash
notionsci sync zotero collections <Url of your Zotero Collections page>
```

and the References with:

```bash
notionsci sync zotero refs <Url of your Zotero References page>
```

## [Documentation](https://egordm.github.io/notionsci/)