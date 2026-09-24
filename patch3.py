import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content = file_path.read_text(encoding='utf-8')

# Let's use regex to replace handleDownloadTrack
content = re.sub(
    r'const handleDownloadTrack = \(track: Track, e: React\.MouseEvent\) => \{.*?\}',
    '''const handleDownloadTrack = (track: Track, e: React.MouseEvent) => {
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
        artist: track.artist,
        cover_url: track.cover_url || (currentArtist ? currentArtist.picture_url : undefined)
      });
    }''',
    content,
    flags=re.DOTALL
)

# And now replace the download button rendering. There are 2 places where it checks queue.some(t => t.id === track.id.toString()) in the button
# We will do a generic replacement for the button block.
old_btn_pattern = r'<button[^>]*onClick=\{\(e\) => handleDownloadTrack\(track, e\)\}[^>]*>.*?</button>'

new_btn_code = '''<button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={p-2 rounded-full transition-all }
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

# Make sure X and Check are imported
if "import { Play, Pause, Download, Menu, ArrowLeft, Search, Volume2," in content:
    content = content.replace(
        "import { Play, Pause, Download, Menu, ArrowLeft, Search, Volume2,",
        "import { Play, Pause, Download, Menu, ArrowLeft, Search, Volume2, X, Check,"
    )

content = re.sub(old_btn_pattern, new_btn_code, content, flags=re.DOTALL)

file_path.write_text(content, encoding='utf-8')
print("Patched handleDownloadTrack and download button")
