import { useState, useEffect, useRef } from "react";

// ─── DATA ────────────────────────────────────────────────────────────────────
const AGENTS = [
  { id: "allisson", name: "Allisson", role: "CEO", color: "#D4AF37", icon: "👑", description: "Empire Orchestrator" },
  { id: "hannah",   name: "Hannah",   role: "Social Media", color: "#FF6B9D", icon: "📱", description: "Twitter · LinkedIn · Facebook" },
  { id: "lucy",     name: "Lucy",     role: "Research",     color: "#7DD3FC", icon: "🔍", description: "Web Research · Reports" },
  { id: "mike",     name: "Mike",     role: "Finance",      color: "#86EFAC", icon: "📈", description: "Investments · Markets" },
  { id: "joseph",   name: "Joseph",   role: "Health",       color: "#FCA5A5", icon: "💪", description: "Fitness · Nutrition" },
  { id: "melvin",   name: "Melvin",   role: "Freelancing",  color: "#C4B5FD", icon: "💼", description: "Gigs · Content · Ecommerce" },
  { id: "steve",    name: "Steve",    role: "Monitor",      color: "#FDE68A", icon: "📊", description: "Performance · Quality" },
];

const TOPICS = ["AI & Tech", "Finance", "Health", "Business", "Content", "Research"];

const MOCK_PROJECTS = {
  learning: [
    { id: 1, title: "LLM Fine-tuning Fundamentals", topic: "AI & Tech", agent: "lucy", progress: 65 },
    { id: 2, title: "Options Trading Strategies", topic: "Finance", agent: "mike", progress: 40 },
    { id: 3, title: "Nutrition & Macro Cycling", topic: "Health", agent: "joseph", progress: 80 },
  ],
  building: [
    { id: 4, title: "Allisson Empire UI", topic: "AI & Tech", agent: "allisson", progress: 30 },
    { id: 5, title: "Freelance Portfolio Site", topic: "Business", agent: "melvin", progress: 55 },
    { id: 6, title: "Twitter Growth System", topic: "Content", agent: "hannah", progress: 20 },
  ],
};

const MOCK_LIVE_TASKS = [
  { id: 1, title: "Analyzing AI trends for weekly report", agent: "lucy", topic: "AI & Tech", status: "running", time: "2m ago" },
  { id: 2, title: "Drafting LinkedIn post on productivity", agent: "hannah", topic: "Content", status: "running", time: "5m ago" },
  { id: 3, title: "Checking BTC/ETH portfolio balance", agent: "mike", topic: "Finance", status: "queued", time: "pending" },
  { id: 4, title: "Generating weekly workout plan", agent: "joseph", topic: "Health", status: "done", time: "12m ago" },
  { id: 5, title: "Scanning Upwork for dev gigs", agent: "melvin", topic: "Business", status: "running", time: "1m ago" },
];

const MOCK_AGENT_RESULTS = {
  hannah: { completed: 14, ongoing: 3, tasks: ["Posted 3 tweets about AI trends", "LinkedIn article on productivity", "Engaged 22 Twitter replies"], lastActive: "5m ago" },
  lucy:   { completed: 8,  ongoing: 1, tasks: ["Research report on LLM market", "Fact-checked 5 articles", "Web scrape: top AI tools"], lastActive: "2m ago" },
  mike:   { completed: 5,  ongoing: 2, tasks: ["Portfolio rebalancing analysis", "BTC price alert system", "Stock screener run"], lastActive: "15m ago" },
  joseph: { completed: 11, ongoing: 1, tasks: ["30-day workout plan", "Meal prep calendar", "Calorie tracking setup"], lastActive: "12m ago" },
  melvin: { completed: 7,  ongoing: 2, tasks: ["Found 8 Upwork gigs", "Wrote 3 proposals", "Fiverr profile optimization"], lastActive: "1m ago" },
  steve:  { completed: 20, ongoing: 0, tasks: ["Weekly performance review", "API cost optimization", "Error rate analysis"], lastActive: "1h ago" },
};

// ─── TYPING ANIMATION ────────────────────────────────────────────────────────
const statusBrief = `Empire Status: All 6 sub-agents are operational. Hannah posted 3 pieces of content today. Lucy completed a market research report. Mike flagged a portfolio rebalancing opportunity. Melvin found 8 new freelance gigs. Joseph generated your weekly workout plan. Steve reports a 94% task success rate. No critical issues detected. Ready for new commands.`;

function useTypingEffect(text, speed = 28) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  useEffect(() => {
    setDisplayed("");
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        setDone(true);
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text]);
  return { displayed, done };
}

// ─── ALLISSON AVATAR ──────────────────────────────────────────────────────────
function AllissonAvatar({ speaking }) {
  return (
    <div style={{ position: "relative", width: 80, height: 80 }}>
      {/* Pulse rings */}
      {speaking && [0, 1, 2].map(i => (
        <div key={i} style={{
          position: "absolute", inset: 0, borderRadius: "50%",
          border: "2px solid #D4AF37",
          animation: `pulse-ring 2s ease-out ${i * 0.6}s infinite`,
          opacity: 0,
        }} />
      ))}
      <div style={{
        width: 80, height: 80, borderRadius: "50%",
        background: "linear-gradient(135deg, #1a1200 0%, #3d2b00 50%, #1a1200 100%)",
        border: "2px solid #D4AF37",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 32, position: "relative", zIndex: 1,
        boxShadow: speaking ? "0 0 24px #D4AF3766" : "0 0 12px #D4AF3733",
        transition: "box-shadow 0.3s",
      }}>
        👑
      </div>
    </div>
  );
}

// ─── NEW PROJECT MODAL ────────────────────────────────────────────────────────
function NewProjectModal({ onClose }) {
  const [form, setForm] = useState({ agent: "", objective: "", context: "", guidelines: "" });
  const update = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async () => {
    try {
      const response = await fetch("/api/projects/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const result = await response.json();
      console.log("Project created:", result);
      onClose();
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  return (
    <ModalOverlay onClose={onClose}>
      <h2 style={styles.modalTitle}>✦ New Project</h2>
      <p style={styles.modalSub}>Define a new empire project and assign it to a sub-agent.</p>

      <label style={styles.label}>Sub-Agent</label>
      <select style={styles.select} value={form.agent} onChange={update("agent")}>
        <option value="">— Select Agent —</option>
        {AGENTS.filter(a => a.id !== "allisson").map(a => (
          <option key={a.id} value={a.id}>{a.icon} {a.name} · {a.role}</option>
        ))}
      </select>

      <label style={styles.label}>Objective</label>
      <input style={styles.input} placeholder="What's the main goal?" value={form.objective} onChange={update("objective")} />

      <label style={styles.label}>Context</label>
      <textarea style={{ ...styles.input, height: 80, resize: "vertical" }} placeholder="Background info, links, current situation..." value={form.context} onChange={update("context")} />

      <label style={styles.label}>Guidelines & Instructions</label>
      <textarea style={{ ...styles.input, height: 80, resize: "vertical" }} placeholder="Tone, format preferences, constraints..." value={form.guidelines} onChange={update("guidelines")} />

      <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
        <button style={styles.btnGold} onClick={handleSubmit}>Launch Project ✦</button>
        <button style={styles.btnGhost} onClick={onClose}>Cancel</button>
      </div>
    </ModalOverlay>
  );
}

// ─── ADD TASK MODAL ───────────────────────────────────────────────────────────
function AddTaskModal({ onClose }) {
  const [form, setForm] = useState({ agent: "", task: "", priority: "medium" });
  const update = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async () => {
    try {
      const response = await fetch("/api/execute/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: `${form.task} (priority: ${form.priority})` }),
      });
      const result = await response.json();
      console.log("Task dispatched:", result);
      onClose();
    } catch (error) {
      console.error("Error dispatching task:", error);
    }
  };

  return (
    <ModalOverlay onClose={onClose}>
      <h2 style={styles.modalTitle}>⚡ Add Task</h2>
      <p style={styles.modalSub}>Fire off a quick task to any sub-agent.</p>

      <label style={styles.label}>Assign to Agent</label>
      <select style={styles.select} value={form.agent} onChange={update("agent")}>
        <option value="">— Select Agent —</option>
        {AGENTS.filter(a => a.id !== "allisson").map(a => (
          <option key={a.id} value={a.id}>{a.icon} {a.name}</option>
        ))}
      </select>

      <label style={styles.label}>Task Description</label>
      <textarea style={{ ...styles.input, height: 100, resize: "vertical" }} placeholder="Describe exactly what you need done..." value={form.task} onChange={update("task")} />

      <label style={styles.label}>Priority</label>
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {["low", "medium", "high", "urgent"].map(p => (
          <button key={p} onClick={() => setForm(f => ({ ...f, priority: p }))} style={{
            flex: 1, padding: "8px 0", borderRadius: 8, border: "1px solid",
            borderColor: form.priority === p ? "#D4AF37" : "#333",
            background: form.priority === p ? "#D4AF3722" : "transparent",
            color: form.priority === p ? "#D4AF37" : "#666",
            cursor: "pointer", fontSize: 12, textTransform: "capitalize", fontFamily: "inherit"
          }}>{p}</button>
        ))}
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <button style={styles.btnGold} onClick={handleSubmit}>Dispatch Task ⚡</button>
        <button style={styles.btnGhost} onClick={onClose}>Cancel</button>
      </div>
    </ModalOverlay>
  );
}

// ─── AGENT RESULTS MODAL ─────────────────────────────────────────────────────
function AgentResultsModal({ agent, onClose }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/api/agents/stats/")
      .then(r => r.json())
      .then(result => {
        const agentData = result.agents?.[agent.name.toLowerCase()];
        if (agentData) {
          setData({
            completed: agentData.completed,
            ongoing: agentData.ongoing,
            failed: agentData.failed,
            tasks: [],
            lastActive: "recently"
          });
        }
      })
      .catch(() => {
        // Fallback to mock data if API fails
        setData(MOCK_AGENT_RESULTS[agent.id]);
      });
  }, [agent]);

  if (!data) return null;

  return (
    <ModalOverlay onClose={onClose}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
        <div style={{ width: 56, height: 56, borderRadius: "50%", background: `${agent.color}22`, border: `2px solid ${agent.color}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24 }}>
          {agent.icon}
        </div>
        <div>
          <h2 style={{ ...styles.modalTitle, margin: 0 }}>{agent.name}</h2>
          <p style={{ color: agent.color, margin: 0, fontSize: 13 }}>{agent.role} · Last active {data.lastActive}</p>
        </div>
      </div>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={styles.statBox}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#86EFAC" }}>{data.completed}</div>
          <div style={{ fontSize: 12, color: "#666" }}>Completed</div>
        </div>
        <div style={styles.statBox}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#FDE68A" }}>{data.ongoing}</div>
          <div style={{ fontSize: 12, color: "#666" }}>Ongoing</div>
        </div>
      </div>

      <p style={{ color: "#888", fontSize: 12, marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.1em" }}>Recent Activity</p>
      {(data.tasks && data.tasks.length > 0) ? data.tasks.map((t, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "1px solid #1a1a1a" }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: agent.color, flexShrink: 0 }} />
          <span style={{ color: "#ccc", fontSize: 14 }}>{t}</span>
        </div>
      )) : (
        <p style={{ color: "#555", fontSize: 13 }}>No recent activity</p>
      )}

      <button style={{ ...styles.btnGhost, marginTop: 24, width: "100%" }} onClick={onClose}>Close</button>
    </ModalOverlay>
  );
}

// ─── MODAL OVERLAY ────────────────────────────────────────────────────────────
function ModalOverlay({ children, onClose }) {
  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)",
      backdropFilter: "blur(8px)", zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#0d0d0d", border: "1px solid #2a2a2a", borderRadius: 20,
        padding: 32, width: "100%", maxWidth: 520, maxHeight: "85vh", overflowY: "auto",
        boxShadow: "0 0 80px rgba(212,175,55,0.15)",
      }}>
        {children}
      </div>
    </div>
  );
}

// ─── LEFT SIDEBAR ─────────────────────────────────────────────────────────────
function LeftSidebar() {
  const [open, setOpen] = useState({ learning: true, building: true });
  const toggle = k => setOpen(o => ({ ...o, [k]: !o[k] }));

  return (
    <div style={styles.sidebar}>
      <div style={styles.sidebarHeader}>
        <span style={styles.sidebarTitle}>Projects</span>
        <span style={{ color: "#D4AF37", fontSize: 18 }}>◈</span>
      </div>

      {/* Learning */}
      <div style={{ marginBottom: 16 }}>
        <div style={styles.sectionRow} onClick={() => toggle("learning")}>
          <span style={{ color: "#7DD3FC", fontSize: 13, fontWeight: 600 }}>📚 Learning</span>
          <span style={{ color: "#555", transition: "transform 0.2s", display: "inline-block", transform: open.learning ? "rotate(180deg)" : "rotate(0deg)" }}>▾</span>
        </div>
        {open.learning && MOCK_PROJECTS.learning.map(p => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>

      {/* Building */}
      <div>
        <div style={styles.sectionRow} onClick={() => toggle("building")}>
          <span style={{ color: "#C4B5FD", fontSize: 13, fontWeight: 600 }}>🔨 Building</span>
          <span style={{ color: "#555", transition: "transform 0.2s", display: "inline-block", transform: open.building ? "rotate(180deg)" : "rotate(0deg)" }}>▾</span>
        </div>
        {open.building && MOCK_PROJECTS.building.map(p => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>
    </div>
  );
}

function ProjectCard({ project }) {
  const agent = AGENTS.find(a => a.id === project.agent);
  return (
    <div style={styles.projectCard}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
        <span style={{ color: "#ddd", fontSize: 12, lineHeight: 1.4, flex: 1 }}>{project.title}</span>
        <span style={{ fontSize: 14, marginLeft: 6 }}>{agent?.icon}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ flex: 1, height: 3, background: "#1a1a1a", borderRadius: 2 }}>
          <div style={{ width: `${project.progress}%`, height: "100%", background: agent?.color || "#D4AF37", borderRadius: 2 }} />
        </div>
        <span style={{ color: "#555", fontSize: 10 }}>{project.progress}%</span>
      </div>
      <div style={{ marginTop: 4 }}>
        <span style={{ color: "#444", fontSize: 10 }}>{project.topic}</span>
      </div>
    </div>
  );
}

// ─── RIGHT SIDEBAR ────────────────────────────────────────────────────────────
function RightSidebar() {
  const [liveTasks, setLiveTasks] = useState(MOCK_LIVE_TASKS);

  useEffect(() => {
    // Initial load
    fetch("/api/tasks/?status=executing&limit=20")
      .then(r => r.json())
      .then(data => {
        if (data.tasks && data.tasks.length > 0) {
          setLiveTasks(data.tasks.map(t => ({
            id: t.id,
            title: t.command,
            agent: t.agent_name?.toLowerCase() || "allisson",
            topic: "Tasks",
            status: t.status === "executing" ? "running" : t.status,
            time: t.created_at
          })));
        }
      })
      .catch(() => {
        // Keep using mock data if API fails
      });

    // WebSocket for real-time updates
    let ws;
    const connectWebSocket = () => {
      ws = new WebSocket("ws://" + window.location.host + "/ws/tasks/");
      
      ws.onopen = () => {
        console.log("WebSocket connected");
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "task_update") {
          setLiveTasks(prev => {
            const exists = prev.find(t => t.id === data.task.id);
            if (exists) {
              return prev.map(t => t.id === data.task.id ? { ...t, ...data.task } : t);
            }
            return [data.task, ...prev].slice(0, 20);
          });
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected, reconnecting...");
        setTimeout(connectWebSocket, 3000);
      };
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const grouped = TOPICS.reduce((acc, t) => {
    const tasks = liveTasks.filter(lt => lt.topic === t);
    if (tasks.length) acc[t] = tasks;
    return acc;
  }, {});

  return (
    <div style={styles.sidebar}>
      <div style={styles.sidebarHeader}>
        <span style={styles.sidebarTitle}>Live Tasks</span>
        <span style={{ color: "#FF6B6B", fontSize: 10, animation: "blink 1.5s infinite" }}>● LIVE</span>
      </div>

      {Object.keys(grouped).length > 0 ? (
        Object.entries(grouped).map(([topic, tasks]) => (
          <div key={topic} style={{ marginBottom: 18 }}>
            <div style={{ color: "#555", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.12em", marginBottom: 8 }}>{topic}</div>
            {tasks.map(task => <LiveTaskCard key={task.id} task={task} />)}
          </div>
        ))
      ) : (
        <div style={{ marginBottom: 18 }}>
          <div style={{ color: "#555", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.12em", marginBottom: 8 }}>Tasks</div>
          {liveTasks.map(task => <LiveTaskCard key={task.id} task={task} />)}
        </div>
      )}
    </div>
  );
}

function LiveTaskCard({ task }) {
  const agent = AGENTS.find(a => a.id === task.agent);
  const statusColor = { running: "#86EFAC", queued: "#FDE68A", done: "#444" }[task.status];
  const statusLabel = { running: "Running", queued: "Queued", done: "Done" }[task.status];

  return (
    <div style={styles.taskCard}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 14 }}>{agent?.icon}</span>
        <span style={{ fontSize: 10, color: statusColor, display: "flex", alignItems: "center", gap: 4 }}>
          {task.status === "running" && <span style={{ animation: "blink 1.2s infinite" }}>●</span>}
          {statusLabel}
        </span>
      </div>
      <div style={{ color: "#bbb", fontSize: 11, lineHeight: 1.4 }}>{task.title}</div>
      <div style={{ color: "#444", fontSize: 10, marginTop: 4 }}>{task.time}</div>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function AllissonEmpire() {
  const [modal, setModal] = useState(null); // null | "project" | "task" | agent
  const [statusText, setStatusText] = useState("Loading empire status...");

  useEffect(() => {
    fetch("/api/status/")
      .then(r => r.json())
      .then(data => {
        const msg = data?.result?.message || data?.result?.statistics
          ? `Total tasks: ${data.result.statistics?.total_tasks || 0}. Completed: ${data.result.statistics?.completed || 0}.`
          : "All systems operational.";
        setStatusText(msg);
      })
      .catch(() => setStatusText("Unable to reach empire systems."));
  }, []);

  const { displayed, done } = useTypingEffect(statusText);

  return (
    <>
      {/* Global styles */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #080808; }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 4px; }

        @keyframes pulse-ring {
          0%   { transform: scale(1); opacity: 0.8; }
          100% { transform: scale(2.2); opacity: 0; }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0; }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50%       { transform: translateY(-6px); }
        }
        @keyframes shimmer {
          0%   { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .agent-chip:hover {
          transform: translateY(-4px) scale(1.03) !important;
          box-shadow: 0 12px 40px rgba(0,0,0,0.6) !important;
        }
        .action-btn:hover {
          transform: scale(1.05) !important;
          filter: brightness(1.1) !important;
        }
      `}</style>

      {/* Layout wrapper */}
      <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "#080808", fontFamily: "'DM Sans', sans-serif", color: "#e0e0e0" }}>

        {/* LEFT SIDEBAR */}
        <LeftSidebar />

        {/* MAIN CONTENT */}
        <main style={{ flex: 1, overflowY: "auto", padding: "40px 32px" }}>

          {/* ── HEADER ── */}
          <div style={{ textAlign: "center", marginBottom: 32, animation: "fadeIn 0.8s ease" }}>
            <div style={{ display: "inline-block", marginBottom: 12 }}>
              <div style={{
                fontSize: 11, letterSpacing: "0.25em", color: "#D4AF37", textTransform: "uppercase",
                fontFamily: "'DM Mono', monospace", marginBottom: 8,
              }}>✦ Command Interface ✦</div>
              <h1 style={{
                fontFamily: "'Cinzel', serif", fontSize: "clamp(22px, 3vw, 36px)",
                fontWeight: 700, lineHeight: 1.15,
                background: "linear-gradient(135deg, #D4AF37 0%, #F5E27A 40%, #D4AF37 60%, #B8860B 100%)",
                backgroundSize: "200% auto",
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                animation: "shimmer 4s linear infinite",
              }}>Allisson Superpowered AI Assistant</h1>
              <p style={{ color: "#666", fontSize: 14, marginTop: 8, letterSpacing: "0.08em" }}>
                In-charge of an Empire of Sub-agents
              </p>
            </div>
          </div>

          {/* ── STATUS BRIEF ── */}
          <div style={{
            maxWidth: 680, margin: "0 auto 36px",
            background: "linear-gradient(135deg, #0f0f0f, #111)",
            border: "1px solid #1e1e1e", borderRadius: 16, padding: "20px 24px",
            boxShadow: "inset 0 1px 0 #2a2a2a, 0 4px 24px rgba(0,0,0,0.4)",
            animation: "fadeIn 1s ease 0.3s both",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#D4AF37", animation: "blink 2s infinite" }} />
              <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.15em" }}>Empire Status Brief</span>
            </div>
            <p style={{
              fontFamily: "'DM Mono', monospace", fontSize: 12, color: "#aaa", lineHeight: 1.7,
              minHeight: 80,
            }}>
              {displayed}
              {!done && <span style={{ animation: "blink 0.8s infinite", color: "#D4AF37" }}>█</span>}
            </p>
          </div>

          {/* ── ALLISSON AVATAR + BUTTONS ── */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "center",
            gap: 32, marginBottom: 48, animation: "fadeIn 1s ease 0.6s both",
          }}>
            {/* New Project btn */}
            <button className="action-btn" onClick={() => setModal("project")} style={{
              background: "transparent", border: "1px solid #2a2a2a", borderRadius: 12,
              padding: "14px 24px", color: "#aaa", cursor: "pointer", fontFamily: "'DM Sans', sans-serif",
              fontSize: 13, display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
              transition: "all 0.2s",
            }}>
              <span style={{ fontSize: 22 }}>◈</span>
              <span>New Project</span>
            </button>

            {/* Allisson Avatar */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <div style={{ animation: "float 4s ease-in-out infinite" }}>
                <AllissonAvatar speaking={!done} />
              </div>
              <span style={{
                fontFamily: "'DM Mono', monospace", fontSize: 10, color: "#D4AF37",
                letterSpacing: "0.1em", textTransform: "uppercase",
              }}>● Allisson</span>
            </div>

            {/* Add Task btn */}
            <button className="action-btn" onClick={() => setModal("task")} style={{
              background: "transparent", border: "1px solid #2a2a2a", borderRadius: 12,
              padding: "14px 24px", color: "#aaa", cursor: "pointer", fontFamily: "'DM Sans', sans-serif",
              fontSize: 13, display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
              transition: "all 0.2s",
            }}>
              <span style={{ fontSize: 22 }}>⚡</span>
              <span>Add Task</span>
            </button>
          </div>

          {/* ── AGENT RESULTS ── */}
          <div style={{ marginBottom: 40, animation: "fadeIn 1s ease 0.9s both" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
              <div style={{ flex: 1, height: 1, background: "linear-gradient(90deg, transparent, #222)" }} />
              <span style={{ color: "#555", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.15em", fontFamily: "'DM Mono', monospace" }}>Agent Results</span>
              <div style={{ flex: 1, height: 1, background: "linear-gradient(90deg, #222, transparent)" }} />
            </div>

            <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center" }}>
              {AGENTS.filter(a => a.id !== "allisson").map((agent, i) => (
                <div key={agent.id} className="agent-chip"
                  onClick={() => setModal({ type: "agent", agent })}
                  style={{
                    background: `linear-gradient(135deg, #0f0f0f, #111)`,
                    border: `1px solid ${agent.color}33`,
                    borderRadius: 14, padding: "16px 20px", cursor: "pointer",
                    transition: "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
                    animation: `fadeIn 0.6s ease ${0.1 * i}s both`,
                    minWidth: 130, textAlign: "center",
                    boxShadow: `0 0 24px ${agent.color}11`,
                    position: "relative", overflow: "hidden",
                  }}>
                  {/* Top accent line */}
                  <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${agent.color}, transparent)` }} />

                  <div style={{ fontSize: 26, marginBottom: 8 }}>{agent.icon}</div>
                  <div style={{ color: "#fff", fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{agent.name}</div>
                  <div style={{ color: agent.color, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>{agent.role}</div>

                  <div style={{ display: "flex", justifyContent: "center", gap: 10 }}>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ color: "#86EFAC", fontSize: 14, fontWeight: 700 }}>{MOCK_AGENT_RESULTS[agent.id]?.completed}</div>
                      <div style={{ color: "#444", fontSize: 9 }}>done</div>
                    </div>
                    <div style={{ width: 1, background: "#1a1a1a" }} />
                    <div style={{ textAlign: "center" }}>
                      <div style={{ color: "#FDE68A", fontSize: 14, fontWeight: 700 }}>{MOCK_AGENT_RESULTS[agent.id]?.ongoing}</div>
                      <div style={{ color: "#444", fontSize: 9 }}>active</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </main>

        {/* RIGHT SIDEBAR */}
        <RightSidebar />
      </div>

      {/* MODALS */}
      {modal === "project" && <NewProjectModal onClose={() => setModal(null)} />}
      {modal === "task"    && <AddTaskModal    onClose={() => setModal(null)} />}
      {modal?.type === "agent" && (
        <AgentResultsModal agent={modal.agent} onClose={() => setModal(null)} />
      )}
    </>
  );
}

// ─── SHARED STYLES ────────────────────────────────────────────────────────────
const styles = {
  sidebar: {
    width: 240, minWidth: 240, height: "100vh", overflowY: "auto",
    background: "#090909", borderRight: "1px solid #141414",
    padding: "32px 16px", flexShrink: 0,
  },
  sidebarHeader: {
    display: "flex", justifyContent: "space-between", alignItems: "center",
    marginBottom: 20, paddingBottom: 14, borderBottom: "1px solid #141414",
  },
  sidebarTitle: {
    fontFamily: "'Cinzel', serif", fontSize: 13, color: "#D4AF37", letterSpacing: "0.1em",
  },
  sectionRow: {
    display: "flex", justifyContent: "space-between", alignItems: "center",
    cursor: "pointer", marginBottom: 8, padding: "6px 0",
  },
  projectCard: {
    background: "#0d0d0d", border: "1px solid #1a1a1a", borderRadius: 10,
    padding: "10px 12px", marginBottom: 8, cursor: "pointer",
    transition: "border-color 0.2s",
  },
  taskCard: {
    background: "#0d0d0d", border: "1px solid #1a1a1a", borderRadius: 10,
    padding: "10px 12px", marginBottom: 8,
  },
  modalTitle: {
    fontFamily: "'Cinzel', serif", fontSize: 20, color: "#D4AF37", marginBottom: 6,
  },
  modalSub: {
    color: "#555", fontSize: 13, marginBottom: 24,
  },
  label: {
    display: "block", color: "#666", fontSize: 11, textTransform: "uppercase",
    letterSpacing: "0.1em", marginBottom: 8, marginTop: 16,
    fontFamily: "'DM Mono', monospace",
  },
  input: {
    width: "100%", background: "#111", border: "1px solid #222", borderRadius: 10,
    padding: "12px 14px", color: "#ddd", fontSize: 13, fontFamily: "'DM Sans', sans-serif",
    outline: "none",
  },
  select: {
    width: "100%", background: "#111", border: "1px solid #222", borderRadius: 10,
    padding: "12px 14px", color: "#ddd", fontSize: 13, fontFamily: "'DM Sans', sans-serif",
    outline: "none", cursor: "pointer",
  },
  btnGold: {
    flex: 1, background: "linear-gradient(135deg, #D4AF37, #B8860B)", border: "none",
    borderRadius: 10, padding: "14px 20px", color: "#000", fontWeight: 700,
    fontSize: 13, cursor: "pointer", fontFamily: "'DM Sans', sans-serif",
  },
  btnGhost: {
    background: "transparent", border: "1px solid #2a2a2a", borderRadius: 10,
    padding: "14px 20px", color: "#555", cursor: "pointer", fontSize: 13,
    fontFamily: "'DM Sans', sans-serif",
  },
  statBox: {
    flex: 1, background: "#111", border: "1px solid #1a1a1a", borderRadius: 12,
    padding: "16px", textAlign: "center",
  },
};
