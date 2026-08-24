import { Card } from "../common/Card.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatPercent, titleCase } from "../../utils/format.js";

export function ExtractedFieldsPanel({ ocr, extraction }) {
  if (!ocr) {
    return (
      <Card title="OCR / Extraction">
        <EmptyState title="Not run yet" message="OCR has not been run for this cheque." />
      </Card>
    );
  }

  const fields = extraction?.fields ?? {};
  const fieldNames = Object.keys(fields);

  return (
    <Card
      title="OCR / Extraction"
      subtitle={`Engine ${ocr.engine_name ?? "—"} ${ocr.engine_version ?? ""} · Confidence ${formatPercent(ocr.average_confidence)}`}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">OCR Status</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(ocr.ocr_status)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Extraction Status</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(extraction?.extraction_status)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Template</p>
          <p className="text-sm font-medium text-slate-900">{extraction?.template ?? "—"}</p>
        </div>
      </div>

      {(extraction?.missing_fields?.length > 0 || extraction?.ambiguous_fields?.length > 0) && (
        <div className="mt-3 space-y-1 text-xs">
          {extraction.missing_fields.length > 0 && (
            <p className="text-red-600">Missing fields: {extraction.missing_fields.join(", ")}</p>
          )}
          {extraction.ambiguous_fields.length > 0 && (
            <p className="text-amber-600">Ambiguous fields: {extraction.ambiguous_fields.join(", ")}</p>
          )}
        </div>
      )}

      {fieldNames.length > 0 ? (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-500">
                <th className="py-2 pr-4">Field</th>
                <th className="py-2 pr-4">Normalized Value</th>
                <th className="py-2 pr-4">Raw (OCR) Value</th>
                <th className="py-2 pr-4">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {fieldNames.map((name) => {
                const f = fields[name];
                return (
                  <tr key={name}>
                    <td className="py-2 pr-4 font-medium text-slate-700">{titleCase(name)}</td>
                    <td className="py-2 pr-4 text-slate-900">{f.value ?? <span className="text-slate-400">Not detected</span>}</td>
                    <td className="py-2 pr-4 text-slate-500">{f.raw_value ?? "—"}</td>
                    <td className="py-2 pr-4 text-slate-500">{formatPercent(f.confidence)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">No field-level extraction data available.</p>
      )}
    </Card>
  );
}
