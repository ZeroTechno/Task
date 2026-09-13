import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Zap, Trash2, CheckCircle2 } from "lucide-react";

export interface ActionNodeData {
  label: string;
  actionType: "slack" | "email" | "ticket" | "resolve";
  status?: "idle" | "running" | "completed";
  onDelete?: (id: string) => void;
  onChangeAction?: (id: string, type: string) => void;
}

export const ActionNode = memo(({ id, data, selected }: NodeProps<any>) => {
  return (
    <div
      className={`group relative w-[290px] rounded-2xl border bg-white/95 dark:bg-slate-900/95 backdrop-blur-md shadow-lg shadow-slate-200/50 dark:shadow-black/40 transition-all duration-200 ${
        data.status === "completed"
          ? "border-amber-500/80 ring-2 ring-amber-500/20 shadow-amber-500/10"
          : selected
          ? "border-slate-800 ring-2 ring-slate-400/30 dark:border-slate-200"
          : "border-slate-200 hover:border-slate-300 dark:border-slate-800"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-slate-400 dark:!bg-slate-500 !border-2 !border-white dark:!border-slate-900 shadow transition-transform group-hover:scale-110"
      />

      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-800/30 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400">
            <Zap className="w-3.5 h-3.5 fill-current" />
          </div>
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 tracking-tight">
            {data.label}
          </span>
        </div>

        <button
          onClick={() => data.onDelete?.(id)}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 rounded-md"
          title="Delete node"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="p-4 space-y-2">
        <label className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block">
          Terminal Integration
        </label>
        <select
          value={data.actionType || "slack"}
          onChange={(e) => data.onChangeAction?.(id, e.target.value)}
          className="w-full text-xs font-medium p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/50 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition"
        >
          <option value="slack">⚡ Escalate to PagerDuty / Slack</option>
          <option value="ticket">📋 Create Jira / GitHub Ticket</option>
          <option value="email">✉️ Dispatch Support Email</option>
          <option value="resolve">✅ Mark Workflow Auto-Resolved</option>
        </select>
      </div>

      {data.status === "completed" && (
        <div className="px-4 py-2 border-t border-amber-100 dark:border-amber-900/40 bg-amber-50/50 dark:bg-amber-950/30 rounded-b-2xl flex items-center gap-1.5 text-[11px] font-bold text-amber-600 dark:text-amber-400">
          <CheckCircle2 className="w-3.5 h-3.5" /> Action Executed
        </div>
      )}
    </div>
  );
});

ActionNode.displayName = "ActionNode";
