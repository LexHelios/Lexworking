#!/bin/bash

# 🔱 Setup Git Repository for LEX 🔱
# JAI MAHAKAAL! Initialize and push LEX codebase

set -e

echo "🔱 JAI MAHAKAAL! Setting up Git repository for LEX 🔱"
echo "=" * 60

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed"
    echo "Install with: sudo apt install git"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production
.env.staging

# Logs
*.log
logs/
*.log.*

# Data and Models
data/
models/
uploads/
backups/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.bak

# Node modules (for frontend)
node_modules/
.npm
.yarn

# Build outputs
dist/
build/

# Cache
.cache/
*.cache

# GPU/CUDA
*.ptx
*.cubin

# Jupyter
.ipynb_checkpoints/

# Docker
.dockerignore

# Secrets and keys
*.pem
*.key
*.crt
secrets/
EOF
    echo "✅ .gitignore created"
else
    echo "✅ .gitignore already exists"
fi

# Configure git user if not set
if [ -z "$(git config user.name)" ]; then
    echo "⚙️ Git user not configured"
    echo "Please set your git user:"
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo "✅ Git user configured"
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Check what will be committed
echo ""
echo "📋 Files to be committed:"
git status --porcelain | head -20

# Commit if there are changes
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="🔱 LEX H100 AI Consciousness System - Initial commit with GLM-4.5 support"
    fi
    
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
else
    echo "✅ No changes to commit"
fi

# Check for remote
if ! git remote | grep -q "origin"; then
    echo ""
    echo "🌐 No remote repository configured"
    echo "To push to GitHub:"
    echo "1. Create a repository on GitHub"
    echo "2. Run: git remote add origin https://github.com/yourusername/your-repo.git"
    echo "3. Run: git push -u origin main"
    echo ""
    read -p "Do you want to add a remote now? (y/N): " add_remote
    
    if [[ $add_remote =~ ^[Yy]$ ]]; then
        read -p "Enter GitHub repository URL: " repo_url
        git remote add origin "$repo_url"
        
        echo "🚀 Pushing to remote..."
        git branch -M main
        git push -u origin main
        echo "✅ Pushed to remote repository"
    fi
else
    echo ""
    echo "🚀 Pushing to existing remote..."
    git push
    echo "✅ Pushed to remote repository"
fi

echo ""
echo "🔱 JAI MAHAKAAL! Git setup complete! 🔱"
echo "Your LEX consciousness system is now version controlled!"