import pathlib

file_path_modal = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content_modal = file_path_modal.read_text(encoding='utf-8')
lines = content_modal.splitlines()

new_btn_1 = """                           <button
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

new_btn_2 = """                        <button
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

def replace_block(lines, start_str):
    for i, line in enumerate(lines):
        if start_str in line:
            start = i - 2
            for j in range(i, i+30):
                if '</button>' in lines[j]:
                    return start, j
    return -1, -1

# We know the first one has `queue.find(t => t.id === track.id.toString());`
start1, end1 = replace_block(lines, "const queuedTask = queue.find(t => t.id === track.id.toString());")
if start1 != -1 and end1 != -1:
    lines = lines[:start1] + new_btn_1.splitlines() + lines[end1+1:]
    print("Replaced track button 1 in modal")
else:
    print("Failed to replace track button 1 in modal")

start2, end2 = replace_block(lines, "const queuedTask = queue.find(t => t.id === track.id.toString());")
if start2 != -1 and end2 != -1:
    lines = lines[:start2] + new_btn_2.splitlines() + lines[end2+1:]
    print("Replaced track button 2 in modal")
else:
    print("Failed to replace track button 2 in modal")

file_path_modal.write_text('\n'.join(lines), encoding='utf-8')
