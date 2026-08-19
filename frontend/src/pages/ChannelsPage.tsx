import { useEffect, useState } from 'react';
import { CheckCircle2, Facebook, Instagram, MessageCircle, Smartphone, Youtube } from 'lucide-react';
import { api, type Channel } from '../lib/api';

const providers = [
  { type:'facebook', name:'Facebook', icon:Facebook, description:'Connect Facebook messaging and supported Page events.' },
  { type:'instagram', name:'Instagram', icon:Instagram, description:'Connect a professional Instagram account for messaging and supported events.' },
  { type:'whatsapp', name:'WhatsApp', icon:MessageCircle, description:'Connect WhatsApp Business messaging through Meta.' },
  { type:'viber', name:'Viber', icon:Smartphone, description:'Connect a Viber bot/business channel for real inbound and outbound messages.' },
  { type:'youtube', name:'YouTube', icon:Youtube, description:'Connect a YouTube channel for publishing, video management and comments.' },
];

export function ChannelsPage() {
  const [channels,setChannels]=useState<Channel[]>([]);
  const [error,setError]=useState('');
  useEffect(()=>{api.channels().then(setChannels).catch((err:Error)=>setError(err.message));},[]);
  const youtubeConnect=async()=>{try{const response=await api.youtubeOAuthUrl();window.location.assign(response.authorization_url);}catch(err){setError(err instanceof Error?err.message:'Unable to start YouTube connection.');}};
  return <section className="page-view"><div className="page-heading"><div><p className="eyebrow">OMNICHANNEL</p><h1>Channels</h1><p className="muted">Connect real provider accounts to start receiving and sending real customer data.</p></div></div>{error&&<div className="form-error">{error}</div>}<div className="channel-grid">{providers.map(({type,name,icon:Icon,description})=>{const connected=channels.filter(channel=>channel.type===type&&channel.is_active);return <article className="glass-card channel-card" key={type}><div className="channel-card-top"><div className="channel-logo"><Icon size={22}/></div><span className={connected.length?'connected-badge':'disconnected-badge'}>{connected.length?<><CheckCircle2 size={14}/> Connected</>:'Not connected'}</span></div><h2>{name}</h2><p>{description}</p>{connected.length?<div className="connected-list">{connected.map(channel=><div key={channel.id}><strong>{channel.name}</strong><span>{channel.external_id}</span></div>)}</div>:type==='youtube'?<button className="primary-button full" onClick={()=>void youtubeConnect()}>Connect YouTube</button>:<button className="secondary-button full" disabled>Provider setup required</button>}</article>})}</div></section>;
}
