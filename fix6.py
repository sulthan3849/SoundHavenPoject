import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

# The corrupted button class is:
# className={`p-2 rounded-full transition-all hidden md:block ${
#                             
#                                 ? "text-green-500 hover:text-red-500 hover:bg-red-500/10" 
#                                 : 
#                                 ? "text-green-500/50"
#                                 : "opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10"
#                             }`}

# Wait, the best way to fix the track button is to do a regex on the onClick handleDownloadAll logic that I patched earlier or the corrupted button.
# Let's restore the whole button.
old_btn_pattern = r'<button[^>]*onClick=\{\(e\) => \{\s*e\.stopPropagation\(\);\s*const queuedTask = queue\.find\(t => t\.id === track\.id\.toString\(\)\);.*?\} \?\s*\(\s*<X className="h-4 w-4" />\s*\)\s*:\s*queue\.find\(t => t\.id === track\.id\.toString\(\)\)\?\.status === \'completed\' \?\s*\(\s*<Check className="h-4 w-4" />\s*\)\s*:\s*\(\s*<Download className="h-4 w-4" />\s*\)\s*\}\s*</button>'

new_track_btn = """<button
                            onClick={(e) => {
                              e.stopPropagation();
                              const queuedTask = queue.find(t => t.id === track.id.toString());
                              if (queuedTask) {
                                if (queuedTask.status === 'downloading' || queuedTask.status === 'pending') {
                                  cancelDownload(queuedTask.id);
                                  return;
                                }
                                if (queuedTask.status === 'completed') {
                                  return;
                                }
                              }
                              addDownload({
                                id: track.id.toString(),
                                type: 'track',
                                title: track.title,
                                artist: track.artist || 'Unknown',
                                cover_url: track.cover_url || (details && 'cover_url' in details ? details.cover_url : undefined)
                              });
                            }}
                            className={`p-2 rounded-full transition-all hidden md:block ${
                              queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending'
                                ? 'text-red-500 hover:bg-red-500/10' 
                                : queue.find(t => t.id === track.id.toString())?.status === 'completed'
                                ? 'text-green-500/50'
                                : 'opacity-0 group-hover:opacity-100 hover:text-white hover:bg-white/10'
                            }`}
                            title={queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? 'Cancel Download' : 'Download FLAC'}
                          >
                            {queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? (
                              <X className="h-4 w-4" />
                            ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                              <Check className="h-4 w-4" />
                            ) : (
                              <Download className="h-4 w-4" />
                            )}
                          </button>"""

if re.search(old_btn_pattern, content, flags=re.DOTALL):
    content = re.sub(old_btn_pattern, new_track_btn, content, flags=re.DOTALL)
else:
    print("Failed to find old track button to replace")

# I also need to replace the first track button because there is one in the top track section of artist modal and one in the album modal.
# Both were probably corrupted.
# My earlier regex replaced ONE of them or both? re.sub replaces ALL occurrences!
# Let's see if the regex fixes both.

file_path.write_text(content, encoding='utf-8')
print("Fixed track buttons")
