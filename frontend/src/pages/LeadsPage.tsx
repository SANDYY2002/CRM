import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, DollarSign, MoreHorizontal, Plus, Target } from 'lucide-react';
import { api } from '../lib/api';

type Lead = { id: number; title: string; status: string; source?: string; value?: string | number; customer?: { first_name?: string; last_name?: string } };
const stages = [['new', 'New'], ['contacted', 'Contacted'], ['qualified', 'Qualified'], ['proposal', 'Proposal'], ['won', 'Won'], ['lost', 'Lost']];
const fallback: Lead[] = [
  { id: 1, title: 'Deluxe room inquiry', status: 'new', source: 'Instagram', value: 4500, customer: { first_name: 'Maya', last_name: 'Gurung' } },
  { id: 2, title: 'Corporate package', status: 'contacted', source: 'Facebook', value: 18500, customer: { first_name: 'Ram', last_name: 'Chhetri' } },
  { id: 3, title: 'Annual service plan', status: 'qualified', source: 'WhatsApp', value: 32000, customer: { first_name: 'Sita', last_name: 'Sharma' } },
  { id: 4, title: 'Premium package', status: 'proposal', source: 'Viber', value: 56000, customer: { first_name: 'Hari', last_name: 'Thapa' } },
];

export function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  useEffect(() => { api.leads().then(data => setLeads(data as Lead[])).catch(() => setLeads(fallback)); }, []);
  const data = leads.length ? leads : fallback;
  return <section className="page-view">
    <div className="page-heading"><div><p className="eyebrow">SALES PIPELINE</p><h1>Leads</h1><p className="muted">Move prospects forward and never lose an opportunity.</p></div><button className="primary-button"><Plus size={17}/> New lead</button></div>
    <div className="pipeline-summary glass-card"><div><Target size={18}/><strong>{data.length}</strong><span>active opportunities</span></div><div><DollarSign size={18}/><strong>NPR {data.reduce((sum, lead) => sum + Number(lead.value || 0), 0).toLocaleString()}</strong><span>pipeline value</span></div></div>
    <div className="pipeline">{stages.map(([key, label]) => { const items = data.filter(lead => lead.status === key); return <div className="pipeline-column" key={key}><div className="pipeline-heading"><span>{label}</span><b>{items.length}</b><button className="icon-button"><Plus size={15}/></button></div><div className="lead-stack">{items.map((lead, index) => <motion.article key={lead.id} className="lead-card glass-card" layout initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} transition={{delay:index*.04}} whileHover={{y:-3}}><div className="lead-top"><span className="source-pill">{lead.source || 'Direct'}</span><button className="icon-button"><MoreHorizontal size={15}/></button></div><h3>{lead.title}</h3><div className="lead-customer"><span className="mini-avatar">{lead.customer?.first_name?.[0] || 'L'}</span><span>{lead.customer?.first_name} {lead.customer?.last_name}</span></div><div className="lead-footer"><strong>NPR {Number(lead.value || 0).toLocaleString()}</strong><ChevronRight size={15}/></div></motion.article>)}</div></div>; })}</div>
  </section>;
}
