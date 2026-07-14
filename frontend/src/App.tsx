import { useCallback, useState } from "react";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import { Sidebar } from "./components/layout/Sidebar";
import { ErrorAlert } from "./components/ErrorAlert";
import { ExampleQuestions } from "./components/ExampleQuestions";
import { HeroSection } from "./components/HeroSection";
import { QuestionForm } from "./components/QuestionForm";
import { ResultsPanel } from "./components/ResultsPanel";
import { useTheme } from "./hooks/useTheme";
import { askQuestion } from "./services/api";
import type { ApiError, AskResponse } from "./types/api";

function App() {
  const { theme, toggleTheme } = useTheme();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponse | null>(null);

  const handleAsk = useCallback(async () => {
    const trimmed = question.trim();
    if (!trimmed || loading) {
      if (!trimmed) {
        setError("Please enter a question before asking.");
      }
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(trimmed);
      setResult(response);
    } catch (err) {
      const apiError = err as ApiError;
      setResult(null);
      setError(apiError.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  }, [question, loading]);

  return (
    <DashboardLayout
      sidebarCollapsed={sidebarCollapsed}
      sidebar={
        <Sidebar
          collapsed={sidebarCollapsed}
          theme={theme}
          onToggleCollapse={() => setSidebarCollapsed((value) => !value)}
          onToggleTheme={toggleTheme}
        />
      }
    >
      <HeroSection />

      <ExampleQuestions
        disabled={loading}
        onSelect={(example) => {
          setQuestion(example);
          setError(null);
        }}
      />

      <QuestionForm
        question={question}
        loading={loading}
        onQuestionChange={setQuestion}
        onSubmit={handleAsk}
      />

      {error && <ErrorAlert message={error} />}

      {result && <ResultsPanel result={result} />}
    </DashboardLayout>
  );
}

export default App;
