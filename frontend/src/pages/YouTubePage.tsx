import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, CloudUpload, ExternalLink, Film, Loader2, Lock, PlaySquare, Youtube } from 'lucide-react';
import { api, type Channel } from '../lib/api';

export function YouTubePage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [channelId, setChannelId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [privacy, setPrivacy] = useState('private');
  const [video, setVideo] = useState<File | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ id?: string; title?: string } | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.channels().then((items) => {
      const youtube = items.filter((item) => item.type === 'youtube');
      setChannels(youtube);
      setChannelId(youtube.find((item) => item.is_active)?.id ? String(youtube.find((item) => item.is_active)!.id) : '');
    }).catch((err: Error) => setError(err.message));
  }, []);

  const activeChannel = useMemo(() => channels.find((channel) => String(channel.id) === channelId), [channels, channelId]);

  const connect = async () => {
    setConnecting(true);
    setError('');
    try {
      const { authorization_url } = await api.youtubeOAuthUrl();
      window.location.href = authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start YouTube OAuth.');
      setConnecting(false);
    }
  };

  const upload = async () => {
    if (!video || !channelId || !title.trim()) {
      setError('Choose a connected YouTube channel, video file, and title.');
      return;
    }
    setUploading(true);
    setError('');
    setResult(null);
    try {
      const data = await api.uploadYouTubeVideo({ channelId: Number(channelId), video, title, description, tags, privacy });
      setResult(data);
      setVideo(null);
      setTitle('');
      setDescription('');
      setTags('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return <section className="page-view">
    <div className="page-heading">
      <div><p className="eyebrow">VIDEO PUBLISHING</p><h1>YouTube Studio</h1><p className="muted">Connect a real YouTube channel and publish videos directly from CRM.</p></div>
      {!activeChannel && <button className="primary-button" onClick={connect} disabled={connecting}>{connecting ? <Loader2 size={16} className="spin"/> : <Youtube size={16}/>} Connect YouTube</button>}
    </div>

    {error && <div className="form-error">{error}</div>}
    {result && <div className="success-banner glass-card"><CheckCircle2 size={18}/><div><strong>Video uploaded</strong><p>{result.title || title}</p></div>{result.id && <a href={`https://youtube.com/watch?v=${result.id}`} target="_blank" rel="noreferrer"><ExternalLink size={16}/></a>}</div>}

    <div className="youtube-grid">
      <section className="glass-card upload-card">
        <div className="section-heading"><div><h2>Publish a video</h2><p>Uploads use your connected channel's OAuth permission.</p></div><Lock size={17}/></div>
        <label className="field"><span>YouTube channel</span><select value={channelId} onChange={e=>setChannelId(e.target.value)}><option value="">Select channel</option>{channels.map(channel=><option key={channel.id} value={channel.id}>{channel.name}</option>)}</select></label>
        <label className="field"><span>Video file</span><input type="file" accept="video/*" onChange={e=>setVideo(e.target.files?.[0] || null)}/>{video && <small>{video.name} · {(video.size / 1024 / 1024).toFixed(1)} MB</small>}</label>
        <label className="field"><span>Title</span><input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Enter a real video title"/></label>
        <label className="field"><span>Description</span><textarea value={description} onChange={e=>setDescription(e.target.value)} placeholder="Describe your video..." rows={6}/></label>
        <div className="field-row"><label className="field"><span>Tags</span><input value={tags} onChange={e=>setTags(e.target.value)} placeholder="crm, hotel, nepali"/></label><label className="field"><span>Privacy</span><select value={privacy} onChange={e=>setPrivacy(e.target.value)}><option value="private">Private</option><option value="unlisted">Unlisted</option><option value="public">Public</option></select></label></div>
        <button className="primary-button upload-button" onClick={upload} disabled={uploading || !activeChannel}>{uploading ? <><Loader2 size={16} className="spin"/> Uploading...</> : <><CloudUpload size={17}/> Upload to YouTube</>}</button>
      </section>

      <aside className="glass-card youtube-info"><div className="youtube-mark"><Youtube size={30}/></div><h2>Real publishing</h2><p>This module talks directly to YouTube Data API v3. There are no demo uploads or simulated video records.</p><div className="info-row"><Film size={16}/><span>Title, description and tags</span></div><div className="info-row"><PlaySquare size={16}/><span>Private, unlisted or public</span></div><div className="info-row"><Lock size={16}/><span>OAuth-controlled access</span></div>{activeChannel ? <div className="connected-state"><CheckCircle2 size={16}/> Connected: {activeChannel.name}</div> : <button className="secondary-button" onClick={connect}>Connect a channel first</button>}</aside>
    </div>
  </section>;
}
