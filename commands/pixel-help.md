---
description: Show plugin help from maintained command and skill references
argument-hint: [palettes|export|animation|setup|shortcuts]
allowed-tools: Read
---

# /pixel-help

Read `$ARGUMENTS` as an optional help topic. Use maintained documents rather than a duplicate tool list:

- Overview/shortcuts: [commands](README.md) and [skills](../skills/README.md).
- Palettes: [palette command](pixel-palette.md) and [preset data](../config/palettes.json).
- Export: [export command](pixel-export.md) and [format limits](../skills/pixel-art-exporter/export-formats.md).
- Animation: [animator](../skills/pixel-art-animator/SKILL.md), including one-based frames and empty-target native links.
- Setup/development: [configuration](../config/README.md) and [local MCP build](../docs/LOCAL_MCP.md).
- Exact tools and response fields: [MCP contract](../docs/MCP_TOOLS.md).

Give concise usage and a relevant example. Plugin options such as scale/FPS are workflows using several MCP calls; do not describe them as server export parameters. Read the current version from .claude-plugin/plugin.json when reporting it.
