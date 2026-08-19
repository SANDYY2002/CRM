import { useEffect, useState } from 'react';
import { ArrowLeft, CalendarDays, ChevronRight, Mail, MessageCircle, MoreHorizontal, Phone, Plus, StickyNote, Tag, UserRound } from 'lucide-react';
import { motion } from 'framer-motion';
import { api, type Customer, type Conversation, type Lead } from '../lib/api';

export function CustomerDetailPage({ id, onBack }: { id: number; onBack: () => void }) {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([api.customer(id), api.conversations(), api.leads()])
      .then(([record, allConversations, allLeads]) => {
        setCustomer(record);
        setConversations(allConversations.filter((item) => item.customer === id));
        setLeads(allLeads.filter((item) => item.customer === id));
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <section className="page-view"><button className="back-button" onClick={onBack}><ArrowLeft size={17}/> Back to customers</button><div className="empty-state glass-card"><strong>Loading customer…</strong><p>Fetching the live record from Django.</p></div></section>;
  if (error || !customer) return <section className="page-view"><button className="back-button" onClick={onBack}><ArrowLeft size={17}/> Back to customers</button><div className="empty-state glass-card"><strong>Customer unavailable</strong><p>{error || 'The requested customer was not found.'}</p></div></section>;

  const fullName = `${customer.first_name} ${customer.last_name || ''}`.trim();
  const latestConversation = conversations[0];
  const latestLead = leads[0];

  return <section className="page-view detail-view">
    <div className="detail-toolbar"><button className="back-button" onClick={onBack}><ArrowLeft size={17}/> Back to customers</button></div>
    <div className="profile-hero glass-card"><div className="profile-glow"/><div className="detail-avatar">{customer.first_name[0]}{customer.last_name?.[0] || ''}</div><div className="profile-main"><div className="eyebrow">CUSTOMER 360°</div><h1>{fullName}</h1><p>{customer.company || 'Independent customer'}</p><div className="hero-tags">{(customer.tags || []).map((tag) => <span className="tag" key={tag.id}><Tag size={11}/>{tag.name}</span>)}</div></div><div className="hero-actions"><button className="primary-button"><MessageCircle size={16}/> Message</button><button className="secondary-button"><Plus size={16}/> Add task</button></div></div>
    <div className="detail-grid"><main className="detail-main">
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Overview</h2><p>Live contact information from your CRM record</p></div><button className="icon-button"><MoreHorizontal size={18}/></button></div><div className="contact-grid"><div><span>Email</span><strong><Mail size={15}/>{customer.email || 'Not provided'}</strong></div><div><span>Phone</span><strong><Phone size={15}/>{customer.phone || 'Not provided'}</strong></div><div><span>Company</span><strong><UserRound size={15}/>{customer.company || 'Independent'}</strong></div><div><span>Created</span><strong><CalendarDays size={15}/>{new Date(customer.updated_at || customer.created_at || Date.now()).toLocaleDateString()}</strong></div></div></section>
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Activity</h2><p>Only real conversations and leads are shown here</p></div></div><div className="timeline">{latestConversation && <motion.div className="timeline-item" initial={{opacity:0,x:-8}} animate={{opacity:1,x:0}}><div className="timeline-icon whatsapp"><MessageCircle size={15}/></div><div><strong>{latestConversation.channel_name} conversation</strong><p>Status: {latestConversation.status}</p><time>{latestConversation.last_message_at ? new Date(latestConversation.last_message_at).toLocaleString() : 'No messages yet'}</time></div></motion.div>}{latestLead && <div className="timeline-item"><div className="timeline-icon lead"><ChevronRight size={15}/></div><div><strong>{latestLead.title}</strong><p>{latestLead.status} · NPR {Number(latestLead.value || 0).toLocaleString()}</p><time>{new Date(latestLead.updated_at || Date.now()).toLocaleString()}</time></div></div>}{!latestConversation && !latestLead && <div className="empty-state compact"><strong>No activity yet</strong><p>This customer has no stored conversations or leads.</p></div>}</div></section>
    </main><aside className="detail-aside"><section className="glass-card detail-section"><div className="section-heading"><div><h2>Relationship</h2><p>Live CRM signals</p></div></div><div className="metric-stack"><div><span>Lead status</span><strong className="status-pill">{latestLead?.status || 'No lead'} <ChevronRight size={13}/></strong></div><div><span>Conversations</span><strong>{conversations.length}</strong></div><div><span>Leads</span><strong>{leads.length}</strong></div></div></section><section className="glass-card detail-section"><div className="section-heading"><div><h2>Notes</h2><p>Stored on the customer record</p></div><button className="icon-button"><Plus size={17}/></button></div><div className="note-card"><StickyNote size={16}/><p>{customer.notes || 'No notes stored for this customer.'}</p></div></section></aside></div>
  </section>;
}
