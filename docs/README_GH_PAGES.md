# GitHub Pages Deployment (No Backend)

This site is fully static and runs the Python chord engine in the browser via Pyodide.

## Files used by Pages
- `docs/index.html`
- `docs/GuitarChords.py`
- `docs/guitar.wav`

## Publish steps
1. Push repository to GitHub.
2. In repository Settings -> Pages:
   - Source: `Deploy from a branch`
   - Branch: `main` (or your branch)
   - Folder: `/docs`
3. Save and wait for deployment.

## Update workflow
Whenever you modify `GuitarChords.py` in project root, sync it to docs:

```bash
cp GuitarChords.py docs/GuitarChords.py
```

Then commit and push.

## Local preview
Use a static server from repository root:

```bash
python -m http.server 8000
```

Open:
- `http://127.0.0.1:8000/docs/`
