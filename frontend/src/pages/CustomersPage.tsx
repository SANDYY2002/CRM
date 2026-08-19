import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, MoreHorizontal, Phone, Plus, Search, Tag, Users } from 'lucide-react';
import { api } from '../lib/api';

type Customer = { id: number; first_name: string; last_name?: string; email?: string; phone?: string; company?: string; tags?: { id: number; name: string }[] };
const fallback: Customer[] = [
  { id: 1, first_name: 'Ram', last_name: 'Chhetri', email: 'ram@example.com', phone: '+977 9800000000', company: 'Ram Holdings', tags: [{ id: 1, name: 'VIP' }] },
  { id: 2, first_name: 'Sita', last_name: 'Sharma', email: 'sita@example.com', phone: '+977 9811111111', company: 'Sharma Studio', tags: [{ id: 2, name: 'Hot Lead' }] },
  { id: 3, first_name: 'Maya', last_name: 'Gurung', email: 'maya@example.com', phone: '+977 9822222222', company: 'Maya Studio' },
];

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [query, setQuery] = useState('');
  useEffect(() => { api.customers().then(data => setCustomers(data as Customer[])).catch(() => setCustomers(fallback)); }, []);
  const visible = useMemo(() => (customers.length ? customers : fallback).filter(c => `${c.first_name} ${c.last_name || ''} ${c.email || ''} ${c.company || ''}`.toLowerCase().includes(query.toLowerCase())), [customers, query]);
  return <section className="page-view">
    <div className="page-heading"><div><p className="eyebrow">CUSTOMER RELATIONSHIPS</p><h1>Customers</h1><p className="muted">One beautiful place for every customer relationship.</p></div><button className="primary-button"><Plus size={17}/> New customer</button></div>
    <div className="toolbar glass-card"><div className="search wide"><Search size={17}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search by name, email, company..."/></div><div className="toolbar-stat"><Users size={17}/><strong>{visible.length}</strong><span>customers</span></div></div>
    <div className="customer-grid">{visible.map((customer, index) => <motion.article key={customer.id} className="customer-card glass-card" initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{delay:index*.04}} whileHover={{y:-4}}><div className="customer-card-top"><div className="customer-avatar">{customer.first_name[0]}{customer.last_name?.[0] || ''}</div><button className="icon-button"><MoreHorizontal size={18}/></button></div><h3>{customer.first_name} {customer.last_name}</h3><p>{customer.company || 'Independent customer'}</p><div className="contact-lines">{customer.email && <span><Mail size={14}/>{customer.email}</span>}{customer.phone && <span><Phone size={14}/>{customer.phone}</span>}</div><div className="tag-row">{(customer.tags || []).map(tag => <span className="tag" key={tag.id}><Tag size={11}/>{tag.name}</span>)}</div></motion.article>)}</div>
  </section>;
}
