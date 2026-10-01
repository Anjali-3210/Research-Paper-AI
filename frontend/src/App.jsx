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
  const [history, setHistory] = useState([])

  const [paper, setPaper] = useState(null)

  const [comparisonMode, setComparisonMode] = useState(false)
  const [paper1, setPaper1] = useState("paper1")
  const [paper2, setPaper2] = useState("paper2")

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    fetch("https://research-paper-ai-wp3m.onrender.com/paper")
      .then((response) => response.json())
      .then((data) => {
        setPaper(data)
      })
      .catch(() => {
        setPaper(null)
      })
  }, [])

  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.")
      return
    }

    if (comparisonMode && paper1 === paper2) {
      setError("Please select two different papers.")
      return
    }

    setLoading(true)
    setError("")

    try {
      const endpoint = comparisonMode
      ? "https://research-paper-ai-wp3m.onrender.com/compare"
      : "https://research-paper-ai-wp3m.onrender.com/ask"

      const requestBody = comparisonMode
        ? {
            question: question,
            paper1_id: paper1,
            paper2_id: paper2,
          }
        : {
            question: question,
            history: history,
          }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      const data = await response.json()

      if (data.success) {
        setAnswer(data.answer)
        setSources(data.sources || [])
        setError("")

        if (!comparisonMode) {
          setHistory((prev) => [
            ...prev,
            {
              question: question,
              answer: data.answer,
              sources: data.sources || [],
            },
          ])
        }
      } else {
        setAnswer("")
        setSources([])
        setError(data.error || "Unable to process the question.")
      }
    } catch (error) {
      console.error(error)

      setAnswer("")
      setSources([])
      setError("Unable to connect to the backend.")
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setQuestion("")
    setAnswer("")
    setSources([])
    setHistory([])
    setError("")
  }

  const handleHistoryClick = (item) => {
    setQuestion(item.question)
    setAnswer(item.answer)
    setSources(item.sources || [])
    setError("")
  }

  const getPaperTitle = (paperId) => {
    if (paperId === "paper1") {
      return "Attention Is All You Need"
    }

    if (paperId === "paper2") {
      return "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
    }

    return paperId
  }

  return (
    <div className="app">
      <div className="container">

        {/* Header */}
        <header className="header">
          <h1>Research Paper AI</h1>

          <p>
            Ask questions about research papers using Retrieval-Augmented
            Generation.
          </p>
        </header>

        {/* Single Paper Information */}
        {paper && !comparisonMode && (
          <div className="paper-card">
            <h2>{paper.title}</h2>

            <p>
              <strong>Authors:</strong>{" "}
              {paper.authors?.join(", ")}
            </p>

            <p>
              <strong>Pages:</strong> {paper.pages}
            </p>

            <span className="status">
              ● {paper.status}
            </span>
          </div>
        )}

        {/* Mode Switch */}
        <div className="mode-switch">

          <button
            className={
              !comparisonMode
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() => {
              setComparisonMode(false)
              setAnswer("")
              setSources([])
              setError("")
            }}
          >
            Single Paper
          </button>

          <button
            className={
              comparisonMode
                ? "mode-button active"
                : "mode-button"
            }
            onClick={() => {
              setComparisonMode(true)
              setAnswer("")
              setSources([])
              setError("")
            }}
          >
            Compare Papers
          </button>

        </div>

        {/* Comparison Paper Selection */}
        {comparisonMode && (
          <div className="comparison-card">

            <h2>Compare Research Papers</h2>

            <div className="paper-selectors">

              <div className="paper-selector">

                <label htmlFor="paper1">
                  Paper 1
                </label>

                <select
                  id="paper1"
                  value={paper1}
                  onChange={(event) =>
                    setPaper1(event.target.value)
                  }
                >
                  <option value="paper1">
                    Attention Is All You Need
                  </option>

                  <option value="paper2">
                    BERT: Pre-training of Deep Bidirectional Transformers
                  </option>
                </select>

              </div>

              <div className="paper-selector">

                <label htmlFor="paper2">
                  Paper 2
                </label>

                <select
                  id="paper2"
                  value={paper2}
                  onChange={(event) =>
                    setPaper2(event.target.value)
                  }
                >
                  <option value="paper1">
                    Attention Is All You Need
                  </option>

                  <option value="paper2">
                    BERT: Pre-training of Deep Bidirectional Transformers
                  </option>
                </select>

              </div>

            </div>

            <div className="selected-papers">

              <div>
                <strong>Paper 1:</strong>

                <span>
                  {getPaperTitle(paper1)}
                </span>
              </div>

              <div>
                <strong>Paper 2:</strong>

                <span>
                  {getPaperTitle(paper2)}
                </span>
              </div>

            </div>

          </div>
        )}

        {/* Question Section */}
        <div
          className="question-section"
          style={{
            width: "100%",
            boxSizing: "border-box",
            padding: "28px",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >

          <textarea
            value={question}
            onChange={(event) => {
              setQuestion(event.target.value)

              if (error) {
                setError("")
              }
            }}
            placeholder={
              comparisonMode
                ? "Ask a question comparing the two papers..."
                : "Ask a question about the research paper..."
            }
            rows={6}
            style={{
              width: "100%",
              minHeight: "150px",
              boxSizing: "border-box",
              padding: "18px",
              borderRadius: "10px",
              border: "1px solid #333",
              background: "#171717",
              color: "#ffffff",
              fontSize: "16px",
              lineHeight: "1.5",
              resize: "vertical",
              outline: "none",
              fontFamily: "inherit",
            }}
          />

          <div
            className="button-row"
            style={{
              display: "flex",
              gap: "10px",
              alignItems: "center",
            }}
          >

            <button
              className="ask-button"
              onClick={askQuestion}
              disabled={loading}
            >
              {loading
                ? "Thinking..."
                : comparisonMode
                  ? "Compare Papers"
                  : "Ask Question"}
            </button>

            <button
              className="clear-button"
              onClick={clearChat}
              disabled={loading}
            >
              Clear
            </button>

          </div>

        </div>

        {/* Error */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Answer */}
        {answer && (
          <>

            <div className="answer">

              <h2>
                {comparisonMode
                  ? "Comparison Result"
                  : "Answer"}
              </h2>

              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {answer}
              </ReactMarkdown>

            </div>

            {/* Sources */}
            {sources.length > 0 && (
              <div className="sources">

                <h2>Sources</h2>

                {sources.map((source, index) => (
                  <div
                    className="source-item"
                    key={index}
                  >

                    <strong>
                      📄{" "}

                      {comparisonMode && source.paper_id
                        ? `${getPaperTitle(source.paper_id)} — `
                        : ""}

                      Page {source.page}
                    </strong>

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

        {/* Question History */}
        {!comparisonMode && history.length > 0 && (
          <div className="history">

            <h2>Question History</h2>

            {history.map((item, index) => (
              <div
                className="history-item"
                key={index}
                onClick={() => handleHistoryClick(item)}
              >

                <strong>
                  {item.question}
                </strong>

                <p>
                  {item.answer.length > 180
                    ? `${item.answer.slice(0, 180)}...`
                    : item.answer}
                </p>

              </div>
            ))}

          </div>
        )}

      </div>
    </div>
  )
}

export default App