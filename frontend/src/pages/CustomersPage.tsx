import { useEffect, useMemo, useState } from 'react';
import { Mail, MoreHorizontal, Phone, Plus, Search, Tag, Users } from 'lucide-react';
import { motion } from 'framer-motion';
import { api, type Customer } from '../lib/api';

export function CustomersPage({ onOpen }: { onOpen: (id: number) => void }) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.customers()
      .then(setCustomers)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const visible = useMemo(
    () => customers.filter((c) => `${c.first_name} ${c.last_name || ''} ${c.email || ''} ${c.company || ''}`.toLowerCase().includes(query.toLowerCase())),
    [customers, query],
  );

  return (
    <section className="page-view">
      <div className="page-heading">
        <div><p className="eyebrow">CUSTOMER RELATIONSHIPS</p><h1>Customers</h1><p className="muted">Every customer stored in your CRM database.</p></div>
        <button className="primary-button"><Plus size={17} /> New customer</button>
      </div>
      <div className="toolbar glass-card">
        <div className="search wide"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by name, email, company..." /></div>
        <div className="toolbar-stat"><Users size={17} /><strong>{customers.length}</strong><span>customers</span></div>
      </div>
      {loading && <div className="empty-state glass-card"><span className="loading-orb small" /><strong>Loading customers…</strong><p>Fetching current records from Django.</p></div>}
      {!loading && error && <div className="empty-state glass-card"><strong>Couldn't load customers</strong><p>{error}</p></div>}
      {!loading && !error && visible.length === 0 && <div className="empty-state glass-card"><Users size={28} /><strong>{query ? 'No matching customers' : 'No customers yet'}</strong><p>{query ? 'Try another search.' : 'Create your first customer to start building the CRM database.'}</p></div>}
      {!loading && !error && visible.length > 0 && <div className="customer-grid">{visible.map((customer, index) => (
        <motion.article key={customer.id} className="customer-card glass-card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .04 }} whileHover={{ y: -4 }} onClick={() => onOpen(customer.id)}>
          <div className="customer-card-top"><div className="customer-avatar">{customer.first_name[0]}{customer.last_name?.[0] || ''}</div><button className="icon-button" onClick={(e) => e.stopPropagation()}><MoreHorizontal size={18} /></button></div>
          <h3>{customer.first_name} {customer.last_name}</h3><p>{customer.company || 'Independent customer'}</p>
          <div className="contact-lines">{customer.email && <span><Mail size={14} />{customer.email}</span>}{customer.phone && <span><Phone size={14} />{customer.phone}</span>}</div>
          <div className="tag-row">{(customer.tags || []).map((tag) => <span className="tag" key={tag.id}><Tag size={11} />{tag.name}</span>)}</div>
        </motion.article>
      ))}</div>}
    </section>
  );
}
