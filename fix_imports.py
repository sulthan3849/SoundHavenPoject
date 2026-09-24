import pathlib

# Fix glassmorphism imports
file_path_1 = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content_1 = file_path_1.read_text(encoding='utf-8')
content_1 = content_1.replace(
    'import { Search, Loader2, Download, Play, Volume2, Pause } from "lucide-react";',
    'import { Search, Loader2, Download, Play, Volume2, Pause, X, Check } from "lucide-react";'
)
file_path_1.write_text(content_1, encoding='utf-8')

# Fix progressive-blur-modal imports
file_path_2 = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content_2 = file_path_2.read_text(encoding='utf-8')
content_2 = content_2.replace(
    "import { X, Play, Heart, MoreHorizontal, Download, Volume2, Pause } from 'lucide-react';",
    "import { X, Play, Heart, MoreHorizontal, Download, Volume2, Pause, Check } from 'lucide-react';"
)
file_path_2.write_text(content_2, encoding='utf-8')
