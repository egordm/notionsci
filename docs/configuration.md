# Configuration

Initial run of `notionsci` cli command creates a `default.yml` config profile at:

* (Linux) `~/.config/notionsci`
* (Mac OS X) `/Library/Application Support/notionsci`
* (Windows) `%APPDATA%/Local/notionsci`

Configuration can be overridden by creating config.yml in the working directory.

## Profiles
Profiles are additional copies of the configuration to separate Notion and other connection configuration for different
tasks.
Feel free to create additional profiles such as `work.yml` or `school.yml` within the configuration directory.

The profile name can followingly be passed as `--profile=work` option.

Example:
```bash
notionsci --profile=work ...
```

## Options
The default configuration looks as follows

```yaml
version: 1
connections:
  notion:
    token: ''
  notion_unofficial:
    token_v2: ''
  zotero:
    library_id: '123456'
    library_type: 'user'
    token: ''
development:
  test_page: https://www.notion.so/NotionSci-Tests-22ecab6188d147ef83fa455e2694395b
templates:
  zotero_template: https://efficacious-alarm-7cc.notion.site/Zotero-Library-dd4b26a3b11d46518b70b5031aee8989
```