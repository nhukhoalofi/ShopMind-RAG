const questions = [
  "How long does shipping take?",
  "What payment methods are accepted?",
  "Can I cancel my order?",
  "What happens if I receive a damaged product?",
  "I forgot my account password. What should I do?",
  "Do you have a physical store in Japan?",
];

export function ExampleQuestions({
  onSelect,
  disabled,
}: {
  onSelect: (question: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
      {questions.map((question) => (
        <button
          key={question}
          type="button"
          onClick={() => onSelect(question)}
          disabled={disabled}
          className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-left text-sm text-slate-600 transition hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50"
        >
          {question}
        </button>
      ))}
    </div>
  );
}
