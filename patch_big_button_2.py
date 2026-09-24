import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

old_btn_2_regex = r'<button\s+onClick=\{handleDownloadAll\}\s+disabled=\{!!queuedCollection && queuedCollection\.status === \'completed\'\}\s+className=\{`flex-1 max-w-\[160px\].*?</button>'

new_button_2 = """<button 
                   onClick={handleDownloadAll}
                   disabled={!!queuedCollection && queuedCollection.status === 'completed'}
                   className={`flex-1 max-w-[160px] h-12 rounded-full font-bold flex items-center justify-center gap-2 transition-all active:scale-95 border relative overflow-hidden ${
                     queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading')
                       ? "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20" 
                       : queuedCollection?.status === 'completed'
                       ? "bg-green-500/10 text-green-400 border-green-500/20"
                       : "bg-white/10 hover:bg-white/20 text-white border-white/10"
                   }`}
                 >
                   {queuedCollection && (queuedCollection.status === 'pending' || queuedCollection.status === 'downloading') ? (
                     <>
                       <X className="w-5 h-5 z-10" />
                       <span className="z-10">Cancel</span>
                     </>
                   ) : (
                     <>
                       {queuedCollection?.status === 'completed' ? (
                         <Check className="w-5 h-5 z-10" />
                       ) : (
                         <Download className="w-5 h-5 z-10" />
                       )}
                       <span className="z-10">
                         {queuedCollection?.status === 'completed' ? 'Downloaded' : 'Download'}
                       </span>
                     </>
                   )}
                 </button>"""

if re.search(old_btn_2_regex, content, flags=re.DOTALL):
    content = re.sub(old_btn_2_regex, new_button_2, content, flags=re.DOTALL)
    print("Replaced big button 2 with regex")
else:
    print("Failed to replace big button 2 with regex")

file_path.write_text(content, encoding='utf-8')
