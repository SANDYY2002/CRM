import { useEffect, useState } from 'react';
import { ArrowLeft, CalendarDays, Check, ChevronRight, Mail, MessageCircle, MoreHorizontal, Phone, Plus, StickyNote, Tag, UserRound } from 'lucide-react';
import { motion } from 'framer-motion';
import { api, type Customer } from '../lib/api';

const fallback: Customer = { id: 1, first_name: 'Ram', last_name: 'Chhetri', email: 'ram@example.com', phone: '+977 9800000000', company: 'Ram Holdings', notes: 'Interested in a deluxe room. Follow up after confirmation.', tags: [{ id: 1, name: 'VIP' }, { id: 2, name: 'Hotel' }] };

export function CustomerDetailPage({ id, onBack }: { id: number; onBack: () => void }) {
  const [customer, setCustomer] = useState<Customer>(fallback);
  useEffect(() => { api.customer(id).then(setCustomer).catch(() => setCustomer(fallback)); }, [id]);
  const fullName = `${customer.first_name} ${customer.last_name || ''}`.trim();
  return <section className="page-view detail-view">
    <div className="detail-toolbar"><button className="back-button" onClick={onBack}><ArrowLeft size={17} /> Back to customers</button></div>
    <div className="profile-hero glass-card"><div className="profile-glow" /><div className="detail-avatar">{customer.first_name[0]}{customer.last_name?.[0] || ''}</div><div className="profile-main"><div className="eyebrow">CUSTOMER 360°</div><h1>{fullName}</h1><p>{customer.company || 'Independent customer'} · Active relationship</p><div className="hero-tags">{(customer.tags || []).map(t => <span className="tag" key={t.id}><Tag size={11} />{t.name}</span>)}</div></div><div className="hero-actions"><button className="primary-button"><MessageCircle size={16} /> Message</button><button className="secondary-button"><Plus size={16} /> Add task</button></div></div>
    <div className="detail-grid"><main className="detail-main">
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Overview</h2><p>Contact details and relationship information</p></div><button className="icon-button"><MoreHorizontal size={18} /></button></div><div className="contact-grid"><div><span>Email</span><strong><Mail size={15} />{customer.email || 'Not provided'}</strong></div><div><span>Phone</span><strong><Phone size={15} />{customer.phone || 'Not provided'}</strong></div><div><span>Company</span><strong><UserRound size={15} />{customer.company || 'Independent'}</strong></div><div><span>Customer record</span><strong><CalendarDays size={15} />Active</strong></div></div></section>
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Recent activity</h2><p>Latest events across this relationship</p></div></div><div className="timeline"><motion.div className="timeline-item" initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}><div className="timeline-icon whatsapp"><MessageCircle size={15} /></div><div><strong>WhatsApp conversation opened</strong><p>Customer asked about room availability.</p><time>Today · 10:42 AM</time></div></motion.div><div className="timeline-item"><div className="timeline-icon note"><StickyNote size={15} /></div><div><strong>Note added</strong><p>Interested in a deluxe room. Follow up after confirmation.</p><time>Yesterday · 3:15 PM</time></div></div><div className="timeline-item"><div className="timeline-icon lead"><Check size={15} /></div><div><strong>Lead moved to Qualified</strong><p>Opportunity value: NPR 4,500</p><time>Aug 17 · 11:06 AM</time></div></div></div></section>
    </main><aside className="detail-aside">
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Relationship</h2><p>Key customer signals</p></div></div><div className="metric-stack"><div><span>Lead status</span><strong className="status-pill">Qualified <ChevronRight size={13} /></strong></div><div><span>Last contact</span><strong>2 minutes ago</strong></div><div><span>Channels</span><strong>3 connected</strong></div></div></section>
      <section className="glass-card detail-section"><div className="section-heading"><div><h2>Notes</h2><p>Private notes for your team</p></div><button className="icon-button"><Plus size={17} /></button></div><div className="note-card"><StickyNote size={16} /><p>{customer.notes || 'No notes yet.'}</p></div></section>
    </aside></div>
  </section>;
}
