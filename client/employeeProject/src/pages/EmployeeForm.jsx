import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createEmployee,
  getDepartments,
  getEmployee,
  getTeams,
  updateEmployee,
} from "../../api.js";

const EMPTY_FORM = {
  employee_id: "",
  full_name: "",
  email: "",
  phone: "",
  date_of_joining: "",
  department: "",
  team: "",
  designation: "",
  role: "employee",
  status: "active",
};

export default function EmployeeForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [departments, setDepartments] = useState([]);
  const [teams, setTeams] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getDepartments().then((data) => setDepartments(data.results || data));
  }, []);

  useEffect(() => {
    if (form.department) {
      getTeams({ department: form.department }).then((data) =>
        setTeams(data.results || data)
      );
    } else {
      setTeams([]);
    }
  }, [form.department]);

  useEffect(() => {
    if (isEdit) {
      getEmployee(id).then((emp) =>
        setForm({
          employee_id: emp.employee_id,
          full_name: emp.full_name,
          email: emp.email,
          phone: emp.phone || "",
          date_of_joining: emp.date_of_joining,
          department: emp.department,
          team: emp.team || "",
          designation: emp.designation,
          role: emp.role,
          status: emp.status,
        })
      );
    }
  }, [id, isEdit]);

  function handleChange(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const payload = { ...form, team: form.team || null };
      if (isEdit) {
        await updateEmployee(id, payload);
      } else {
        await createEmployee(payload);
      }
      navigate("/admin/employees");
    } catch (err) {
      setError(err?.message || "Couldn't save employee. Check the fields and try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <div className="student__page-header">
        <h1 className="student__page-title">{isEdit ? "Edit Employee" : "Add Employee"}</h1>
      </div>

      <form className="form form--wide" onSubmit={handleSubmit}>
        {error && <p className="form__banner form__banner--error">{error}</p>}

        <div className="form__row--split">
          <div>
            <label htmlFor="employee_id">Employee ID</label>
            <input
              id="employee_id"
              value={form.employee_id}
              onChange={handleChange("employee_id")}
              required
              disabled={isEdit}
            />
          </div>
          <div>
            <label htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              value={form.full_name}
              onChange={handleChange("full_name")}
              required
            />
          </div>
        </div>

        <div className="form__row--split">
          <div>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={form.email}
              onChange={handleChange("email")}
              required
            />
          </div>
          <div>
            <label htmlFor="phone">Phone</label>
            <input id="phone" value={form.phone} onChange={handleChange("phone")} />
          </div>
        </div>

        <div className="form__row--split">
          <div>
            <label htmlFor="date_of_joining">Date of Joining</label>
            <input
              id="date_of_joining"
              type="date"
              value={form.date_of_joining}
              onChange={handleChange("date_of_joining")}
              required
            />
          </div>
          <div>
            <label htmlFor="designation">Designation</label>
            <input
              id="designation"
              value={form.designation}
              onChange={handleChange("designation")}
              required
            />
          </div>
        </div>

        <div className="form__row--split">
          <div>
            <label htmlFor="department">Department</label>
            <select
              id="department"
              value={form.department}
              onChange={handleChange("department")}
              required
            >
              <option value="">Select department</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="team">Team</label>
            <select id="team" value={form.team} onChange={handleChange("team")}>
              <option value="">No team</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form__row--split">
          <div>
            <label htmlFor="role">Role</label>
            <select id="role" value={form.role} onChange={handleChange("role")}>
              <option value="employee">Employee</option>
              <option value="team_lead">Team Lead</option>
              <option value="hr">HR</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div>
            <label htmlFor="status">Status</label>
            <select id="status" value={form.status} onChange={handleChange("status")}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <div className="form__row--split">
          <button type="submit" className="button button--primary" disabled={saving}>
            {saving ? "Saving…" : isEdit ? "Save Changes" : "Add Employee"}
          </button>
          <button
            type="button"
            className="button button--ghost"
            onClick={() => navigate("/admin/employees")}
          >
            Cancel
          </button>
        </div>
      </form>
    </>
  );
}
