import os
import re
import yaml
from datetime import datetime

# Path to articles
ARTICLES_DIR = 'articles'

def get_post_date(content):
    """Extracts date from YAML frontmatter."""
    match = re.search(r'---(.*?)---', content, re.DOTALL)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
        date_val = data.get('date')
        if not date_val:
            return None
        if isinstance(date_val, datetime):
            return date_val
        # Handle string dates
        return datetime.strptime(str(date_val), '%Y-%m-%d')
    except Exception:
        return None

def update_order(file_path, order):
    """Injects or updates the 'order' field in frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'---(.*?)---', content, re.DOTALL)
    if not match:
        return

    try:
        data = yaml.safe_load(match.group(1))
        data['order'] = order
        
        # Rebuild the file
        new_yaml = yaml.dump(data, sort_keys=False, default_flow_style=False).strip()
        new_content = f"---\n{new_yaml}\n---" + content[match.end():]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    # Loop through each topic folder
    for topic in os.listdir(ARTICLES_DIR):
        topic_path = os.path.join(ARTICLES_DIR, topic)
        if not os.path.isdir(topic_path):
            continue
        
        # Gather all posts in this topic
        posts = []
        for post_folder in os.listdir(topic_path):
            post_path = os.path.join(topic_path, post_folder, 'index.qmd')
            if os.path.isfile(post_path):
                with open(post_path, 'r', encoding='utf-8') as f:
                    date = get_post_date(f.read())
                    if date:
                        posts.append({'path': post_path, 'date': date})
        
        # Sort posts by date (Oldest first)
        posts.sort(key=lambda x: x['date'])
        
        # Apply order numbers
        for i, post in enumerate(posts):
            update_order(post['path'], i + 1)
            print(f"Updated {post['path']} with order {i+1}")

if __name__ == "__main__":
    main()
