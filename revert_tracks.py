import pathlib
import re

# 1. Revert track buttons in progressive-blur-modal.tsx
file_path_modal = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content_modal = file_path_modal.read_text(encoding='utf-8')

# The current track button in modal has this logic:
# const queuedTask = queue.find(t => t.id === track.id.toString());
# if (queuedTask) { ... cancelDownload ... }
# Let's replace it with the original logic.
old_track_btn_regex = r'<button\s+onClick=\{\(e\) => \{\s*e\.stopPropagation\(\);\s*const queuedTask = queue\.find\(t => t\.id === track\.id\.toString\(\)\);.*?\} \?\s*\(\s*<X className="h-4 w-4" />\s*\)\s*:\s*queue\.find\(t => t\.id === track\.id\.toString\(\)\)\?\.status === \'completed\' \?\s*\(\s*<Check className="h-4 w-4" />\s*\)\s*:\s*\(\s*<Download className="h-4 w-4" />\s*\)\s*\}\s*</button>'

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

if re.search(old_track_btn_regex, content_modal, flags=re.DOTALL):
    content_modal = re.sub(old_track_btn_regex, new_track_btn_modal, content_modal, flags=re.DOTALL)
    print("Reverted track buttons in modal")
else:
    print("Failed to revert track buttons in modal")
    
file_path_modal.write_text(content_modal, encoding='utf-8')


# 2. Revert track buttons in glassmorphism-listen-app-block-shadcnui.tsx
file_path_main = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content_main = file_path_main.read_text(encoding='utf-8')

# The handleDownloadTrack function needs reverting
old_handle_regex = r'const handleDownloadTrack = \(track: Track, e: React\.MouseEvent\) => \{.*?const queuedTask = queue\.find.*?addDownload\(\{.*?\}\);\s*\};'

new_handle = """const handleDownloadTrack = (track: Track, e: React.MouseEvent) => {
    e.stopPropagation(); // Mencegah terklik play
    if (queue.some(t => t.id === track.id.toString())) return;
    
    addDownload({
      id: track.id.toString(),
      type: 'track',
      title: track.title,
      artist: track.artist,
      cover_url: track.cover_url || (currentArtist ? currentArtist.picture_url : undefined)
    });
  };"""

if re.search(old_handle_regex, content_main, flags=re.DOTALL):
    content_main = re.sub(old_handle_regex, new_handle, content_main, flags=re.DOTALL)
    print("Reverted handleDownloadTrack in main")
else:
    print("Failed to revert handleDownloadTrack in main")

# Revert the buttons in main
# They look like this:
# <button
#   onClick={(e) => handleDownloadTrack(track, e)}
#   className={`p-2 rounded-full transition-all ${queue.find(...) ? 'text-red-500 hover:bg-red-500/10' : ...}`}
#   title={...}
# >
#   {... ? <X /> : ...}
# </button>
old_main_btn_regex = r'<button\s+onClick=\{\(e\) => handleDownloadTrack\(track, e\)\}\s+className=\{`p-2 rounded-full transition-all \$\{.*?\} \?\s*\(\s*<X className="h-4 w-4" />\s*\)\s*:\s*queue\.find\(t => t\.id === track\.id\.toString\(\)\)\?\.status === \'completed\' \?\s*\(\s*<Check className="h-4 w-4" />\s*\)\s*:\s*\(\s*<Download className="h-4 w-4" />\s*\)\s*\}\s*</button>'

new_main_btn = """<button
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

if re.search(old_main_btn_regex, content_main, flags=re.DOTALL):
    content_main = re.sub(old_main_btn_regex, new_main_btn, content_main, flags=re.DOTALL)
    print("Reverted track buttons in main")
else:
    print("Failed to revert track buttons in main")

file_path_main.write_text(content_main, encoding='utf-8')
