import { request } from "./client.js";

export function getCurrentUser() {
  return request("/users/me");
}
