import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content = file_path.read_text(encoding='utf-8')

# Let's find handleDownloadTrack
old_handle_download_track = '''    const handleDownloadTrack = (track: Track, e: React.MouseEvent) => {
      e.stopPropagation(); // Mencegah terklik play
      if (queue.some(t => t.id === track.id.toString())) return;
      
      addDownload({
        id: track.id.toString(),
        type: 'track',
        title: track.title,
        artist: track.artist,
        cover_url: track.cover_url || (currentArtist ? currentArtist.picture_url : undefined)
      });
    };'''

new_handle_download_track = '''    const handleDownloadTrack = (track: Track, e: React.MouseEvent) => {
      e.stopPropagation(); // Mencegah terklik play
      const queuedTask = queue.find(t => t.id === track.id.toString());
      
      if (queuedTask) {
        // If it's currently downloading or pending, clicking it again will cancel it
        if (queuedTask.status === 'downloading' || queuedTask.status === 'pending') {
          cancelDownload(queuedTask.id);
          return;
        }
        // If completed, don't redownload for now
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
    };'''

if old_handle_download_track in content:
    content = content.replace(old_handle_download_track, new_handle_download_track)
    print("Replaced handleDownloadTrack")
else:
    print("Could not find handleDownloadTrack")

# Let's find the button rendering
# We need to change queue.some(t => t.id === track.id.toString()) to check for downloading status
old_btn = '''                              <button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={p-2 rounded-full transition-all }
                                title="Download FLAC"
                              >
                                <Download className={h-4 w-4 } />
                              </button>'''

new_btn = '''                              <button
                                onClick={(e) => handleDownloadTrack(track, e)}
                                className={p-2 rounded-full transition-all }
                                title={queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? "Cancel Download" : "Download FLAC"}
                              >
                                {queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? (
                                  <X className="h-4 w-4 animate-pulse" />
                                ) : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? (
                                  <Check className="h-4 w-4" />
                                ) : (
                                  <Download className="h-4 w-4" />
                                )}
                              </button>'''

if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("Replaced download button")
else:
    print("Could not find download button")

file_path.write_text(content, encoding='utf-8')
