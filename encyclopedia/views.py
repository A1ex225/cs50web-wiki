from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import random
from . import util
import markdown


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "error_title": "Page Not Found",
            "error_message": f"The page '{title}' does not exist.",
            "title":title,
        })
    
    html_content = markdown.markdown(content)
    return render(request, "encyclopedia/entry.html",{
        "title": title,
        "content": util.markdown_to_html(content),
    })


def search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('index')

    entries = util.list_entries()    
    exact_match=None

    for entry in entries:
        if entry and entry.lower() == query.lower():
            exact_match = entry
            break

    if exact_match:
        return redirect('entry', title=exact_match)
    
    matches = []
    for entry in entries:
        if entry and query.lower() in entry.lower():
            matches.append(entry)

    if len(matches)==1:
        return redirect('entry', title=matches[0])
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches,
        "matches_count": len(matches),
    })


def new_page(request):
    if request.method == "POST":
        title=request.POST.get("title")
        content=request.POST.get("content")
        
        if util.get_entry(title):
            return render(request, "encyclopedia/new.html", {
                "error": "This entry already exists.",
                "title": title,
                "content": content,
            })
        if title and content:
            markdown_content = f"# {title}\n\n{content}"
            util.save_entry(title, markdown_content)
            return redirect('entry', title=title)
    return render(request, "encyclopedia/new.html")


def edit_page(request, title):
    if not util.get_entry(title):
        return render(request, "encyclopedia/Error.html", {
            "error_title": "Page Not Found",
            "error_message": f"The page '{title}' does not exist. You can create it instead.",
            "title": title,
        })
    
    if request.method == "POST":
        content= request.POST.get("content", "").strip()
        if content:
            markdown_content= f"# {title}\n\n{content}"
            util.save_entry(title, markdown_content)
            return redirect('entry', title=title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": content,
                "error": "Content cannot be empty."
            })
    content = util.get_entry(title)
    if content:
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            content_for_edit = '\n'.join(lines[1:]).lstrip()

        else:
            content_for_edit = content
    else:
        content_for_edit = ""
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content_for_edit,
    })

def random_page(request):
    try:
        all_entries = util.list_entries()

        valid_entries = [entry for entry in all_entries if entry]
        if not valid_entries:
            return render(request, "encyclopedia/error.html", {
                "error_title": "No pages available",
                "error_message": "There are no encyclopedia entries yet."
            })
            
        random_entry = random.choice(valid_entries)
        return redirect('entry', title=random_entry)
    except Exception as e:
        return redirect('index')