import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import { PublicOnly, RequireAuth } from "./auth/guards";
import { AppLayout } from "./components/layout/AppLayout";
import { isClientError } from "./lib/errors";
import { JobDetailPage } from "./pages/JobDetailPage";
import { JobsPage } from "./pages/JobsPage";
import { LoginPage } from "./pages/LoginPage";
import { NewJobPage } from "./pages/NewJobPage";
import { NewResumePage } from "./pages/NewResumePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResumeDetailPage } from "./pages/ResumeDetailPage";
import { ResumesPage } from "./pages/ResumesPage";
import { SettingsPage } from "./pages/SettingsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => !isClientError(error) && failureCount < 2,
      refetchOnWindowFocus: false,
    },
  },
});

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ScrollToTop />
          <Routes>
            <Route element={<PublicOnly />}>
              <Route path="entrar" element={<LoginPage />} />
              <Route path="criar-conta" element={<RegisterPage />} />
            </Route>

            <Route element={<RequireAuth />}>
              <Route element={<AppLayout />}>
                <Route index element={<Navigate to="/curriculos" replace />} />
                <Route path="curriculos" element={<ResumesPage />} />
                <Route path="curriculos/novo" element={<NewResumePage />} />
                <Route path="curriculos/:resumeId" element={<ResumeDetailPage />} />
                <Route path="vagas" element={<JobsPage />} />
                <Route path="vagas/nova" element={<NewJobPage />} />
                <Route path="vagas/:jobId" element={<JobDetailPage />} />
                <Route path="configuracoes" element={<SettingsPage />} />
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
