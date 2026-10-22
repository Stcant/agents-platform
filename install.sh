#!/usr/bin/env bash
# Install dev-brain into the global OpenCode configuration.
# Idempotent: existing files that are not ours are backed up, never deleted.

set -eu

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
plugin_dir="$repo_dir/plugin/dev-brain"
stamp="$(date +%Y%m%d%H%M%S)"

link() {
  src="$1"
  dst="$2"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    return 0
  fi
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    mv "$dst" "$dst.bak.$stamp"
    echo "backed up: $dst -> $dst.bak.$stamp"
  fi
  ln -s "$src" "$dst"
  echo "linked: $dst"
}

mkdir -p "$config_dir/commands" "$config_dir/agents" "$config_dir/skills"

link "$repo_dir/global/AGENTS.md" "$config_dir/AGENTS.md"

for src in "$repo_dir"/global/commands/*.md; do
  link "$src" "$config_dir/commands/$(basename "$src")"
done

for src in "$repo_dir"/global/agents/*.md; do
  link "$src" "$config_dir/agents/$(basename "$src")"
done

for src in "$repo_dir"/global/skills/*/; do
  name="$(basename "$src")"
  link "${src%/}" "$config_dir/skills/$name"
done

config_file="$config_dir/opencode.json"
python3 - "$config_file" "$plugin_dir" <<'PY'
import json
import os
import sys

path, plugin = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError) as error:
        print(f"warning: cannot parse {path}: {error}")
        print(f"add this manually: \"plugins\": [\"{plugin}\"]")
        sys.exit(0)

data.setdefault("$schema", "https://opencode.ai/config.json")
plugins = data.setdefault("plugins", [])
if plugin not in plugins:
    plugins.append(plugin)

with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
print(f"plugin registered in {path}")
PY

echo
echo "Installed. New sessions see the rules, skills and plugin."
echo "Commands require a server that started after this install: when no session is active, run 'opencode service restart'."
echo "Available commands: /start /resume /handoff /plan /impact /learn /review"
echo "Check the plugin with: opencode plugin list"
