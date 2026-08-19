import { useEffect, useMemo, useState } from 'react';
import { Archive, ChevronDown, FileText, Image, MoreHorizontal, Paperclip, Phone, Search, Send, Smile, UserPlus, Video } from 'lucide-react';
import { motion } from 'framer-motion';
import { api, type Conversation, type Message } from '../lib/api';
import { connectConversation } from '../lib/realtime';

export function InboxPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [draft, setDraft] = useState('');
  const [typing, setTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState('');
  const [sendError, setSendError] = useState('');

  useEffect(() => {
    api.conversations()
      .then((items) => { setConversations(items); setSelected(items[0] || null); })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected) { setMessages([]); return; }
    setLoadingMessages(true);
    setMessages([]);
    api.conversationMessages(selected.id)
      .then(setMessages)
      .catch(() => setMessages([]))
      .finally(() => setLoadingMessages(false));
    api.markConversationRead(selected.id).then((updated) => {
      setConversations((current) => current.map((item) => item.id === updated.id ? updated : item));
      setSelected(updated);
    }).catch(() => undefined);
    return connectConversation(selected.id, {
      onMessage: (message) => setMessages((current) => current.some((item) => item.id === message.id) ? current : [...current, message]),
      onTyping: setTyping,
    });
  }, [selected?.id]);

  const visible = useMemo(() => conversations.filter((item) => `${item.customer_name} ${item.channel_name}`.toLowerCase().includes(query.toLowerCase())), [conversations, query]);

  const send = async () => {
    const text = draft.trim();
    if (!text || !selected) return;
    setSendError('');
    try {
      const message = await api.sendMessage(selected.id, text);
      setMessages((current) => current.some((item) => item.id === message.id) ? current : [...current, message]);
      setDraft('');
    } catch (err) {
      setSendError(err instanceof Error ? err.message : 'Message could not be sent.');
    }
  };

  const selectedName = selected?.customer_name || '';
  const selectedChannel = selected?.channel_name || '';

  return <main className="workspace-page inbox-page">
    <div className="orb orb-one"/><div className="orb orb-two"/>
    <header className="workspace-header glass-panel">
      <div><p className="eyebrow">CUSTOMER COMMUNICATION</p><h1>Unified Inbox</h1><p className="muted">Every real conversation, every connected channel, one workspace.</p></div>
      <div className="inbox-actions"><span className="live"><i/> Live</span><button className="icon-button"><Archive size={18}/></button></div>
    </header>
    <section className="inbox-shell glass-panel">
      <aside className="conversation-sidebar">
        <div className="inbox-tabs"><button className="tab active">All <b>{conversations.reduce((sum, item) => sum + item.unread_count, 0)}</b></button><button className="tab">Assigned</button><button className="tab">Unread</button></div>
        <div className="search inbox-search"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search conversations..."/></div>
        {loading && <div className="empty-state compact"><strong>Loading conversations…</strong></div>}
        {!loading && error && <div className="empty-state compact"><strong>Couldn't load conversations</strong><p>{error}</p></div>}
        {!loading && !error && visible.length === 0 && <div className="empty-state compact"><InboxIconFallback/><strong>{query ? 'No matches' : 'No conversations yet'}</strong><p>{query ? 'Try another search.' : 'Once a channel receives a real message, it will appear here.'}</p></div>}
        {!loading && !error && visible.length > 0 && <div className="conversation-list">{visible.map((item) => {
          const initial = item.customer_name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
          return <button key={item.id} onClick={() => setSelected(item)} className={`conversation-item ${selected?.id === item.id ? 'selected' : ''}`}>
            <div className="avatar-wrap"><div className="avatar conversation-avatar">{initial}</div><i className="presence online"/></div>
            <div className="conversation-copy"><div><strong>{item.customer_name}</strong><small>{item.last_message_at ? new Date(item.last_message_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''}</small></div><p><span className={`channel-mini ${item.channel_type}`}>{item.channel_type[0]?.toUpperCase()}</span>{item.channel_name} · {item.status}</p></div>
            {item.unread_count > 0 && <span className="unread">{item.unread_count}</span>}
          </button>;
        })}</div>}
      </aside>
      <section className="chat-panel">
        {!selected && !loading && !error && <div className="empty-state chat-empty"><Send size={30}/><strong>No conversation selected</strong><p>Connect a channel and receive a real customer message to begin.</p></div>}
        {selected && <>
          <header className="chat-header"><div className="chat-person"><div className="avatar large">{selectedName.split(' ').map((part) => part[0]).join('').slice(0,2)}</div><div><strong>{selectedName}</strong><span><i className="presence online"/> {selectedChannel} · {selected.status}</span></div></div><div className="chat-tools"><button className="icon-button"><Phone size={18}/></button><button className="icon-button"><Video size={18}/></button><button className="icon-button"><MoreHorizontal size={19}/></button></div></header>
          <div className="message-area"><div className="date-divider"><span>Conversation</span></div>{loadingMessages && <div className="empty-state compact"><strong>Loading messages…</strong></div>}{!loadingMessages && messages.length === 0 && <div className="empty-state compact"><strong>No messages yet</strong><p>This conversation does not contain any stored messages.</p></div>}{messages.map((message, index) => <motion.div key={message.id} className={`message-row ${message.direction === 'outbound' ? 'out' : 'in'}`} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} transition={{delay:index*.02}}><div className="message-bubble">{message.content}<time>{new Date(message.created_at).toLocaleTimeString([], { hour:'numeric', minute:'2-digit' })}</time></div></motion.div>)}{typing && <div className="typing"><span/><span/><span/> Customer is typing...</div>}</div>
          <div className="composer"><div className="composer-inner"><textarea value={draft} onChange={e=>setDraft(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();void send();}}} placeholder="Write a message..."/><div className="composer-tools"><button><Paperclip size={18}/></button><button><Image size={18}/></button><button><FileText size={18}/></button><button><Smile size={18}/></button></div><button className="send-button" onClick={()=>void send()} disabled={!draft.trim()}><Send size={17}/></button></div>{sendError && <span className="composer-error">{sendError}</span>}<span className="composer-hint">Enter to send · Shift + Enter for a new line</span></div>
        </>}
      </section>
      <aside className="customer-panel">{selected ? <><div className="customer-cover"/><div className="customer-profile"><div className="avatar profile-avatar">{selectedName.split(' ').map((part)=>part[0]).join('').slice(0,2)}</div><h2>{selectedName}</h2><p>Customer · {selectedChannel}</p><div className="customer-actions"><button><Phone size={16}/> Call</button><button><UserPlus size={16}/> Assign</button></div></div><div className="customer-details"><div><span>Channel</span><strong>{selectedChannel}</strong></div><div><span>Status</span><strong className="status-pill">{selected.status} <ChevronDown size={13}/></strong></div><div><span>Unread</span><strong>{selected.unread_count}</strong></div><div><span>Assigned to</span><strong>{selected.assigned_to_name || 'Unassigned'}</strong></div></div></> : <div className="empty-state compact"><strong>Customer context</strong><p>Select a conversation to see customer information.</p></div>}</aside>
    </section>
  </main>;
}

function InboxIconFallback() {
  return <span className="empty-icon">◎</span>;
}
