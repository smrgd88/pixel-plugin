# Contributing

Contributions are welcome! This document provides guidelines for contributing to the Aseprite Pixel Art Plugin.

## Reporting Issues

Use the GitHub issue tracker to report bugs or suggest features:
- **Bugs**: Include plugin version, Aseprite version, OS, steps to reproduce
- **Features**: Describe the use case and proposed solution

## Submitting Changes

1. Fork the repository
2. Create a dedicated task branch/worktree from latest origin/develop (e.g. fix/shared-mcp-sync); never add feature commits directly to main/develop
3. Make your changes
4. Run tests: `./bin/test-plugin.sh`
5. Commit with conventional commit format: `feat(scope): description`
6. Push and create a pull request

## Development Setup

### Prerequisites
- Aseprite v1.3.0+
- Go 1.25+ (for building pixel-mcp binaries)
- Bash (for test scripts)
- Python 3 and bin/requirements-test.txt (for JSON Schema validation)

### Local Development

Follow [local MCP development](docs/LOCAL_MCP.md) to build a pinned source commit without writing to another checkout. Use PIXEL_MCP_BINARY for a local binary; --release updates all bundled targets and checksums together. Install test dependencies, run the default suite, and run the separate real-Aseprite smoke test before release. No develop/main merge is implied by a code change.

## Project Structure

```
pixel-plugin-plugin/
├── .claude-plugin/       # Plugin metadata
├── skills/               # Model-invoked Skills
├── commands/             # User-invoked slash commands
├── bin/                  # MCP server binaries and test scripts
├── config/               # Configuration templates
└── docs/                 # Documentation
```

## Coding Guidelines

### Skills (Markdown + YAML)
- Must have SKILL.md with valid YAML frontmatter
- Include: name, description, allowed-tools
- Provide clear instructions and examples

### Commands (Markdown + YAML)
- Must have valid YAML frontmatter
- Include: description, argument-hint, allowed-tools
- Document usage and examples

### Commit Format
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<optional body>
```

**Types**: feat, fix, docs, test, chore, refactor
**Scopes**: skills, commands, mcp, config, docs, testing

## Testing

Run the full test suite before submitting:
```bash
./bin/test-plugin.sh
```

Individual test suites:
- `./bin/validate-skills.sh` - Skills validation
- `./bin/validate-commands.sh` - Commands validation
- `./bin/test-mcp.sh` - MCP file/package validation

## Questions?

Check existing [issues](https://github.com/willibrandon/pixel-plugin-plugin/issues) or open a new one.

Thank you for contributing!
