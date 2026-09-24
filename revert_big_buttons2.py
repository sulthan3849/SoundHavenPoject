import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

# Revert button 2
old_btn_2_regex = r'<button\s+onClick=\{handleDownloadAll\}\s+disabled=\{!!queuedCollection && queuedCollection\.status === \'completed\'\}\s+className=\{`flex-1 max-w-\[160px\].*?</button>'

new_button_2 = """               <div className="flex flex-1 items-center gap-2 max-w-[220px]">
                 <button 
                   onClick={handleDownloadAll}
                   disabled={!!queuedCollection && queuedCollection.status !== 'error' && queuedCollection.status !== 'cancelled'}
                   className={`flex-1 h-12 rounded-full font-bold flex items-center justify-center gap-2 transition-all active:scale-95 border relative overflow-hidden ${
                     queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')
                       ? "bg-blue-500/10 text-blue-400 border-blue-500/20" 
                       : queuedCollection?.status === 'completed'
                       ? "bg-green-500/10 text-green-400 border-green-500/20"
                       : "bg-white/10 hover:bg-white/20 text-white border-white/10"
                   }`}
                 >
                   {queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') && (
                     <div className="absolute inset-0 bg-blue-500/10 animate-pulse" />
                   )}
                   <Download className={`w-5 h-5 z-10 ${queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') ? 'animate-bounce' : ''}`} />
                   <span className="z-10">
                     {queuedCollection 
                       ? (queuedCollection.status === 'downloading' ? `Downloading...` : 
                          queuedCollection.status === 'pending' ? 'Queued' : 
                          queuedCollection.status === 'completed' ? 'Downloaded' : 'Download') 
                       : 'Download'}
                   </span>
                 </button>
                 {queuedCollection && (queuedCollection.status === 'downloading' || queuedCollection.status === 'pending') && (
                   <button
                     onClick={(e) => { e.stopPropagation(); cancelDownload(queuedCollection.id); }}
                     className="h-12 w-12 rounded-full flex shrink-0 items-center justify-center border border-white/10 bg-white/5 hover:bg-red-500/20 hover:text-red-500 hover:border-red-500/30 transition-all"
                     title="Cancel Download"
                   >
                     <X className="w-5 h-5" />
                   </button>
                 )}
               </div>"""

if re.search(old_btn_2_regex, content, flags=re.DOTALL):
    content = re.sub(old_btn_2_regex, new_button_2, content, flags=re.DOTALL)
    print("Replaced big button 2 with regex")
else:
    print("Failed to replace big button 2 with regex")


# Revert handleDownloadAll
old_handle_all_regex = r'const handleDownloadAll = \(\) => \{.*?if \(queuedCollection && \(queuedCollection\.status === \'downloading\' \|\| queuedCollection\.status === \'pending\'\)\) \{.*?cancelDownload\(queuedCollection\.id\);.*?return;.*?\}[\s\n]*if \(\!queuedCollection \|\| queuedCollection\.status === \'error\' \|\| queuedCollection\.status === \'cancelled\'\) \{.*?addDownload.*?\}'

new_handle_all = """  const handleDownloadAll = () => {
    if (type === 'artist') {
      tracks.forEach(track => {
        const queuedTask = queue.find(t => t.id === track.id.toString());
        if (!queuedTask || queuedTask.status === 'error' || queuedTask.status === 'cancelled') {
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
  };"""

# A simpler way to replace handleDownloadAll is just splitting lines
lines = content.split('\n')
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "const handleDownloadAll =" in line:
        start_idx = i
    if start_idx != -1 and "};" in line and i > start_idx + 10:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    content = '\n'.join(lines[:start_idx]) + '\n' + new_handle_all + '\n' + '\n'.join(lines[end_idx+1:])
    print("Replaced handleDownloadAll")
else:
    print("Failed to replace handleDownloadAll")

file_path.write_text(content, encoding='utf-8')
