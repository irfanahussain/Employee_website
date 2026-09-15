import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../AuthContext.jsx";

const NAV = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/employees", label: "Employees", end: false },
  { to: "/admin/departments", label: "Departments", end: false },
  { to: "/admin/teams", label: "Teams", end: false },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const role = user?.employee?.role;
  if (role !== "admin" && role !== "hr") {
    // Route guard: Team Leads / Employees never reach the admin module.
    navigate("/dashboard");
    return null;
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <section className="student">
      <header className="student__topbar">
        <button
          type="button"
          className="student__hamburger"
          aria-label="Open menu"
          onClick={() => setDrawerOpen(true)}
        >
          <span />
          <span />
          <span />
        </button>
        <span className="student__brand">Admin</span>
      </header>

      {drawerOpen && (
        <div className="student__drawer-backdrop" onClick={() => setDrawerOpen(false)} />
      )}

      <aside className={"student__drawer" + (drawerOpen ? " student__drawer--open" : "")}>
        <button
          type="button"
          className="student__drawer-close"
          aria-label="Close menu"
          onClick={() => setDrawerOpen(false)}
        >
          ×
        </button>

        <div className="student__identity">
          <span className="student__avatar" aria-hidden="true">
            {(user?.full_name || "A").charAt(0).toUpperCase()}
          </span>
          <div>
            <p className="student__name">{user?.full_name}</p>
            <p className="student__email">{user?.email}</p>
          </div>
        </div>

        <nav className="student__nav">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => setDrawerOpen(false)}
              className={({ isActive }) =>
                "student__nav-link" + (isActive ? " student__nav-link--active" : "")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button type="button" className="student__logout" onClick={handleLogout}>
          Log out
        </button>
      </aside>

      <div className="student__main">
        <div className="student__content">
          <Outlet />
        </div>
      </div>
    </section>
  );
}
