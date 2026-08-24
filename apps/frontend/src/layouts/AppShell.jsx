import { NavLink, Outlet } from "react-router-dom";
import { useUser } from "../context/UserContext.jsx";
import { PERMISSION, ROLE_LABELS, roleHasPermission } from "../utils/constants.js";
import { useNotifications } from "./NotificationContext.jsx";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true, permission: PERMISSION.CHEQUE_VIEW },
  { to: "/upload", label: "Upload Cheque", permission: PERMISSION.CHEQUE_UPLOAD },
  { to: "/cheques", label: "Cheques / History", permission: PERMISSION.CHEQUE_VIEW },
  { to: "/reviews", label: "Review Queue", permission: PERMISSION.REVIEW_VIEW },
  { to: "/audit", label: "Audit", permission: PERMISSION.AUDIT_VIEW },
  { to: "/status", label: "System Status", permission: null },
];

function NavItem({ to, label, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `block rounded-md px-3 py-2 text-sm font-medium transition ${
          isActive ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

function NotificationTray() {
  const { notifications, dismiss } = useNotifications();
  if (notifications.length === 0) return null;
  return (
    <div className="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2" data-testid="notification-tray">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`rounded-md border px-4 py-3 text-sm shadow-lg ${
            n.type === "error"
              ? "border-red-200 bg-red-50 text-red-800"
              : n.type === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                : "border-slate-200 bg-white text-slate-700"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <span>{n.message}</span>
            <button
              type="button"
              onClick={() => dismiss(n.id)}
              className="text-xs text-slate-400 hover:text-slate-600"
              aria-label="Dismiss notification"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function AppShell() {
  const { role, profile, signOut } = useUser();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <NotificationTray />
      <aside className="hidden w-56 shrink-0 border-r border-slate-200 bg-white md:block">
        <div className="px-4 py-5">
          <p className="text-sm font-semibold text-slate-900">Mass Mutual</p>
          <p className="text-xs text-slate-500">Cheque Fraud Detection</p>
        </div>
        <nav className="space-y-1 px-3">
          {NAV_ITEMS.filter((item) => !item.permission || roleHasPermission(role, item.permission)).map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:px-6">
          <div className="md:hidden">
            <p className="text-sm font-semibold text-slate-900">Mass Mutual</p>
          </div>
          <div className="ml-auto flex items-center gap-4">
            <div className="text-right text-xs text-slate-500">
              <p className="font-medium text-slate-700">{profile?.username ?? "Unknown user"}</p>
              <p>{ROLE_LABELS[role] ?? role ?? "No role selected"} · Development Mode</p>
            </div>
            <button
              type="button"
              onClick={signOut}
              className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
            >
              Switch role
            </button>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export { NAV_ITEMS };
