import { Suspense, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoadingIntro from "./components/LoadingIntro.jsx";
import MainLayout from "./layouts/MainLayout.jsx";
import Home from "./routes/Home.jsx";

export default function App() {
  const [showIntro, setShowIntro] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowIntro(false), 2600);
    return () => clearTimeout(timer);
  }, []);

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {showIntro && <LoadingIntro />}
      <MainLayout>
        <Suspense
          fallback={
            <div className="flex h-screen w-full items-center justify-center bg-black text-white">
              Loading experience...
            </div>
          }
        >
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </Suspense>
      </MainLayout>
    </BrowserRouter>
  );
}
