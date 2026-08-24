import { EmptyState } from "../common/States.jsx";
import { formatDate, titleCase } from "../../utils/format.js";

export function AuditTimeline({ events }) {
  if (!events || events.length === 0) {
    return <EmptyState title="No audit events" message="No audit events have been recorded yet." />;
  }

  const sorted = [...events].sort((a, b) => new Date(b.event_timestamp) - new Date(a.event_timestamp));

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead>
          <tr className="text-left text-xs uppercase text-slate-500">
            <th className="py-2 pr-4">Time</th>
            <th className="py-2 pr-4">Event</th>
            <th className="py-2 pr-4">Source</th>
            <th className="py-2 pr-4">Actor</th>
            <th className="py-2 pr-4">Result</th>
            <th className="py-2 pr-4">Reason</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {sorted.map((event) => (
            <tr key={event.audit_id}>
              <td className="py-2 pr-4 whitespace-nowrap text-slate-500">{formatDate(event.event_timestamp)}</td>
              <td className="py-2 pr-4 font-medium text-slate-800">{titleCase(event.event_type)}</td>
              <td className="py-2 pr-4 text-slate-600">{event.source}</td>
              <td className="py-2 pr-4 text-slate-600">
                {event.user_id ? `${event.user_id} (${event.user_role ?? "—"})` : "System"}
              </td>
              <td className="py-2 pr-4 text-slate-600">{event.result ?? "—"}</td>
              <td className="py-2 pr-4 text-slate-500">{event.reason ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-xs text-slate-400">
        Audit events are append-only and cannot be edited or deleted from this interface.
      </p>
    </div>
  );
}
