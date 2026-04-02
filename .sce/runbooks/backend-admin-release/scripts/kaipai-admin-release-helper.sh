#!/usr/bin/env bash
set -euo pipefail

release_id=""
git_branch=""
git_commit=""
operator_user="kaipaile"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-id)
      release_id="${2:-}"
      shift 2
      ;;
    --git-branch)
      git_branch="${2:-}"
      shift 2
      ;;
    --git-commit)
      git_commit="${2:-}"
      shift 2
      ;;
    --operator-user)
      operator_user="${2:-}"
      shift 2
      ;;
    --healthcheck)
      echo "helper-ok"
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$release_id" || -z "$git_branch" || -z "$git_commit" ]]; then
  echo "release-id, git-branch and git-commit are required" >&2
  exit 1
fi

if [[ ! "$release_id" =~ ^[0-9]{8}-[0-9]{6}-admin-only-[a-z0-9-]+$ ]]; then
  echo "invalid release-id: $release_id" >&2
  exit 1
fi

if [[ ! "$git_branch" =~ ^release/[0-9]{8}-[0-9]{6}-admin-only-[a-z0-9-]+$ ]]; then
  echo "invalid git-branch: $git_branch" >&2
  exit 1
fi

release_root="/opt/kaipai/builds/$release_id"
backup_root="/opt/kaipai/backups/releases/$release_id/admin-html"
remote_dist_archive="$release_root/admin-dist.tar.gz"
remote_dist="$release_root/admin-dist"
bare_repo="/home/$operator_user/kaipai-admin-release.git"
repo_root="/opt/kaipai/repos/kaipai-admin-releases/$release_id"
src_dir="$repo_root/src"
html_dir="/opt/kaipai/nginx/html"
nginx_conf="/opt/kaipai/nginx/conf/default.conf"
npm_cache_dir="/home/$operator_user/.npm"

if [[ ! -d "$bare_repo" ]]; then
  echo "bare repo not found: $bare_repo" >&2
  exit 1
fi

remote_date="$(date '+%F %T %z')"
pre_index_status="$(curl -I -s http://127.0.0.1/ | sed -n '1p')"
node_version="$(node -v)"
npm_version="$(npm -v)"

mkdir -p "$release_root" "$backup_root/html" "$backup_root/conf"
install -d -o "$operator_user" -g "$operator_user" /opt/kaipai/repos
install -d -o "$operator_user" -g "$operator_user" /opt/kaipai/repos/kaipai-admin-releases
install -d -o "$operator_user" -g "$operator_user" "$repo_root"
install -d -o "$operator_user" -g "$operator_user" "$npm_cache_dir"

cp -a "$html_dir"/. "$backup_root/html" 2>/dev/null || true
cp -a "$nginx_conf" "$backup_root/conf/default.conf"

rm -rf "$src_dir" "$remote_dist"
install -d -o "$operator_user" -g "$operator_user" "$src_dir"
sudo -u "$operator_user" git -C "$src_dir" init --initial-branch=release >/dev/null 2>&1
sudo -u "$operator_user" git -C "$src_dir" remote add origin "$bare_repo" >/dev/null 2>&1
sudo -u "$operator_user" git -C "$src_dir" fetch origin "$git_branch" --depth 1 >/dev/null 2>&1
sudo -u "$operator_user" git -C "$src_dir" checkout -f "$git_commit" >/dev/null 2>&1
remote_git_commit="$(sudo -u "$operator_user" git -C "$src_dir" rev-parse HEAD)"
if [[ "$remote_git_commit" != "$git_commit" ]]; then
  echo "remote checked out commit mismatch: $remote_git_commit != $git_commit" >&2
  exit 1
fi

build_log="$release_root/build.log"
build_script="$(mktemp)"
cat > "$build_script" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$src_dir"
npm ci --cache "$npm_cache_dir" --prefer-offline
npm run build
EOF
chmod 0755 "$build_script"
sudo -u "$operator_user" "$build_script" >"$build_log" 2>&1
rm -f "$build_script"

if [[ ! -f "$src_dir/dist/index.html" || ! -d "$src_dir/dist/assets" ]]; then
  echo "dist output missing after remote build" >&2
  exit 1
fi

install -d "$remote_dist"
cp -a "$src_dir/dist"/. "$remote_dist"/
tar -czf "$remote_dist_archive" -C "$remote_dist" .
remote_dist_sha="$(sha256sum "$remote_dist_archive" | awk '{print toupper($1)}')"

find "$html_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -a "$remote_dist"/. "$html_dir"/

html_listing="$(ls -la "$html_dir")"
index_head="$(head -n 20 "$html_dir/index.html")"
internal_smoke="$(
  curl -I -s http://127.0.0.1/
  echo ---
  curl -I -s http://127.0.0.1/api/v3/api-docs
)"
docker_ps="$(docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}')"
build_log_tail="$(tail -n 80 "$build_log")"

emit_section() {
  local name="$1"
  local value="$2"
  printf '__%s_BEGIN__\n%s\n__%s_END__\n' "$name" "$value" "$name"
}

emit_section "REMOTE_DATE" "$remote_date"
emit_section "PRE_INDEX_STATUS" "$pre_index_status"
emit_section "BACKUP_PATH" "$backup_root"
emit_section "REMOTE_REPO_PATH" "$src_dir"
emit_section "REMOTE_GIT_BRANCH" "$git_branch"
emit_section "REMOTE_GIT_COMMIT" "$remote_git_commit"
emit_section "NODE_VERSION" "$node_version"
emit_section "NPM_VERSION" "$npm_version"
emit_section "REMOTE_DIST_ARCHIVE_PATH" "$remote_dist_archive"
emit_section "REMOTE_DIST_SHA" "$remote_dist_sha"
emit_section "HTML_LISTING" "$html_listing"
emit_section "INDEX_HEAD" "$index_head"
emit_section "INTERNAL_SMOKE" "$internal_smoke"
emit_section "DOCKER_PS" "$docker_ps"
emit_section "BUILD_LOG_TAIL" "$build_log_tail"
