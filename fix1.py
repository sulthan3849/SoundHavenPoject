import pathlib

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content = file_path.read_text(encoding='utf-8')

# Fix text-2xl leading-none mb-1 "Ãƒâ€”" -> <X className="w-5 h-5" />
content = content.replace('<span className="text-2xl leading-none mb-1">Ãƒâ€”</span>', '<X className="w-5 h-5" />')

file_path.write_text(content, encoding='utf-8')
