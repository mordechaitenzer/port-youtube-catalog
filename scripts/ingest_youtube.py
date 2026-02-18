import requests, os, json, isodate, re
from datetime import datetime

def fetch_data():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    playlist_url = os.environ.get('PLAYLIST_URL')
    playlist_id = re.search(r"list=([^&]+)", playlist_url).group(1)
    
    entities = []

    # 1. Playlist Ingestion
    pl_url = f"https://www.googleapis.com/youtube/v3/playlists?part=snippet,contentDetails&id={playlist_id}&key={api_key}"
    pl_resp = requests.get(pl_url).json()
    if 'items' in pl_resp and len(pl_resp['items']) > 0:
        pl = pl_resp['items'][0]
        entities.append({
            "identifier": playlist_id,
            "blueprint": "youtube_playlist",
            "title": pl["snippet"]["title"],
            "properties": {
                "link": playlist_url,
                "playlistId": playlist_id,
                "videoCount": pl["contentDetails"]["itemCount"],
                "lastUpdatedAt": datetime.utcnow().isoformat() + "Z"
            }
        })

    # 2. Videos Ingestion
    v_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&maxResults=50&playlistId={playlist_id}&key={api_key}"
    v_items = requests.get(v_url).json().get('items', [])

    for item in v_items:
        vid = item['contentDetails']['videoId']
        v_info_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails,snippet&id={vid}&key={api_key}"
        v_info_resp = requests.get(v_info_url).json()
        
        if 'items' in v_info_resp and len(v_info_resp['items']) > 0:
            v_info = v_info_resp['items'][0]
            snippet = v_info['snippet']
            stats = v_info['statistics']
            
            entities.append({
                "identifier": vid,
                "blueprint": "youtube_video",
                "title": snippet['title'],
                "properties": {
                    "title": snippet['title'],
                    "titleLength": len(snippet['title']),
                    "link": f"https://www.youtube.com/watch?v={vid}",
                    "publishedAt": snippet['publishedAt'],
                    "thumbnailUrl": snippet['thumbnails'].get('high', {}).get('url', ''),
                    "description": snippet.get('description', '')[:500],
                    "channelTitle": snippet.get('channelTitle', ''),
                    "durationSeconds": int(isodate.parse_duration(v_info['contentDetails']['duration']).total_seconds()),
                    "viewCount": int(stats.get('viewCount', 0)),
                    "likeCount": int(stats.get('likeCount', 0)),
                    "commentCount": int(stats.get('commentCount', 0))
                },
                "relations": {"playlist": playlist_id}
            })
    
    with open('entities.json', 'w') as f:
        json.dump(entities, f)

if __name__ == "__main__":
    fetch_data()
