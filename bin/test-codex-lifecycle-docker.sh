#!/usr/bin/env bash
# Explicit CLI install/remove/upgrade tests in a disposable Docker user home.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="${1:-$ROOT/test-outputs/codex-lifecycle}"
mkdir -p "$OUTPUT/runtime" "$OUTPUT/package"
OUTPUT="$(cd "$OUTPUT" && pwd)"
RUN="$OUTPUT/evidence/run-$(date -u +%Y%m%d-%H%M%S)-$$"
mkdir -p "$RUN"
printf "%s\n" "$RUN" > "$OUTPUT/latest-run.txt"
for asset in codex-x86_64-unknown-linux-musl.tar.gz codex-app-server-x86_64-unknown-linux-musl.tar.gz codex-code-mode-host-x86_64-unknown-linux-musl.tar.gz; do
  if [[ ! -f "$OUTPUT/runtime/$asset" ]]; then
    gh release download rust-v0.160.0 --repo openai/codex --pattern "$asset" --dir "$OUTPUT/runtime"
  fi
done
python3 - "$ROOT" "$OUTPUT/package" <<'PY'
from pathlib import Path
import shutil,subprocess,sys
root=Path(sys.argv[1]);target=Path(sys.argv[2])
for name in subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines():
    source=root/name
    if source.is_file():
        destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
PY
docker image inspect pixel-mcp-ci:latest --format '{{.Id}}' > "$OUTPUT/image-id.txt"
docker run --rm --platform linux/amd64 --entrypoint /bin/bash \
  -v "$OUTPUT/runtime:/runtime:ro" -v "$OUTPUT/package:/package:ro" \
  -v "$RUN:/evidence" pixel-mcp-ci:latest -lc '
    mkdir -p /opt/codex /work
    for archive in /runtime/*.tar.gz; do tar -xzf "$archive" -C /opt/codex; done
    for binary in /opt/codex/*; do
      case "$binary" in
        *code-mode-host*) ln -s "$binary" /usr/local/bin/codex-code-mode-host;;
        *app-server*) ln -s "$binary" /usr/local/bin/codex-app-server;;
        *codex-x86*) ln -s "$binary" /usr/local/bin/codex;;
      esac
    done
    python3 /package/bin/test-codex-lifecycle.py --package /package \
      --aseprite /build/aseprite/build/bin/aseprite --output /evidence --isolated-home /root
  '
