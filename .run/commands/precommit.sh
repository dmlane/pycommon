# vim: set ft=bash ts=3 sw=3 expandtab:
# Install pre-commit hooks

command_precommit() {
   echo -n "Installing pre-commit hooks..."
   if git rev-parse --git-dir > /dev/null 2>&1; then
      cat > ${REPO_DIR}/.git/hooks/pre-commit <<EOF
#!/usr/bin/env bash

.run/pre_commit.sh
EOF
      chmod 755 ${REPO_DIR}/.git/hooks/pre-commit
   else
      echo "not a Git repository"
   fi
}

