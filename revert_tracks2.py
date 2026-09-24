import pathlib
import re

# 1. Revert track buttons in progressive-blur-modal.tsx
file_path_modal = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content_modal = file_path_modal.read_text(encoding='utf-8')

lines = content_modal.splitlines()
start = -1
end = -1
for i, line in enumerate(lines):
    if 'const queuedTask = queue.find(t => t.id === track.id.toString());' in line:
        start = i - 2
        for j in range(i, i+30):
            if '</button>' in lines[j]:
                end = j
                break
        break

if start != -1 and end != -1:
    new_track_btn_modal = """<button
                            onClick={(e) => {
                              e.stopPropagation();
                              if (!queue.some(t => t.id === track.id.toString())) {
                                addDownload({
                                  id: track.id.toString(),
                                  type: 'track',
                                  title: track.title,
                                  artist: track.artist || 'Unknown',
                                  cover_url: track.cover_url || (details && 'cover_url' in details ? details.cover_url : undefined)
                                });
                              }
                            }}
                            className={`p-2 rounded-full transition-all hidden md:block ${
                              queue.some(t => t.id === track.id.toString())
                                ? "text-green-500" 
                                : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
                            }`}
                            title="Download FLAC"
                          >
                             <Download className={`w-4 h-4 ${queue.some(t => t.id === track.id.toString()) ? 'animate-pulse' : ''}`} />
                          </button>"""
    
    content_modal = '\n'.join(lines[:start]) + '\n' + new_track_btn_modal + '\n' + '\n'.join(lines[end+1:])
    file_path_modal.write_text(content_modal, encoding='utf-8')
    print('Reverted track button in modal')
else:
    print('Could not find track button in modal')


# 2. Revert track buttons in glassmorphism-listen-app-block-shadcnui.tsx
file_path_main = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content_main = file_path_main.read_text(encoding='utf-8')
lines2 = content_main.splitlines()

new_btn_main = """                              <button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={`p-2 rounded-full transition-all ${
                                  queue.some(t => t.id === track.id.toString())
                                    ? "text-green-500" 
                                    : "text-foreground/40 hover:text-foreground hover:bg-foreground/10"
                                }`}
                                title="Download FLAC"
                              >
                                <Download className={`h-4 w-4 ${queue.some(t => t.id === track.id.toString()) ? 'animate-pulse' : ''}`} />
                              </button>"""

while True:
    start2 = -1
    end2 = -1
    for i, line in enumerate(lines2):
        if 'className={`p-2 rounded-full transition-all ${queue.find' in line:
            for k in range(i, i-5, -1):
                if '<button' in lines2[k]:
                    start2 = k
                    break
            for j in range(i, i+15):
                if '</button>' in lines2[j]:
                    end2 = j
                    break
            break
    if start2 != -1 and end2 != -1:
        lines2 = lines2[:start2] + new_btn_main.splitlines() + lines2[end2+1:]
        print('Reverted a track button in main')
    else:
        break

file_path_main.write_text('\n'.join(lines2), encoding='utf-8')
