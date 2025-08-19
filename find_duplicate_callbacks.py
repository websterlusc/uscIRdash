#!/usr/bin/env python3
"""
Script to find and help fix duplicate callback outputs in main_app.py
"""

import re
import os

def find_duplicate_outputs(filename='main_app.py'):
    """Find callbacks that might have duplicate outputs"""
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"🔍 Analyzing {filename} for duplicate outputs...")
    print("=" * 60)
    
    # Find all callbacks with session-store.data output
    session_store_patterns = [
        r"Output\(['\"]session-store['\"],\s*['\"]data['\"]",
        r"Output\(['\"]session-store['\"].*['\"]data['\"]",
        r"session-store\.data"
    ]
    
    matches = []
    line_numbers = content.split('\n')
    
    for i, line in enumerate(line_numbers, 1):
        for pattern in session_store_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append((i, line.strip()))
    
    if matches:
        print(f"🚨 Found {len(matches)} potential session-store.data outputs:")
        print()
        
        for line_num, line in matches:
            print(f"Line {line_num}: {line}")
        
        print("\n" + "=" * 60)
        print("🔧 TO FIX:")
        print("1. Remove ALL callbacks that have Output('session-store', 'data')")
        print("2. Replace with the SINGLE combined callback from the artifact")
        print("3. Look for these callback function names to remove:")
        
        # Look for callback function definitions near the matches
        callback_functions = find_callback_functions(content, matches)
        for func_name in callback_functions:
            print(f"   - {func_name}")
            
    else:
        print("✅ No obvious session-store.data duplicates found")
    
    # Also check for other common duplicate outputs
    check_other_duplicates(content, line_numbers)

def find_callback_functions(content, matches):
    """Find the function names that contain the duplicate outputs"""
    functions = []
    lines = content.split('\n')
    
    for line_num, _ in matches:
        # Look backwards from the match to find the function definition
        for i in range(max(0, line_num - 20), line_num):
            line = lines[i].strip()
            if line.startswith('def ') and '(' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if func_name not in functions:
                    functions.append(func_name)
                break
    
    return functions

def check_other_duplicates(content, line_numbers):
    """Check for other common duplicate outputs"""
    common_outputs = [
        'url.pathname',
        'page-content.children',
        'navbar-container.children'
    ]
    
    for output in common_outputs:
        count = content.count(f"Output('{output.split('.')[0]}', '{output.split('.')[1]}')")
        if count > 1:
            print(f"⚠️  Warning: {output} appears {count} times")

def show_solution():
    """Show the solution steps"""
    print("\n" + "=" * 60)
    print("💡 SOLUTION STEPS:")
    print("=" * 60)
    print("""
1. FIND and REMOVE these callback functions from main_app.py:
   - Any function with @app.callback that has Output('session-store', 'data')
   - Common names: sync_flask_session, handle_logout, etc.

2. REPLACE with the SINGLE combined callback from the artifact

3. MAKE SURE you have these imports:
   from dash import callback_context
   from flask import session as flask_session

4. RESTART your app and test

Example of what to REMOVE:
-------------------------
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def sync_flask_session(pathname):
    # REMOVE THIS ENTIRE FUNCTION

@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('logout-btn', 'n_clicks')],
    prevent_initial_call=True  
)
def handle_logout(n_clicks, session_data):
    # REMOVE THIS ENTIRE FUNCTION TOO

Replace BOTH with the single combined callback from the artifact.
""")

if __name__ == "__main__":
    find_duplicate_outputs()
    show_solution()
