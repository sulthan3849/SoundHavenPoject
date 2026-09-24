import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

# 1. Update handleDownloadAll
old_handle_download_all = '''  const handleDownloadAll = () => {
    if (type === 'artist') {
      tracks.forEach(track => {
        if (!queue.some(t => t.id === track.id.toString())) {
          addDownload({
            id: track.id.toString(),
            type: 'track',
            title: track.title,
            artist: track.artist,
            cover_url: track.cover_url || (details && 'picture_url' in details ? details.picture_url : undefined)
          });
        }
      });
    } else if (details && 'id' in details) {
      if (!queuedCollection) {
        addDownload({
          id: details.id.toString(),
          type: type as 'album' | 'playlist',
          title: details.title,
          artist: details.artist || 'Unknown',
          cover_url: details.cover_url
        });
      }
    }
  };'''

new_handle_download_all = '''  const handleDownloadAll = () => {
    if (type === 'artist') {
      tracks.forEach(track => {
        const queuedTask = queue.find(t => t.id === track.id.toString());
        if (!queuedTask) {
          addDownload({
            id: track.id.toString(),
            type: 'track',
            title: track.title,
            artist: track.artist,
            cover_url: track.cover_url || (details && 'picture_url' in details ? details.picture_url : undefined)
          });
        }
      });
    } else if (details && 'id' in details) {
      if (queuedCollection && (queuedCollection.status === 'downloading' || queuedCollection.status === 'pending')) {
        cancelDownload(queuedCollection.id);
        return;
      }
      if (!queuedCollection || queuedCollection.status === 'error' || queuedCollection.status === 'cancelled') {
        addDownload({
          id: details.id.toString(),
          type: type as 'album' | 'playlist',
          title: details.title,
          artist: details.artist || 'Unknown',
          cover_url: details.cover_url
        });
      }
    }
  };'''

content = content.replace(old_handle_download_all, new_handle_download_all)

# 2. Fix the "Download All" button to not be disabled when downloading, and show X icon or cancel text
# There are two instances of "Download All" buttons (one for small screens, one for large)
# We will use regex to replace both.
# The old pattern has disabled={...} and className={...}
old_download_btn_pattern = r'<button\s+onClick=\{handleDownloadAll\}\s+disabled=\{!!queuedCollection && queuedCollection\.status !== \'error\' && queuedCollection\.status !== \'cancelled\'\}\s+className=\{[^]+\}\s*>\s*(.*?)\s*</button>'

# Wait, regex for this might be tricky. Let's just do generic text replacement for the disabled prop and button content.
# Remove disabled prop if queuedCollection is downloading/pending
content = content.replace(
    "disabled={!!queuedCollection && queuedCollection.status !== 'error' && queuedCollection.status !== 'cancelled'}",
    "disabled={!!queuedCollection && queuedCollection.status === 'completed'}"
)

# Replace "Downloading..." text with a condition
content = content.replace(
    "queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')\n                          ? 'text-blue-400 border-blue-400/30'\n                          : queuedCollection && queuedCollection.status === 'completed'\n                            ? 'text-green-500 border-green-500/30 opacity-50'\n                            : 'text-foreground/80 border-border hover:bg-foreground/5'",
    "queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')\n                          ? 'text-red-400 border-red-400/30 hover:bg-red-400/10'\n                          : queuedCollection && queuedCollection.status === 'completed'\n                            ? 'text-green-500 border-green-500/30 opacity-50'\n                            : 'text-foreground/80 border-border hover:bg-foreground/5'"
)
content = content.replace(
    "queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')\n                        ? 'text-blue-400 border-blue-400/30'\n                        : queuedCollection && queuedCollection.status === 'completed'\n                          ? 'text-green-500 border-green-500/30 opacity-50'\n                          : 'text-foreground/80 border-border hover:bg-foreground/5'",
    "queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')\n                        ? 'text-red-400 border-red-400/30 hover:bg-red-400/10'\n                        : queuedCollection && queuedCollection.status === 'completed'\n                          ? 'text-green-500 border-green-500/30 opacity-50'\n                          : 'text-foreground/80 border-border hover:bg-foreground/5'"
)

# Change the content of the button
content = content.replace(
    "queuedCollection.status === 'downloading' || queuedCollection.status === 'pending' ? (\n                          <>\n                            <Download className=\"w-4 h-4 animate-pulse\" />\n                            Downloading...\n                          </>\n                        )",
    "queuedCollection.status === 'downloading' || queuedCollection.status === 'pending' ? (\n                          <>\n                            <X className=\"w-4 h-4\" />\n                            Cancel\n                          </>\n                        )"
)
content = content.replace(
    "queuedCollection.status === 'downloading' || queuedCollection.status === 'pending' ? (\n                        <>\n                          <Download className=\"w-4 h-4 animate-pulse\" />\n                          Downloading...\n                        </>\n                      )",
    "queuedCollection.status === 'downloading' || queuedCollection.status === 'pending' ? (\n                        <>\n                          <X className=\"w-4 h-4\" />\n                          Cancel\n                        </>\n                      )"
)

# 3. Update the track row download button in the modal
track_btn_pattern = r'<button\s+onClick=\{\(e\) => \{\s*e\.stopPropagation\(\);\s*if \(\!queue\.some\(t => t\.id === track\.id\.toString\(\)\)\) \{\s*addDownload\(\{\s*id: track\.id\.toString\(\),\s*type: \'track\',\s*title: track\.title,\s*artist: track\.artist \|\| \'Unknown\',\s*cover_url: track\.cover_url \|\| \(details && \'cover_url\' in details \? details\.cover_url : undefined\)\s*\}\);\s*\}\s*\}\}\s+className=\{[^]+\}\s+title="Download FLAC"\s*>\s*<Download className=\{[^]+\} />\s*</button>'

new_track_btn = '''<button
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
                            className={p-2 rounded-full transition-all hidden md:block }
                            title={queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? "Cancel Download" : "Download FLAC"}
                          >
                            {queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? (
                              <X className="h-4 w-4" />
                            ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                              <Check className="h-4 w-4" />
                            ) : (
                              <Download className="h-4 w-4" />
                            )}
                          </button>'''

content = re.sub(track_btn_pattern, new_track_btn, content, flags=re.DOTALL)

# Also make sure X and Check are imported
if "import { Play, Pause, Download, Heart, Share2, Music2" in content:
    content = content.replace(
        "import { Play, Pause, Download, Heart, Share2, Music2",
        "import { Play, Pause, Download, Heart, Share2, Music2, X, Check"
    )

file_path.write_text(content, encoding='utf-8')
print("Patched progressive-blur-modal")
