import { useState } from "react";
import { imageUrl } from "../../api/client.js";
import { Card } from "../common/Card.jsx";

function ImageSlot({ chequeId, variant, label }) {
  const [failed, setFailed] = useState(false);
  if (failed) {
    return (
      <div className="flex h-48 items-center justify-center rounded-md border border-dashed border-slate-300 bg-slate-50 text-xs text-slate-400">
        {label} image not available
      </div>
    );
  }
  return (
    <img
      src={imageUrl(chequeId, variant)}
      alt={`${label} cheque`}
      className="h-48 w-full rounded-md border border-slate-200 object-contain bg-slate-50"
      onError={() => setFailed(true)}
    />
  );
}

export function ChequeImages({ chequeId }) {
  return (
    <Card title="Cheque Images">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-1 text-xs font-medium text-slate-500">Original</p>
          <ImageSlot chequeId={chequeId} variant="original" label="Original" />
        </div>
        <div>
          <p className="mb-1 text-xs font-medium text-slate-500">Processed</p>
          <ImageSlot chequeId={chequeId} variant="processed" label="Processed" />
        </div>
      </div>
    </Card>
  );
}
