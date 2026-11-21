PAGE_THEMES = [
    ("/learn/", "forest"),
    ("/library/", "forest"),
    ("/studio/", "lavender"),
    ("/governance/", "burgundy"),
    ("/upload/", "burgundy"),
    ("/onboard/", "burgundy"),
]
def theme(request):
    mode = request.session.get("theme_override")
    if mode:
        return {"theme_class": "theme-" + mode, "theme_mode": mode, "theme_current": mode}
    for prefix, name in PAGE_THEMES:
        if request.path.startswith(prefix):
            return {"theme_class": "theme-" + name, "theme_mode": "auto", "theme_current": name}
    return {"theme_class": "theme-royal", "theme_mode": "auto", "theme_current": "royal"}
