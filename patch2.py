import re

with open('frontend/src/components/ui/progressive-blur-modal.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''  const [isZipping, setIsZipping] = useState(false);
  const [zipStatus, setZipStatus] = useState<string>('');

  const handleDownloadAll = async () => {
    if (type === 'artist') {
      tracks.forEach(track => {
        if (!queue.some(t => t.id === track.id.toString())) {
          addDownload({
            id: track.id.toString(),
            type: 'track',
            title: track.title,
            artist: track.artist
          });
        }
      });
      return;
    }

    if (details?.id && !isZipping) {
      setIsZipping(true);
      setZipStatus('Starting...');
      
      const apiType = type === 'ep' ? 'album' : type;
      
      try {
        const startRes = await fetch(http://localhost:8000/api/download/collection/start/\/\);
        if (!startRes.ok) throw new Error('Failed to start download');
        const startData = await startRes.json();
        const taskId = startData.task_id;
        
        const checkStatus = async () => {
          try {
            const statusRes = await fetch(http://localhost:8000/api/download/collection/status/\);
            const statusData = await statusRes.json();
            
            if (statusData.status === 'processing') {
              setZipStatus(statusData.message || 'Zipping...');
              setTimeout(checkStatus, 3000);
            } else if (statusData.status === 'ready') {
              setZipStatus('Done!');
              const a = document.createElement('a');
              a.href = http://localhost:8000/api/download/collection/file/\;
              a.download = '';
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              setTimeout(() => { setIsZipping(false); setZipStatus(''); }, 2000);
            } else {
              setZipStatus('Error!');
              setTimeout(() => { setIsZipping(false); setZipStatus(''); }, 3000);
            }
          } catch (e) {
            setZipStatus('Error!');
            setTimeout(() => { setIsZipping(false); setZipStatus(''); }, 3000);
          }
        };
        
        setTimeout(checkStatus, 2000);
      } catch (e) {
        setZipStatus('Error!');
        setTimeout(() => { setIsZipping(false); setZipStatus(''); }, 3000);
      }
    }
  };'''

pattern = r'  const \[isZipping, setIsZipping\] = useState\(false\);.*?  const handleDownloadAll = \(\) => \{.*?(?=\n  if \(\!isOpen \|\| \!mounted\))'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('frontend/src/components/ui/progressive-blur-modal.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
