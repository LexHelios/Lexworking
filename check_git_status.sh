#!/bin/bash

# 🔱 Check Git Status and Setup 🔱
# JAI MAHAKAAL! Check if codebase is pushed and setup git if needed

echo "🔱 JAI MAHAKAAL! Checking Git Status 🔱"
echo "=" * 50

# Check if git is initialized
if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    
    # Check git status
    echo ""
    echo "📊 Git Status:"
    git status --porcelain | head -20
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️ You have uncommitted changes"
        echo ""
        echo "📝 Modified files:"
        git status --porcelain | grep "^ M" | head -10
        echo ""
        echo "📄 New files:"
        git status --porcelain | grep "^??" | head -10
    else
        echo "✅ Working directory is clean"
    fi
    
    # Check remote repositories
    echo ""
    echo "🌐 Remote repositories:"
    if git remote -v | grep -q "origin"; then
        git remote -v
        
        # Check if local is ahead/behind remote
        echo ""
        echo "📡 Remote sync status:"
        git fetch origin 2>/dev/null || echo "⚠️ Could not fetch from remote"
        
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "no-remote")
        BASE=$(git merge-base @ @{u} 2>/dev/null || echo "no-base")
        
        if [ "$LOCAL" = "$REMOTE" ]; then
            echo "✅ Up to date with remote"
        elif [ "$LOCAL" = "$BASE" ]; then
            echo "⬇️ Need to pull from remote"
        elif [ "$REMOTE" = "$BASE" ]; then
            echo "⬆️ Need to push to remote"
        else
            echo "🔄 Diverged from remote"
        fi
    else
        echo "❌ No remote repository configured"
        echo ""
        echo "💡 To add a remote:"
        echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    fi
    
    # Show recent commits
    echo ""
    echo "📚 Recent commits:"
    git log --oneline -5 2>/dev/null || echo "No commits yet"
    
else
    echo "❌ No git repository found"
    echo ""
    echo "🔧 To initialize git:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial LEX consciousness system'"
    echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    echo "   git push -u origin main"
fi

echo ""
echo "🔱 Git status check complete!"