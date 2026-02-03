import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { AppLayout } from '../components/layout';

type MessageRole = 'user' | 'assistant';

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

export function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your health assistant. Ask me about your check-ins, symptoms, or care plan. RAG integration coming soon.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    // Mock reply (replace with RAG later)
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: "This is a placeholder reply. Connect your RAG pipeline to get answers from health records and guidelines.",
          timestamp: new Date(),
        },
      ]);
    }, 600);
  };

  return (
    <AppLayout
      role={user?.role ?? 'patient'}
      email={user?.email ?? ''}
      pageTitle="AI Chat"
    >
      <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-800">Health Assistant</h2>
          <p className="text-xs text-slate-500">RAG-powered answers coming soon</p>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 text-slate-800'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className={`mt-1 text-xs ${msg.role === 'user' ? 'text-primary-100' : 'text-slate-500'}`}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
        </div>
        <form onSubmit={handleSend} className="border-t border-slate-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your health, check-ins, or care..."
              className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm placeholder:text-slate-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <button
              type="submit"
              className="rounded-xl bg-primary-600 px-4 py-3 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}
