import { useState } from "react";
import { useUser } from "../context/UserContext.jsx";
import { ROLES, ROLE_LABELS } from "../utils/constants.js";

const ROLE_DESCRIPTIONS = {
  ADMINISTRATOR: "Views dashboards, review queue, and audit logs.",
  OPERATOR: "Uploads cheques and runs processing.",
  REVIEWER: "Works the manual review queue and approves/rejects flagged cheques.",
  AUDITOR: "Read-only access to cheques and the audit trail.",
  SYSTEM_SERVICE: "Automated/service account used by the processing pipeline itself.",
};

export default function RoleSelectPage() {
  const { selectRole } = useUser();
  const [role, setRole] = useState("OPERATOR");
  const [userId, setUserId] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    selectRole(role, userId.trim() || undefined);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-slate-900">Mass Mutual Cheque Fraud Detection System</h1>
        <p className="mt-1 text-sm text-slate-500">Select a role to continue</p>
        <div className="mt-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Development Mode: this stands in for real sign-in until a JWT authentication milestone is built. It
          sets the <code>X-User-Role</code> header the backend uses to enforce access control server-side.
        </div>

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-slate-700">
              Role
            </label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABELS[r]}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-slate-500">{ROLE_DESCRIPTIONS[role]}</p>
          </div>

          <div>
            <label htmlFor="userId" className="block text-sm font-medium text-slate-700">
              User ID <span className="text-slate-400">(optional)</span>
            </label>
            <input
              id="userId"
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="e.g. USR-002"
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}
