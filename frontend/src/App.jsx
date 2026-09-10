import { useEffect, useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import "./App.css"

function App() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)

  const [paper, setPaper] = useState(null)
  const [paperLoading, setPaperLoading] = useState(true)
  const [paperError, setPaperError] = useState("")
  const [history, setHistory] = useState([])

  useEffect(() => {
    const fetchPaper = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/paper")

        if (!response.ok) {
          throw new Error("Failed to fetch paper information")
        }

        const data = await response.json()
        setPaper(data)
      } catch (error) {
        console.error("Paper API Error:", error)
        setPaperError("Unable to load paper information.")
      } finally {
        setPaperLoading(false)
      }
    }

    fetchPaper()
  }, [])

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
        setSources(data.sources)

        setHistory((prev) => [
            ...prev,
            {
              question: question,
              answer: data.answer,
            },
          ])
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
        <p>
          Ask questions and get answers directly from your research paper.
        </p>
      </header>

      <main className="main">

        {paperError && (
          <div className="paper-error">
            {paperError}
          </div>
        )}

        {paperLoading && (
          <div className="paper-card">
            <p>Loading paper information...</p>
          </div>
        )}

        {paper && !paperLoading && (
          <div className="paper-card">
            <div>
              <h2>{paper.title}</h2>

              <p>{paper.authors.join(", ")}</p>

              <div className="paper-meta">
                <span>{paper.pages} pages</span>

                <span className="status-badge">
                  ● {paper.status === "ready" ? "Ready" : "Unavailable"}
                </span>
              </div>
            </div>
          </div>
        )}

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
                setSources([])
                setHistory([])
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
            <>
              <div className="answer">
                <h2>Answer</h2>

                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {answer}
                </ReactMarkdown>
              </div>

              {sources.length > 0 && (
                <div className="sources">
                  <h2>Sources</h2>

                  {sources.map((source, index) => (
                    <div className="source-item" key={index}>
                      <strong>📄 Page {source.page}</strong>
                      <p>
                        {source.content.length > 300
                          ? `${source.content.slice(0, 300)}...`
                          : source.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

        {history.length > 0 && (
          <div className="history">
            <h2>Question History ({history.length})</h2>

            {history.map((item, index) => (
              <div
                className="history-item"
                key={index}
                onClick={() => {
                  setQuestion(item.question)
                  setAnswer(item.answer)
                }}
              >
                <h3>{item.question}</h3>

                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {item.answer}
                </ReactMarkdown>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  )
}

export default App