import { Card } from "../common/Card.jsx";
import { StatusBadge, SeverityBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { titleCase } from "../../utils/format.js";

export function ValidationPanel({ validation }) {
  if (!validation) {
    return (
      <Card title="Validation">
        <EmptyState title="Not run yet" message="Validation has not been run for this cheque." />
      </Card>
    );
  }

  const checks = Object.values(validation.checks ?? {});

  return (
    <Card
      title="Validation"
      action={<StatusBadge status={validation.overall_validation_status} />}
      subtitle={validation.validation_message}
    >
      {checks.length === 0 ? (
        <p className="text-sm text-slate-500">No individual checks reported.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-500">
                <th className="py-2 pr-4">Check</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Severity</th>
                <th className="py-2 pr-4">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {checks.map((check) => (
                <tr key={check.check}>
                  <td className="py-2 pr-4 font-medium text-slate-700">{titleCase(check.check)}</td>
                  <td className="py-2 pr-4">
                    <StatusBadge status={check.status} />
                  </td>
                  <td className="py-2 pr-4">
                    <SeverityBadge severity={check.severity} />
                  </td>
                  <td className="py-2 pr-4 text-slate-600">
                    {check.status === "NOT_CHECKED" ? (
                      <span className="italic text-slate-500">{check.message}</span>
                    ) : (
                      check.message
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {validation.not_checked?.length > 0 && (
        <p className="mt-3 text-xs italic text-slate-500">
          Not checked (unavailable data — never treated as a pass): {validation.not_checked.join(", ")}
        </p>
      )}
    </Card>
  );
}
