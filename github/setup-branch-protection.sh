#!/bin/bash
#
# Setup Branch Protection Rules for iPhone Export
#
# This script configures branch protection on 'main' branch to ensure:
# 1. API Docker build must pass before merge
# 2. Frontend Docker build must pass before merge
# 3. Pull requests are required
# 4. Conversations must be resolved
#
# Prerequisites:
# - GitHub CLI (gh) installed
# - Authenticated with repo admin access
#
# Usage:
#   ./github/setup-branch-protection.sh

set -e

echo "🔒 Setting up branch protection rules for iPhone Export..."
echo ""

# Configuration
REPO_OWNER="raolivei"
REPO_NAME="iphone-export"
BRANCH="main"

# Required status checks
STATUS_CHECKS="Build and Push API Docker Image,Build and Push Frontend Docker Image"

echo "📋 Configuration:"
echo "  Repository: ${REPO_OWNER}/${REPO_NAME}"
echo "  Branch: ${BRANCH}"
echo "  Required checks: ${STATUS_CHECKS}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Apply branch protection using GitHub API
echo "🔧 Applying branch protection rules..."
echo ""

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/${BRANCH}/protection" \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Build and Push API Docker Image", "Build and Push Frontend Docker Image"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF

echo ""
echo "✅ Branch protection rules configured successfully!"
echo ""
echo "📝 Rules applied:"
echo "  ✅ Pull requests required"
echo "  ✅ Status checks required:"
echo "     - Build and Push API Docker Image"
echo "     - Build and Push Frontend Docker Image"
echo "  ✅ Branches must be up to date"
echo "  ✅ Conversation resolution required"
echo "  ✅ Linear history enforced"
echo "  ✅ Force push disabled"
echo "  ✅ Branch deletion disabled"
echo "  ✅ Rules apply to administrators"
echo ""
echo "🎯 Result:"
echo "  PRs cannot be merged until both Docker build workflows pass!"
echo ""
echo "🌐 View settings at:"
echo "  https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/branches"
echo ""
echo "✨ Done!"





