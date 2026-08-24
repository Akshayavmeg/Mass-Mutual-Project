import { BrowserRouter, Route, Routes } from "react-router-dom";
import { UserProvider, useUser } from "./context/UserContext.jsx";
import AppShell from "./layouts/AppShell.jsx";
import { NotificationProvider } from "./layouts/NotificationContext.jsx";
import AuditPage from "./pages/AuditPage.jsx";
import ChequeDetailPage from "./pages/ChequeDetailPage.jsx";
import ChequeHistoryPage from "./pages/ChequeHistoryPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";
import ReviewDetailPage from "./pages/ReviewDetailPage.jsx";
import ReviewQueuePage from "./pages/ReviewQueuePage.jsx";
import RoleSelectPage from "./pages/RoleSelectPage.jsx";
import SystemStatusPage from "./pages/SystemStatusPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";

function RootRoutes() {
  const { role } = useUser();

  if (!role) return <RoleSelectPage />;

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/cheques" element={<ChequeHistoryPage />} />
        <Route path="/cheques/:chequeId" element={<ChequeDetailPage />} />
        <Route path="/reviews" element={<ReviewQueuePage />} />
        <Route path="/reviews/:reviewCaseId" element={<ReviewDetailPage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/audit/:chequeId" element={<AuditPage />} />
        <Route path="/status" element={<SystemStatusPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <NotificationProvider>
        <UserProvider>
          <RootRoutes />
        </UserProvider>
      </NotificationProvider>
    </BrowserRouter>
  );
}
