import { request } from "./client.js";

export function getReviewQueue({ status, priority } = {}) {
  return request("/reviews", { query: { status, priority } });
}

/** No GET /reviews/{id} endpoint exists in the canonical contract
 * (docs/26_API_Specification.md S24-S26 only documents the queue,
 * assign, and complete endpoints) -- a single case's full detail is
 * assembled by fetching the queue and finding the matching case, which
 * already carries every field a reviewer needs (docs/22 S23). */
export async function getReviewCase(reviewCaseId) {
  const queue = await getReviewQueue();
  return queue.cases.find((c) => c.review_case_id === reviewCaseId) ?? null;
}

export function assignReviewCase(reviewCaseId, reviewerId) {
  return request(`/reviews/${encodeURIComponent(reviewCaseId)}/assign`, {
    method: "POST",
    body: { reviewer_id: reviewerId },
  });
}

export function completeReviewCase(reviewCaseId, decision, comment) {
  return request(`/reviews/${encodeURIComponent(reviewCaseId)}/complete`, {
    method: "POST",
    body: { decision, comment },
  });
}
