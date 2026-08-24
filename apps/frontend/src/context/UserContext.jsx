import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { setRequestUserContext } from "../api/client.js";
import { getCurrentUser } from "../api/users.js";

const STORAGE_KEY = "mm_dev_role_context";
const UserContext = createContext(null);

function loadStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function UserProvider({ children }) {
  const [context, setContext] = useState(() => loadStored());
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    setRequestUserContext(context ?? { role: null, userId: null });
    if (!context) {
      setProfile(null);
      return;
    }
    let cancelled = false;
    getCurrentUser()
      .then((data) => {
        if (!cancelled) setProfile(data);
      })
      .catch(() => {
        if (!cancelled) setProfile(null);
      });
    return () => {
      cancelled = true;
    };
  }, [context]);

  const selectRole = useCallback((role, userId) => {
    const next = { role, userId: userId || null };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    setContext(next);
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setContext(null);
    setProfile(null);
  }, []);

  const value = useMemo(
    () => ({ role: context?.role ?? null, userId: context?.userId ?? null, profile, selectRole, signOut }),
    [context, profile, selectRole, signOut],
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
}
