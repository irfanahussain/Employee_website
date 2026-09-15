import { useEffect, useState } from "react";
import { createDepartment, getDepartments, updateDepartment } from "../../api.js";

const EMPTY_FORM = { name: "", description: "" };

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [status, setStatus] = useState("loading");
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  function loadDepartments() {
    setStatus("loading");
    getDepartments()
      .then((data) => {
        setDepartments(data.results || data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }

  useEffect(loadDepartments, []);

  function startEdit(dept) {
    setEditingId(dept.id);
    setForm({ name: dept.name, description: dept.description || "" });
  }

  function resetForm() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (editingId) {
        await updateDepartment(editingId, form);
      } else {
        await createDepartment(form);
      }
      resetForm();
      loadDepartments();
    } catch (err) {
      setError(err?.message || "Couldn't save department.");
    }
  }

  async function toggleActive(dept) {
    await updateDepartment(dept.id, { is_active: !dept.is_active });
    loadDepartments();
  }

  return (
    <>
      <div className="student__page-header">
        <h1 className="student__page-title">Departments</h1>
      </div>

      <form className="form form--narrow" onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
        {error && <p className="form__banner form__banner--error">{error}</p>}
        <div>
          <label htmlFor="dept-name">Department Name</label>
          <input
            id="dept-name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
        </div>
        <div>
          <label htmlFor="dept-desc">Description</label>
          <textarea
            id="dept-desc"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </div>
        <div className="form__row--split">
          <button type="submit" className="button button--primary">
            {editingId ? "Save Changes" : "Add Department"}
          </button>
          {editingId && (
            <button type="button" className="button button--ghost" onClick={resetForm}>
              Cancel
            </button>
          )}
        </div>
      </form>

      {status === "loading" && <p className="state-message">Loading departments…</p>}
      {status === "error" && (
        <p className="state-message state-message--error">Couldn't load departments.</p>
      )}

      {status === "ready" && (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Teams</th>
              <th>Employees</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept) => (
              <tr key={dept.id}>
                <td>{dept.name}</td>
                <td>{dept.team_count}</td>
                <td>{dept.employee_count}</td>
                <td>
                  <span className={`status-pill status-pill--${dept.is_active ? "active" : "inactive"}`}>
                    {dept.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="admin-table__actions">
                  <button type="button" onClick={() => startEdit(dept)}>
                    Edit
                  </button>
                  <button type="button" onClick={() => toggleActive(dept)}>
                    {dept.is_active ? "Deactivate" : "Activate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
