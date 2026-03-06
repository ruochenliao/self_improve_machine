#!/usr/bin/env python3
"""
✨ README MAGIC ✨
Generate professional GitHub README.md files with AI-powered content.

Usage:
$ python readme_magic.py
Follow prompts to create a stunning README in seconds.

Free API endpoints used: summarize, explain-code
"""
import sys
import requests

def main():
    project_name = input("Project Name: ")
    description = input("One-line description: ")
    
    # Use Stark-Vortex API to generate features section
    features_response = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/summarize',
        json={'text': f'Key features for {project_name}...'},
    )
    features = features_response.json()['result']
    
    # Generate installation guide
    install_guide = requests.post(
        'https://<tunnel-not-configured>.trycloudflare.com/explain-code',
        json={'code': 'pip install your-project', 'language': 'bash'},
    ).json()['explanation']
    
    # Build README content
    readme = f"""# {project_name}
{description}

## Features
{features}

## Installation
{install_guide}

## Usage
Coming soon! Use `/help` for commands.

![GitHub last commit](https://img.shields.io/github/last-commit/{project_name})
![License](https://img.shields.io/badge/License-MIT-blue)
"""
    
    with open('README.md', 'w') as f:
        f.write(readme)
    print(f"\n\u2705 README.md created! Commit with:\ngit commit -m '{project_name} - New project with AI-generated README'")

if __name__ == '__main__':
    main()