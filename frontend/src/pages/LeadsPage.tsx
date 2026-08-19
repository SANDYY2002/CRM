import { useEffect, useState } from 'react';
import { ChevronRight, DollarSign, MoreHorizontal, Plus, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';

type Lead = { id: number; title: string; status: string; source?: string; value?: string | number; customer_name?: string };
const stages = [['new', 'New'], ['contacted', 'Contacted'], ['qualified', 'Qualified'], ['proposal', 'Proposal'], ['won', 'Won'], ['lost', 'Lost']];

export function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.leads().then((data) => setLeads(data as Lead[])).catch((err: Error) => setError(err.message)).finally(() => setLoading(false));
  }, []);

  const pipelineValue = leads.reduce((sum, lead) => sum + Number(lead.value || 0), 0);

  return <section className="page-view">
    <div className="page-heading"><div><p className="eyebrow">SALES PIPELINE</p><h1>Leads</h1><p className="muted">Real opportunities from your CRM database.</p></div><button className="primary-button"><Plus size={17} /> New lead</button></div>
    <div className="pipeline-summary glass-card"><div><Target size={18} /><strong>{leads.length}</strong><span>opportunities</span></div><div><DollarSign size={18} /><strong>NPR {pipelineValue.toLocaleString()}</strong><span>pipeline value</span></div></div>
    {loading && <div className="empty-state glass-card"><span className="loading-orb small" /><strong>Loading leads…</strong><p>Fetching the live pipeline from Django.</p></div>}
    {!loading && error && <div className="empty-state glass-card"><strong>Couldn't load leads</strong><p>{error}</p></div>}
    {!loading && !error && leads.length === 0 && <div className="empty-state glass-card"><Target size={28} /><strong>No leads yet</strong><p>Create a lead to start tracking your sales pipeline.</p></div>}
    {!loading && !error && leads.length > 0 && <div className="pipeline">{stages.map(([key, label]) => { const items = leads.filter((lead) => lead.status === key); return <div className="pipeline-column" key={key}><div className="pipeline-heading"><span>{label}</span><b>{items.length}</b><button className="icon-button"><Plus size={15} /></button></div><div className="lead-stack">{items.map((lead, index) => <motion.article key={lead.id} className="lead-card glass-card" layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .04 }} whileHover={{ y: -3 }}><div className="lead-top"><span className="source-pill">{lead.source || 'Direct'}</span><button className="icon-button"><MoreHorizontal size={15} /></button></div><h3>{lead.title}</h3><div className="lead-customer"><span className="mini-avatar">{lead.customer_name?.[0] || '?'}</span><span>{lead.customer_name || 'Customer'}</span></div><div className="lead-footer"><strong>NPR {Number(lead.value || 0).toLocaleString()}</strong><ChevronRight size={15} /></div></motion.article>)}</div></div>; })}</div>}
  </section>;
}
