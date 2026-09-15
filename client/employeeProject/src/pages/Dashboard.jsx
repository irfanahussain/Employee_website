import { useEffect, useState } from "react";
import { getAdminDashboard } from "../../api.js";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let cancelled = false;
    getAdminDashboard()
      .then((data) => {
        if (!cancelled) {
          setStats(data);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "loading") return <p className="state-message">Loading dashboard…</p>;
  if (status === "error")
    return <p className="state-message state-message--error">Couldn't load dashboard stats.</p>;

  return (
    <>
      <div className="student__header">
        <p className="eyebrow">Admin</p>
        <h1>Dashboard</h1>
      </div>

      <div className="student__stats">
        <div className="student__stat-card">
          <span className="student__stat-value">{stats.total_employees}</span>
          <p className="student__stat-label">Total Employees</p>
        </div>
        <div className="student__stat-card">
          <span className="student__stat-value">{stats.active_employees}</span>
          <p className="student__stat-label">Active Employees</p>
        </div>
      </div>

      <h2 className="student__section-title">Department-wise Count</h2>
      <div className="student__stats">
        {stats.department_wise_count.map((row) => (
          <div className="student__stat-card" key={row.department__name}>
            <span className="student__stat-value">{row.count}</span>
            <p className="student__stat-label">{row.department__name || "Unassigned"}</p>
          </div>
        ))}
      </div>
    </>
  );
}
