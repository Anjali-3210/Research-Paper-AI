import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import "./App.css"

function App() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
  if (!question.trim()) {
    return
  }

  setLoading(true)
  setAnswer("")

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/ask?question=${encodeURIComponent(question)}`
    )

    const data = await response.json()

    if (data.success) {
      setAnswer(data.answer)
    } else {
      setAnswer(data.error)
    }
  } catch (error) {
    console.error("API Error:", error)
    setAnswer("Unable to connect to the backend.")
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="app">
  <header className="header">
    <h1>Research Paper AI</h1>
    <p>Ask questions and get answers directly from your research paper.</p>
  </header>

  <main className="main">
    <div className="question-section">
      <input
        type="text"
        placeholder="Ask a question about the paper..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleAsk()
          }
        }}
      />

      <div className="button-group">
        <button
          onClick={handleAsk}
          disabled={loading || !question.trim()}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>

        <button
          onClick={() => {
            setQuestion("")
            setAnswer("")
          }}
          disabled={loading}
        >
          Clear
        </button>
      </div>
    </div>

    {loading && (
      <div className="loading">
        <p>Analyzing the research paper...</p>
      </div>
    )}

    {answer && (
      <div className="answer">
        <h2>Answer</h2>

        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {answer}
        </ReactMarkdown>
      </div>
    )}
  </main>
</div>
  )
}

export default App