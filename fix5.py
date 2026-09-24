import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/glassmorphism-listen-app-block-shadcnui.tsx')
content = file_path.read_text(encoding='utf-8')

# Fix className={p-2 rounded-full transition-all }
# We want it to be className={`p-2 rounded-full transition-all ${queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? 'text-red-500 hover:bg-red-500/10' : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? 'text-green-500/50' : 'text-foreground/40 hover:text-foreground hover:bg-foreground/10'}`}
correct_class_name = "className={`p-2 rounded-full transition-all ${queue.find(t => t.id === track.id.toString())?.status === 'downloading' || queue.find(t => t.id === track.id.toString())?.status === 'pending' ? 'text-red-500 hover:bg-red-500/10' : queue.find(t => t.id === track.id.toString())?.status === 'completed' ? 'text-green-500/50' : 'text-foreground/40 hover:text-foreground hover:bg-foreground/10'}`}"

content = content.replace("className={p-2 rounded-full transition-all }", correct_class_name)

# Fix handleDownloadTrack extra `});`
bad_handle = """      addDownload({
        id: track.id.toString(),
        type: 'track',
        title: track.title,
        artist: track.artist,
        cover_url: track.cover_url || (currentArtist ? currentArtist.picture_url : undefined)
      });
    });
  };"""
good_handle = """      addDownload({
        id: track.id.toString(),
        type: 'track',
        title: track.title,
        artist: track.artist,
        cover_url: track.cover_url || (currentArtist ? currentArtist.picture_url : undefined)
      });
    };"""
content = content.replace(bad_handle, good_handle)

file_path.write_text(content, encoding='utf-8')
