import pathlib

file_path_modal = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
lines = file_path_modal.read_text(encoding='utf-8').splitlines()

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

def replace_button_at(lines_list, start_idx, new_btn):
    # Find the closing </button>
    end_idx = -1
    for j in range(start_idx, start_idx+30):
        if '</button>' in lines_list[j]:
            end_idx = j
            break
    if end_idx != -1:
        return lines_list[:start_idx] + new_btn.splitlines() + lines_list[end_idx+1:]
    return lines_list

# We need to find the start indices again since line numbers may have shifted due to previous edits!
start1 = -1
for i, line in enumerate(lines):
    if 'const queuedTask = queue.find(t => t.id === track.id.toString());' in line:
        # backtrack to <button
        for k in range(i, max(0, i-5), -1):
            if '<button' in lines[k]:
                start1 = k
                break
        break

if start1 != -1:
    lines = replace_button_at(lines, start1, new_btn_1)
    print("Replaced button 1")
else:
    print("Failed to find button 1")

start2 = -1
for i, line in enumerate(lines):
    if 'const queuedTask = queue.find(t => t.id === track.id.toString());' in line:
        for k in range(i, max(0, i-5), -1):
            if '<button' in lines[k]:
                start2 = k
                break
        break

if start2 != -1:
    lines = replace_button_at(lines, start2, new_btn_2)
    print("Replaced button 2")
else:
    print("Failed to find button 2")


file_path_modal.write_text('\n'.join(lines), encoding='utf-8')
