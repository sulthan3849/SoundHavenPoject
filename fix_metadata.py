import pathlib
import re

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/frontend/src/components/ui/progressive-blur-modal.tsx')
content = file_path.read_text(encoding='utf-8')

# Fix handleDownloadAll for Albums/Playlists
old_handle_all_regex = r'addDownload\(\{\s*id: details\.id\.toString\(\),\s*type: type as \'album\' \| \'playlist\',\s*title: details\.title,\s*artist: details\.artist \|\| \'Unknown\',\s*cover_url: details\.cover_url\s*\}\);'

new_handle_all_add = """addDownload({
          id: details.id.toString(),
          type: type as 'album' | 'playlist',
          title: details.title,
          artist: ('artist' in details ? details.artist : ('creator' in details ? details.creator : 'Unknown')) as string,
          cover_url: ('coverUrl' in details ? details.coverUrl : ('cover_url' in details ? details.cover_url : undefined)) as string | undefined
        });"""

if re.search(old_handle_all_regex, content, flags=re.DOTALL):
    content = re.sub(old_handle_all_regex, new_handle_all_add, content, flags=re.DOTALL)
    print("Fixed handleDownloadAll for albums/playlists")
else:
    print("Failed to fix handleDownloadAll for albums/playlists")

# Fix handleDownloadAll for Tracks (Artist profile top tracks)
# wait, for artist, details is actually artist info, but let's check
old_handle_all_artist_regex = r'addDownload\(\{\s*id: track\.id\.toString\(\),\s*type: \'track\',\s*title: track\.title,\s*artist: track\.artist,\s*cover_url: track\.cover_url \|\| \(details && \'picture_url\' in details \? details\.picture_url : undefined\)\s*\}\);'
new_handle_all_artist_add = """addDownload({
            id: track.id.toString(),
            type: 'track',
            title: track.title,
            artist: track.artist,
            cover_url: track.cover_url || (details && 'picture_url' in details ? details.picture_url : (details && 'coverUrl' in details ? details.coverUrl : undefined))
          });"""
if re.search(old_handle_all_artist_regex, content, flags=re.DOTALL):
    content = re.sub(old_handle_all_artist_regex, new_handle_all_artist_add, content, flags=re.DOTALL)
    print("Fixed handleDownloadAll for artist tracks")
else:
    print("Failed to fix handleDownloadAll for artist tracks")

# Fix individual track buttons
old_track_btn_regex = r'addDownload\(\{\s*id: track\.id\.toString\(\),\s*type: \'track\',\s*title: track\.title,\s*artist: track\.artist \|\| \'Unknown\',\s*cover_url: track\.cover_url \|\| \(details && \'cover_url\' in details \? details\.cover_url : undefined\)\s*\}\);'
new_track_btn_add = """addDownload({
                                 id: track.id.toString(),
                                 type: 'track',
                                 title: track.title,
                                 artist: track.artist || 'Unknown',
                                 cover_url: track.cover_url || (details && 'coverUrl' in details ? details.coverUrl : (details && 'cover_url' in details ? details.cover_url : undefined))
                               });"""

if re.search(old_track_btn_regex, content, flags=re.DOTALL):
    content = re.sub(old_track_btn_regex, new_track_btn_add, content, flags=re.DOTALL)
    print("Fixed individual track buttons")
else:
    print("Failed to fix individual track buttons")

file_path.write_text(content, encoding='utf-8')
