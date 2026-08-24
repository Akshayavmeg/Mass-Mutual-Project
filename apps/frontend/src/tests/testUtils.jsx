import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { UserProvider } from "../context/UserContext.jsx";
import { NotificationProvider } from "../layouts/NotificationContext.jsx";

export function renderWithProviders(ui, { route = "/", path } = {}) {
  const content = path ? (
    <Routes>
      <Route path={path} element={ui} />
    </Routes>
  ) : (
    ui
  );
  return render(
    <MemoryRouter initialEntries={[route]}>
      <NotificationProvider>
        <UserProvider>{content}</UserProvider>
      </NotificationProvider>
    </MemoryRouter>,
  );
}
