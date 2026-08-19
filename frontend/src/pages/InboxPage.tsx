import { useMemo, useState } from 'react';
import { Archive, ChevronDown, FileText, Image, MoreHorizontal, Paperclip, Phone, Search, Send, Smile, UserPlus, Video } from 'lucide-react';
import { motion } from 'framer-motion';

const seed = [
  { id: 1, name: 'Ram Chhetri', channel: 'WhatsApp', preview: 'Is room 204 available tomorrow?', time: '2m', unread: 3, initial: 'RC', status: 'online' },
  { id: 2, name: 'Maya Studio', channel: 'Instagram', preview: 'Can you send me the pricing?', time: '8m', unread: 1, initial: 'MS', status: 'online' },
  { id: 3, name: 'Sita Sharma', channel: 'Facebook', preview: 'Thanks, I will confirm shortly.', time: '16m', unread: 0, initial: 'SS', status: 'away' },
  { id: 4, name: 'Hari Thapa', channel: 'Viber', preview: 'Please share your location.', time: '31m', unread: 0, initial: 'HT', status: 'offline' },
  { id: 5, name: 'Alex Morgan', channel: 'WhatsApp', preview: 'I have a question about the package.', time: '1h', unread: 0, initial: 'AM', status: 'online' },
];

const messages = [
  { id: 1, side: 'in', text: 'Hi! I wanted to check whether room 204 is available tomorrow.', time: '10:42 AM' },
  { id: 2, side: 'out', text: 'Hi Ram! Yes, room 204 is currently available. I can help you reserve it.', time: '10:43 AM' },
  { id: 3, side: 'in', text: 'Perfect. What is the rate for one night?', time: '10:44 AM' },
  { id: 4, side: 'out', text: 'It is NPR 4,500 per night, including breakfast. Would you like me to hold it for you?', time: '10:45 AM' },
  { id: 5, side: 'in', text: 'Yes please. I will confirm the details in a few minutes.', time: '10:47 AM' },
];

export function InboxPage() {
  const [selected, setSelected] = useState(seed[0]);
  const [query, setQuery] = useState('');
  const [draft, setDraft] = useState('');
  const filtered = useMemo(() => seed.filter((item) => `${item.name} ${item.preview}`.toLowerCase().includes(query.toLowerCase())), [query]);

  return <main className="workspace-page inbox-page">
    <div className="orb orb-one" /><div className="orb orb-two" />
    <header className="workspace-header glass-panel">
      <div><p className="eyebrow">CUSTOMER COMMUNICATION</p><h1>Unified Inbox</h1><p className="muted">Every conversation, every channel, one calm workspace.</p></div>
      <div className="inbox-actions"><span className="live"><i /> Live</span><button className="icon-button"><Archive size={18}/></button></div>
    </header>
    <section className="inbox-shell glass-panel">
      <aside className="conversation-sidebar">
        <div className="inbox-tabs"><button className="tab active">All <b>12</b></button><button className="tab">Assigned</button><button className="tab">Unread</button></div>
        <div className="search inbox-search"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search conversations..." /></div>
        <div className="conversation-list">{filtered.map((item) => <button key={item.id} onClick={() => setSelected(item)} className={`conversation-item ${selected.id === item.id ? 'selected' : ''}`}><div className="avatar-wrap"><div className="avatar conversation-avatar">{item.initial}</div><i className={`presence ${item.status}`} /></div><div className="conversation-copy"><div><strong>{item.name}</strong><small>{item.time}</small></div><p><span className={`channel-mini ${item.channel.toLowerCase()}`}>{item.channel[0]}</span>{item.preview}</p></div>{item.unread > 0 && <span className="unread">{item.unread}</span>}</button>)}</div>
      </aside>
      <section className="chat-panel">
        <header className="chat-header"><div className="chat-person"><div className="avatar large">{selected.initial}</div><div><strong>{selected.name}</strong><span><i className="presence online" /> {selected.channel} · Active now</span></div></div><div className="chat-tools"><button className="icon-button"><Phone size={18}/></button><button className="icon-button"><Video size={18}/></button><button className="icon-button"><MoreHorizontal size={19}/></button></div></header>
        <div className="message-area"><div className="date-divider"><span>Today</span></div>{messages.map((message, index) => <motion.div key={message.id} className={`message-row ${message.side}`} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{delay:index*.04}}><div className="message-bubble">{message.text}<time>{message.time}</time></div></motion.div>)}<div className="typing"><span/><span/><span/> Ram is typing...</div></div>
        <div className="composer"><div className="composer-inner"><textarea value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => { if(e.key==='Enter' && !e.shiftKey){e.preventDefault();setDraft('')}}} placeholder="Write a message..."/><div className="composer-tools"><button><Paperclip size={18}/></button><button><Image size={18}/></button><button><FileText size={18}/></button><button><Smile size={18}/></button></div><button className="send-button" onClick={() => setDraft('')}><Send size={17}/></button></div><span className="composer-hint">Enter to send · Shift + Enter for a new line</span></div>
      </section>
      <aside className="customer-panel"><div className="customer-cover"/><div className="customer-profile"><div className="avatar profile-avatar">{selected.initial}</div><h2>{selected.name}</h2><p>Customer · {selected.channel}</p><div className="customer-actions"><button><Phone size={16}/> Call</button><button><UserPlus size={16}/> Assign</button></div></div><div className="customer-details"><div><span>Contact</span><strong>+977 98XXXXXXXX</strong><strong>ram@example.com</strong></div><div><span>Tags</span><div className="tags"><b>VIP</b><b>Hot Lead</b></div></div><div><span>Lead status</span><strong className="status-pill">Qualified <ChevronDown size={13}/></strong></div><div><span>Notes</span><p>Interested in a deluxe room. Follow up after confirmation.</p></div></div></aside>
    </section>
  </main>;
}
