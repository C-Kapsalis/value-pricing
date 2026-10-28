#!/bin/sh
# Build the downloadable skill and plugin archives into dist/.
#
#   value-pricing-skill.zip  Agent Skill folder for Claude, ChatGPT, Codex,
#                            and other Agent Skills compatible clients.
#   value-pricing-plugin.zip Claude Code plugin bundle.
#   value-pricing-codex.zip  Codex plugin bundle for manual installation.
#   value-pricing-openai.zip Portable, skills-only public-directory package.
#
# Requires POSIX sh and zip. Run from anywhere: sh scripts/package.sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DIST="$ROOT/dist"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT INT TERM
command -v zip >/dev/null 2>&1 || { echo "package.sh: zip not found" >&2; exit 1; }
rm -rf "$DIST"
mkdir -p "$DIST" "$STAGE/skill/value-pricing" "$STAGE/claude" "$STAGE/codex" "$STAGE/openai"

cp -R "$ROOT/skills/value-pricing/." "$STAGE/skill/value-pricing/"
cp "$ROOT/LICENSE" "$STAGE/skill/value-pricing/LICENSE"
find "$STAGE" \( -name '.DS_Store' -o -name '__pycache__' -o -name '*.pyc' \) -prune -exec rm -rf {} +
(cd "$STAGE/skill" && zip -qrX "$DIST/value-pricing-skill.zip" .)

# Claude Code plugin.
mkdir -p "$STAGE/claude/.claude-plugin" "$STAGE/claude/skills" "$STAGE/claude/agents" "$STAGE/claude/commands"
cp "$ROOT/.claude-plugin/plugin.json" "$STAGE/claude/.claude-plugin/"
cp -R "$ROOT/skills/value-pricing" "$STAGE/claude/skills/"
cp -R "$ROOT/agents/." "$STAGE/claude/agents/"
cp -R "$ROOT/commands/." "$STAGE/claude/commands/"
cp "$ROOT/README.md" "$ROOT/LICENSE" "$STAGE/claude/"
(cd "$STAGE/claude" && zip -qrX "$DIST/value-pricing-plugin.zip" .)

# Codex plugin (no lifecycle hooks or MCP server).
mkdir -p "$STAGE/codex/.codex-plugin" "$STAGE/codex/skills" "$STAGE/codex/agents" "$STAGE/codex/commands"
cp "$ROOT/.codex-plugin/plugin.json" "$STAGE/codex/.codex-plugin/"
cp -R "$ROOT/skills/value-pricing" "$STAGE/codex/skills/"
cp -R "$ROOT/agents/." "$STAGE/codex/agents/"
cp -R "$ROOT/commands/." "$STAGE/codex/commands/"
mkdir -p "$STAGE/codex/assets"
cp "$ROOT/assets/value-pricing-icon.svg" "$STAGE/codex/assets/"
cp "$ROOT/README.md" "$ROOT/LICENSE" "$STAGE/codex/"
(cd "$STAGE/codex" && zip -qrX "$DIST/value-pricing-codex.zip" .)

# Portable, skills-only plugin for public directory review. No lifecycle hooks,
# local-only tools, credentials, or customer data are bundled.
mkdir -p "$STAGE/openai/skills" "$STAGE/openai/assets"
cp "$ROOT/plugin.json" "$STAGE/openai/"
cp "$ROOT/LICENSE" "$ROOT/README.md" "$STAGE/openai/"
cp "$ROOT/assets/value-pricing-icon.svg" "$STAGE/openai/assets/"
cp -R "$ROOT/skills/value-pricing" "$STAGE/openai/skills/"
(cd "$STAGE/openai" && zip -qrX "$DIST/value-pricing-openai.zip" .)

ls -lh "$DIST"
