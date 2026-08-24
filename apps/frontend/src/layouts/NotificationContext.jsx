import { createContext, useCallback, useContext, useMemo, useState } from "react";

const NotificationContext = createContext(null);
let counter = 0;

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const dismiss = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const notify = useCallback(
    (message, type = "info", timeoutMs = 5000) => {
      const id = ++counter;
      setNotifications((prev) => [...prev, { id, message, type }]);
      if (timeoutMs) setTimeout(() => dismiss(id), timeoutMs);
      return id;
    },
    [dismiss],
  );

  const value = useMemo(() => ({ notifications, notify, dismiss }), [notifications, notify, dismiss]);
  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error("useNotifications must be used within a NotificationProvider");
  return ctx;
}
