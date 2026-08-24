import { useState } from "react";
import examples from "../data/qaExamples.json";

function findAnswer(question) {
  const normalized = question.trim().toLowerCase();
  const exact = examples.find((e) => e.question.toLowerCase() === normalized);
  if (exact) return exact.answer;

  const words = normalized.split(/\s+/).filter((w) => w.length > 3);
  let best = null;
  let bestScore = 0;
  examples.forEach((e) => {
    const eWords = e.question.toLowerCase().split(/\s+/);
    const score = words.filter((w) => eWords.some((ew) => ew.includes(w))).length;
    if (score > bestScore) {
      bestScore = score;
      best = e;
    }
  });
  return bestScore >= 2 ? best.answer : null;
}

function QaAgent() {
  const [input, setInput] = useState("");
  const [thread, setThread] = useState([]);

  const submit = (question) => {
    if (!question.trim()) return;
    const answer = findAnswer(question);
    setThread((prev) => [
      ...prev,
      {
        question,
        answer:
          answer ||
          "This demo runs in offline mode with a fixed set of example questions. The underlying agent (pipeline/qa_agent.py) calls the Claude API directly and can answer open-ended questions once connected to a live key.",
      },
    ]);
    setInput("");
  };

  return (
    <div className="card">
      <div className="qa-suggestions">
        {examples.map((e) => (
          <button key={e.question} className="qa-suggestion" onClick={() => submit(e.question)}>
            {e.question}
          </button>
        ))}
      </div>

      <div className="qa-thread">
        {thread.length === 0 && (
          <div className="qtd-label" style={{ padding: "8px 0" }}>
            Ask a question above, or type your own below.
          </div>
        )}
        {thread.map((t, i) => (
          <div className="qa-turn" key={i}>
            <div className="qa-question">{t.question}</div>
            <div className="qa-answer">{t.answer}</div>
          </div>
        ))}
      </div>

      <form
        className="qa-input-row"
        onSubmit={(e) => {
          e.preventDefault();
          submit(input);
        }}
      >
        <input
          type="text"
          placeholder="Ask about variance, forecast, or pipeline..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Ask</button>
      </form>
    </div>
  );
}

export default QaAgent;
