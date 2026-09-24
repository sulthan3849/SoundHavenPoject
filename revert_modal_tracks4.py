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

def replace_button_at(lines_list, start_idx):
    # Find the closing </button>
    end_idx = -1
    for j in range(start_idx, start_idx+30):
        if '</button>' in lines_list[j]:
            end_idx = j
            break
    if end_idx != -1:
        return lines_list[:start_idx] + new_btn_1.splitlines() + lines_list[end_idx+1:]
    return lines_list

while True:
    found_and_replaced = False
    for i, line in enumerate(lines):
        if 'const queuedTask = queue.find(t => t.id === track.id.toString());' in line:
            # check if there is a <button around it
            start = -1
            for k in range(i, max(0, i-5), -1):
                if '<button' in lines[k]:
                    start = k
                    break
            
            if start != -1:
                # Replace it!
                lines = replace_button_at(lines, start)
                found_and_replaced = True
                print(f"Replaced button at line {start}")
                break # break the for loop to restart enumeration
    if not found_and_replaced:
        break

file_path_modal.write_text('\n'.join(lines), encoding='utf-8')
