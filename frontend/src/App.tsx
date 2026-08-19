import { motion } from 'framer-motion';
import { Bell, ChevronDown, CircleHelp, Inbox, LayoutDashboard, MessageCircle, Search, Settings2, Users, UserRoundPlus, Zap } from 'lucide-react';

const stats = [
  { label: 'Total conversations', value: '1,248', change: '+12.8%', icon: MessageCircle },
  { label: 'New leads', value: '86', change: '+8.4%', icon: UserRoundPlus },
  { label: 'Customers', value: '2,914', change: '+5.2%', icon: Users },
  { label: 'Avg. response', value: '3m 42s', change: '-18.3%', icon: Zap },
];

const activity = [
  ['WhatsApp', 'Ram asked about a booking', '2 min ago'],
  ['Instagram', 'New lead from @maya.studio', '8 min ago'],
  ['Facebook', 'Sita replied to your campaign', '16 min ago'],
  ['Viber', 'Hari sent a new message', '31 min ago'],
];

function App() {
  return (
    <main className="app-shell">
      <div className="orb orb-one" />
      <div className="orb orb-two" />
      <aside className="sidebar glass-panel">
        <div className="brand"><span className="brand-mark">C</span><span>CRM</span></div>
        <div className="workspace"><div className="workspace-avatar">A</div><div><strong>Acme Workspace</strong><small>Business workspace</small></div><ChevronDown size={15} /></div>
        <nav>
          <a className="active"><LayoutDashboard size={18} />Dashboard</a>
          <a><Inbox size={18} />Unified Inbox<span className="badge">12</span></a>
          <a><Users size={18} />Customers</a>
          <a><UserRoundPlus size={18} />Leads</a>
          <a><MessageCircle size={18} />Campaigns</a>
          <a><Zap size={18} />Automation</a>
          <a><Settings2 size={18} />Settings</a>
        </nav>
        <div className="sidebar-bottom"><CircleHelp size={17} /><span>Help center</span></div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div className="search"><Search size={18} /><input placeholder="Search customers, conversations..." /><kbd>⌘ K</kbd></div>
          <div className="top-actions"><button className="icon-button"><Bell size={19} /><i /></button><div className="profile"><div className="avatar">SC</div><div><strong>Sandesh</strong><small>Administrator</small></div></div></div>
        </header>

        <div className="page-heading"><div><p className="eyebrow">WEDNESDAY, AUGUST 19</p><h1>Good evening, Sandesh <span>👋</span></h1><p className="muted">Here's what's happening across your customer channels today.</p></div><button className="primary-button">+ New customer</button></div>

        <div className="stats-grid">
          {stats.map(({ label, value, change, icon: Icon }, index) => <motion.div key={label} className="stat-card glass-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .06 }}><div className="stat-top"><div className="stat-icon"><Icon size={19} /></div><span className="trend">{change}</span></div><strong>{value}</strong><span>{label}</span></motion.div>)}
        </div>

        <div className="dashboard-grid">
          <section className="glass-card chart-card"><div className="card-heading"><div><h2>Conversation volume</h2><p>Messages received across all channels</p></div><button className="select">Last 7 days <ChevronDown size={14} /></button></div><div className="chart"><div className="grid-line one"/><div className="grid-line two"/><div className="grid-line three"/><svg viewBox="0 0 720 240" preserveAspectRatio="none"><defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#8b5cf6" stopOpacity=".28"/><stop offset="1" stopColor="#8b5cf6" stopOpacity="0"/></linearGradient></defs><path d="M0 190 C55 176 78 145 126 158 S205 115 252 130 S330 83 370 112 S445 98 492 70 S565 96 608 53 S680 76 720 35 L720 240 L0 240Z" fill="url(#fill)"/><path d="M0 190 C55 176 78 145 126 158 S205 115 252 130 S330 83 370 112 S445 98 492 70 S565 96 608 53 S680 76 720 35" fill="none" stroke="currentColor" strokeWidth="3" /></svg><div className="x-axis"><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span></div></div></section>

          <section className="glass-card activity-card"><div className="card-heading"><div><h2>Live activity</h2><p>Recent customer interactions</p></div><span className="live"><i /> Live</span></div><div className="activity-list">{activity.map(([channel, text, time]) => <div className="activity" key={text}><div className={`channel-dot ${channel.toLowerCase()}`}>{channel[0]}</div><div><strong>{text}</strong><span>{channel} · {time}</span></div></div>)}</div><button className="ghost-button">View all activity</button></section>
        </div>
      </section>
    </main>
  );
}

export default App;
