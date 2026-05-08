import os
import re
import yaml
import json
import urllib.parse
from datetime import datetime

# Path to articles
ARTICLES_DIR = 'articles'
SIDEBAR_FILE = '_sidebar.yml'

def parse_date(date_val):
    """Safely parses date strings or datetime objects."""
    if isinstance(date_val, datetime):
        return date_val

    date_str = str(date_val).strip()
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except ValueError:
            pass

    return None

def get_post_info(path, is_ipynb=False):
    """Extracts date and title from YAML frontmatter."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None, None

    data = None
    if is_ipynb:
        try:
            nb = json.loads(content)
            if not nb.get('cells'): return None, None
            first_cell = nb['cells'][0]
            if first_cell.get('cell_type') not in ['raw', 'markdown']: return None, None
            raw_content = "".join(first_cell.get('source', []))
            match = re.search(r'---(.*?)---', raw_content, re.DOTALL)
            if not match: return None, None
            data = yaml.safe_load(match.group(1))
        except Exception:
            return None, None
    else:
        match = re.search(r'---(.*?)---', content, re.DOTALL)
        if not match: return None, None
        try:
            data = yaml.safe_load(match.group(1))
        except Exception:
            return None, None

    if not data: return None, None

    title = data.get('title', os.path.basename(os.path.dirname(path)))
    date_val = data.get('date')
    date = parse_date(date_val) if date_val else None

    return date, title

def update_order_in_file(file_path, order, is_ipynb=False):
    """Injects or updates the 'order' field in frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if is_ipynb:
            nb = json.loads(content)
            first_cell = nb['cells'][0]
            raw_content = "".join(first_cell.get('source', []))
            match = re.search(r'---(.*?)---', raw_content, re.DOTALL)
            if not match: return

            data = yaml.safe_load(match.group(1))
            if data.get('order') == order: return
            data['order'] = order

            new_yaml = yaml.dump(data, sort_keys=False, default_flow_style=False).strip()
            new_raw_content = f"---\n{new_yaml}\n---" + raw_content[match.end():]
            first_cell['source'] = [line + '\n' for line in new_raw_content.split('\n')]

            while first_cell['source'] and first_cell['source'][-1] == '\n':
                first_cell['source'].pop()
            if first_cell['source']:
                first_cell['source'][-1] = first_cell['source'][-1].rstrip('\n')

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1)
                f.write('\n')
        else:
            match = re.search(r'---(.*?)---', content, re.DOTALL)
            if not match: return

            data = yaml.safe_load(match.group(1))
            if data.get('order') == order: return
            data['order'] = order

            new_yaml = yaml.dump(data, sort_keys=False, default_flow_style=False).strip()
            new_content = f"---\n{new_yaml}\n---" + content[match.end():]

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except Exception as e:
        print(f"Error updating order in {file_path}: {e}")

def main():
    if not os.path.exists(ARTICLES_DIR): return

    topics = {}

    # 1. Gather all posts and group by topic
    for entry in os.listdir(ARTICLES_DIR):
        topic_path = os.path.join(ARTICLES_DIR, entry)
        if not os.path.isdir(topic_path): continue

        topic_posts = []
        for post_folder in os.listdir(topic_path):
            post_folder_path = os.path.join(topic_path, post_folder)
            if not os.path.isdir(post_folder_path): continue

            qmd_path = os.path.join(post_folder_path, 'index.qmd')
            ipynb_path = os.path.join(post_folder_path, 'index.ipynb')

            target_path = qmd_path if os.path.isfile(qmd_path) else (ipynb_path if os.path.isfile(ipynb_path) else None)
            if not target_path: continue

            is_ipynb = target_path.endswith('.ipynb')
            date, title = get_post_info(target_path, is_ipynb)

            if date:
                # URL encode the components for safe HREFs
                safe_entry = urllib.parse.quote(entry)
                safe_folder = urllib.parse.quote(post_folder)

                topic_posts.append({
                    'path': target_path,
                    'date': date,
                    'title': title,
                    'is_ipynb': is_ipynb,
                    'href': f"articles/{safe_entry}/{safe_folder}/index.html"
                })

        if topic_posts:
            # Sort posts within topic by date (Oldest first)
            topic_posts.sort(key=lambda x: x['date'])

            # Format topic title
            topic_title = entry.replace('-', ' ').title()
            if entry.lower() in ['eda', 'exploratory data analysis (eda)']: topic_title = 'EDA'
            if entry.lower() == 'python-ds': topic_title = 'Python & Data Science'
            if entry.lower() == 'career-writing': topic_title = 'Career & Writing'

            # 1.5 Extract Topic-Level Date for sidebar sorting
            index_path = os.path.join(ARTICLES_DIR, entry, 'index.qmd')
            topic_date, _ = get_post_info(index_path) if os.path.exists(index_path) else (None, None)

            topics[topic_title] = {
                'posts': topic_posts,
                'earliest_date': topic_date if topic_date else min(p['date'] for p in topic_posts),
                'topic_key': entry
            }

    # 2. Sort topics by topic-level date (or earliest post date as fallback)
    sorted_topic_titles = sorted(topics.keys(), key=lambda t: topics[t]['earliest_date'])

    # 3. Apply global order and build sidebar structure
    global_order = 1
    sidebar_contents = []

    for t_title in sorted_topic_titles:
        topic_data = topics[t_title]
        # Use a dict for section to include both the title and the link
        section = {
            'section': t_title,
            'href': f"articles/{urllib.parse.quote(topic_data['topic_key'])}/index.html",
            'contents': []
        }

        for post in topic_data['posts']:
            # Update order in file for other listings
            update_order_in_file(post['path'], global_order, is_ipynb=post['is_ipynb'])

            # Add to sidebar
            section['contents'].append({
                'text': post['title'],
                'href': post['href']
            })
            global_order += 1

        sidebar_contents.append(section)

    # 4. Write sidebar YAML (Idempotent)
    final_sidebar_structure = {
        'website': {
            'sidebar': {
                'style': 'docked',
                'contents': [
                    {'text': 'TOPICS'},
                    {
                        'section': 'Articles',
                        'href': 'articles/index.html',
                        'section-style': 'flat',
                        'contents': sidebar_contents
                    }
                ]
            }
        }
    }

    new_sidebar_yaml = yaml.dump(final_sidebar_structure, sort_keys=False, default_flow_style=False)

    should_write = True
    if os.path.exists(SIDEBAR_FILE):
        with open(SIDEBAR_FILE, 'r', encoding='utf-8') as f:
            if f.read() == new_sidebar_yaml:
                should_write = False

    if should_write:
        with open(SIDEBAR_FILE, 'w', encoding='utf-8') as f:
            f.write(new_sidebar_yaml)
        print(f"Updated {SIDEBAR_FILE} with {global_order-1} articles across {len(sidebar_contents)} topics.")
    else:
        print(f"No changes to {SIDEBAR_FILE}. Skipping write.")

    # 5. Ensure topic indices exist
    for t_title in sorted_topic_titles:
        topic_key = topics[t_title]['topic_key']
        index_path = os.path.join(ARTICLES_DIR, topic_key, 'index.qmd')
        if not os.path.isfile(index_path):
            content = f"""---
title: "{t_title}"
listing:
  contents: "*/index.*"
  sort: "date asc"
  type: default
  fields: [title, description, date]
  field-links: [title]
---

Browse my articles on {t_title}.
"""
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created topic index: {index_path}")

if __name__ == "__main__":
    main()

