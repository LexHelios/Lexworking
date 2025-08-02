#!/usr/bin/env python3
"""
Setup Persistent Storage for LexOS
JAI MAHAKAAL! Creating document vault and memory systems
"""
import os
import json
from pathlib import Path
from datetime import datetime

def setup_persistent_storage():
    """Create all necessary folders for persistent storage"""
    
    # Base storage path
    base_path = Path("./lex_vault")
    
    # Create directory structure
    directories = {
        "documents": base_path / "documents",          # PDFs, docs, spreadsheets
        "media": base_path / "media",                  # Images, videos, audio
        "conversations": base_path / "conversations",   # Chat histories
        "memories": base_path / "memories",            # Long-term memories
        "generated": base_path / "generated",          # AI-generated content
        "knowledge": base_path / "knowledge",          # Learned information
        "predictions": base_path / "predictions",      # Future predictions
        "changes": base_path / "changes",              # Change tracking
        "embeddings": base_path / "embeddings",        # Vector embeddings
        "index": base_path / "index",                  # Search indexes
    }
    
    # Create all directories
    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created: {path}")
        
        # Create README in each directory
        readme_path = path / "README.md"
        readme_content = f"# {name.title()} Storage\n\nThis directory stores {name} for LexOS.\n\nCreated: {datetime.now().isoformat()}"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    # Create master index file
    index_file = base_path / "vault_index.json"
    index_data = {
        "created": datetime.now().isoformat(),
        "version": "1.0.0",
        "directories": {name: str(path) for name, path in directories.items()},
        "stats": {
            "total_files": 0,
            "total_size": 0,
            "last_updated": datetime.now().isoformat()
        }
    }
    
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"\n[OK] Created master index: {index_file}")
    
    # Create .gitignore to protect sensitive data
    gitignore_path = base_path / ".gitignore"
    gitignore_content = """# Ignore all files by default
*
# But track directory structure
!*/
!README.md
!.gitignore
# Never track sensitive files
*.key
*.pem
*.env
"""
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    
    print(f"[OK] Created .gitignore for data protection")
    
    # Update settings to use new paths
    env_updates = f"""
# LexOS Vault Configuration
LEXOS_VAULT_PATH=./lex_vault
LEXOS_DOCUMENTS_PATH=./lex_vault/documents
LEXOS_MEDIA_PATH=./lex_vault/media
LEXOS_MEMORIES_PATH=./lex_vault/memories
LEXOS_GENERATED_PATH=./lex_vault/generated
"""
    
    print("\n[INFO] Add these to your .env file:")
    print(env_updates)
    
    print("\n[SUCCESS] Persistent storage structure created successfully!")
    return directories

if __name__ == "__main__":
    setup_persistent_storage()