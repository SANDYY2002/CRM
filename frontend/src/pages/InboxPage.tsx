import { useEffect, useMemo, useState } from 'react';
import { Archive, ChevronDown, FileText, Image, MoreHorizontal, Paperclip, Phone, Search, Send, Smile, UserPlus, Video } from 'lucide-react';
import { motion } from 'framer-motion';
import { api, type Conversation, type Message } from '../lib/api';
import { connectConversation } from '../lib/realtime';

const seed = [
  { id: 1, name: 'Ram Chhetri', channel: 'WhatsApp', preview: 'Is room 204 available tomorrow?', time: '2m', unread: 3, initial: 'RC', status: 'online' },
  { id: 2, name: 'Maya Studio', channel: 'Instagram', preview: 'Can you send me the pricing?', time: '8m', unread: 1, initial: 'MS', status: 'online' },
];

const fallbackMessages = [
  { id: 1, direction: 'inbound', content: 'Hi! I wanted to check whether room 204 is available tomorrow.', created_at: '10:42 AM' },
  { id: 2, direction: 'outbound', content: 'Hi Ram! Yes, room 204 is currently available. I can help you reserve it.', created_at: '10:43 AM' },
  { id: 3, direction: 'inbound', content: 'Perfect. What is the rate for one night?', created_at: '10:44 AM' },
];

export function InboxPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [draft, setDraft] = useState('');
  const [typing, setTyping] = useState(false);

  useEffect(() => {
    api.conversations().then((items) => {
      setConversations(items);
      setSelected(items[0] || null);
    }).catch(() => setConversations([]));
  }, []);

  useEffect(() => {
    if (!selected) return;
    setMessages([]);
    api.conversationMessages(selected.id).then(setMessages).catch(() => setMessages([]));
    api.markConversationRead(selected.id).catch(() => undefined);
    return connectConversation(selected.id, {
      onMessage: (message) => setMessages((current) => current.some((item) => item.id === message.id) ? current : [...current, message]),
      onTyping: setTyping,
    });
  }, [selected]);

  const visible = useMemo(() => {
    if (!conversations.length) return seed.filter((item) => `${item.name} ${item.preview}`.toLowerCase().includes(query.toLowerCase()));
    return conversations.filter((item) => `${item.customer_name} ${item.channel_name}`.toLowerCase().includes(query.toLowerCase()));
  }, [conversations, query]);

  const send = async () => {
    const text = draft.trim();
    if (!text || !selected) return;
    try {
      const message = await api.sendMessage(selected.id, text);
      setMessages((current) => [...current, message]);
      setDraft('');
    } catch {
      // Keep the composer intact when the API is unavailable.
    }
  };

  const selectedName = selected?.customer_name || 'Ram Chhetri';
  const selectedChannel = selected?.channel_name || 'WhatsApp';
  const renderedMessages = messages.length ? messages : fallbackMessages;

  return <main className="workspace-page inbox-page">
    <div className="orb orb-one"/><div className="orb orb-two"/>
    <header className="workspace-header glass-panel">
      <div><p className="eyebrow">CUSTOMER COMMUNICATION</p><h1>Unified Inbox</h1><p className="muted">Every conversation, every channel, one calm workspace.</p></div>
      <div className="inbox-actions"><span className="live"><i/> Live</span><button className="icon-button"><Archive size={18}/></button></div>
    </header>
    <section className="inbox-shell glass-panel">
      <aside className="conversation-sidebar">
        <div className="inbox-tabs"><button className="tab active">All <b>{conversations.reduce((sum, item) => sum + item.unread_count, 0) || 12}</b></button><button className="tab">Assigned</button><button className="tab">Unread</button></div>
        <div className="search inbox-search"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search conversations..."/></div>
        <div className="conversation-list">{visible.map((item) => {
          const isSeed = 'preview' in item;
          const id = item.id;
          const name = isSeed ? item.name : item.customer_name;
          const channel = isSeed ? item.channel : item.channel_name;
          const preview = isSeed ? item.preview : `Conversation · ${item.status}`;
          const initial = name.split(' ').map((part) => part[0]).join('').slice(0,2).toUpperCase();
          const unread = isSeed ? item.unread : item.unread_count;
          return <button key={id} onClick={() => !isSeed && setSelected(item as Conversation)} className={`conversation-item ${selected?.id === id ? 'selected' : ''}`}>
            <div className="avatar-wrap"><div className="avatar conversation-avatar">{initial}</div><i className="presence online"/></div>
            <div className="conversation-copy"><div><strong>{name}</strong><small>{isSeed ? item.time : 'live'}</small></div><p><span className={`channel-mini ${channel.toLowerCase()}`}>{channel[0]}</span>{preview}</p></div>
            {unread > 0 && <span className="unread">{unread}</span>}
          </button>;
        })}</div>
      </aside>
      <section className="chat-panel">
        <header className="chat-header"><div className="chat-person"><div className="avatar large">{selectedName.split(' ').map((part) => part[0]).join('').slice(0,2)}</div><div><strong>{selectedName}</strong><span><i className="presence online"/> {selectedChannel} · Active</span></div></div><div className="chat-tools"><button className="icon-button"><Phone size={18}/></button><button className="icon-button"><Video size={18}/></button><button className="icon-button"><MoreHorizontal size={19}/></button></div></header>
        <div className="message-area"><div className="date-divider"><span>Today</span></div>{renderedMessages.map((message, index) => <motion.div key={message.id} className={`message-row ${message.direction === 'outbound' ? 'out' : 'in'}`} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{delay:index*.03}}><div className="message-bubble">{message.content}<time>{new Date(message.created_at).toLocaleTimeString([], { hour:'numeric', minute:'2-digit' })}</time></div></motion.div>)}{typing && <div className="typing"><span/><span/><span/> Customer is typing...</div>}</div>
        <div className="composer"><div className="composer-inner"><textarea value={draft} onChange={e=>setDraft(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();void send();}}} placeholder="Write a message..."/><div className="composer-tools"><button><Paperclip size={18}/></button><button><Image size={18}/></button><button><FileText size={18}/></button><button><Smile size={18}/></button></div><button className="send-button" onClick={()=>void send()}><Send size={17}/></button></div><span className="composer-hint">Enter to send · Shift + Enter for a new line</span></div>
      </section>
      <aside className="customer-panel"><div className="customer-cover"/><div className="customer-profile"><div className="avatar profile-avatar">{selectedName.split(' ').map((part)=>part[0]).join('').slice(0,2)}</div><h2>{selectedName}</h2><p>Customer · {selectedChannel}</p><div className="customer-actions"><button><Phone size={16}/> Call</button><button><UserPlus size={16}/> Assign</button></div></div><div className="customer-details"><div><span>Contact</span><strong>+977 98XXXXXXXX</strong><strong>customer@example.com</strong></div><div><span>Tags</span><div className="tags"><b>VIP</b><b>Hot Lead</b></div></div><div><span>Lead status</span><strong className="status-pill">Qualified <ChevronDown size={13}/></strong></div><div><span>Notes</span><p>Customer context will become fully data-driven as the Customer 360 API expands.</p></div></div></aside>
    </section>
  </main>;
}
