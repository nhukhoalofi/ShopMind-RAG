import {
  Activity,
  Boxes,
  Database,
  FlaskConical,
  MessageSquare,
  Search,
  ShoppingBag,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import clsx from "clsx";

const navigation = [
  { label: "Chat", to: "/chat", icon: MessageSquare },
  { label: "Retrieval Debug", to: "/retrieval", icon: Search },
  { label: "Products", to: "/products", icon: ShoppingBag },
  { label: "Knowledge Base", to: "/knowledge-base", icon: Database },
  { label: "Evaluation", to: "/evaluation", icon: FlaskConical },
  { label: "System Status", to: "/status", icon: Activity },
];

export function Sidebar() {
  return (
    <aside className="border-b border-slate-800 bg-slate-950 px-4 py-4 text-white lg:min-h-screen lg:w-64 lg:border-b-0 lg:border-r">
      <div className="mb-6 flex items-center gap-3 px-2">
        <div className="rounded-xl bg-indigo-500 p-2">
          <Boxes className="h-6 w-6" />
        </div>
        <div>
          <p className="font-bold">ShopMind</p>
          <p className="text-xs text-slate-400">RAG Control Center</p>
        </div>
      </div>
      <nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-1">
        {navigation.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                isActive
                  ? "bg-indigo-500 text-white"
                  : "text-slate-300 hover:bg-slate-900 hover:text-white",
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
