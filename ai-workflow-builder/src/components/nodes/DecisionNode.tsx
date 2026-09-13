import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { GitBranch, Trash2, HelpCircle } from "lucide-react";

export interface DecisionNodeData {
  label: string;
  prompt: string;
  status?: "idle" | "running" | "yes" | "no";
  onChangePrompt?: (id: string, prompt: string) => void;
  onDelete?: (id: string) => void;
}

export const DecisionNode = memo(({ id, data, selected }: NodeProps<any>) => {
  const getStatusStyles = () => {
    switch (data.status) {
      case "yes":
        return "border-emerald-500/80 ring-2 ring-emerald-500/20 shadow-emerald-500/10";
      case "no":
        return "border-rose-500/80 ring-2 ring-rose-500/20 shadow-rose-500/10";
      case "running":
        return "border-indigo-500 ring-2 ring-indigo-500/30 animate-pulse";
      default:
        return selected ? "border-slate-800 ring-2 ring-slate-400/30 dark:border-slate-200" : "border-slate-200 hover:border-slate-300 dark:border-slate-800";
    }
  };

  return (
    <div
      className={`group relative w-[310px] rounded-2xl border bg-white/95 dark:bg-slate-900/95 backdrop-blur-md shadow-lg shadow-slate-200/50 dark:shadow-black/40 transition-all duration-200 ${getStatusStyles()}`}
    >
      {/* Top Input Handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !bg-slate-400 dark:!bg-slate-500 !border-2 !border-white dark:!border-slate-900 shadow transition-transform group-hover:scale-110"
      />

      {/* Card Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-800/30 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400">
            <GitBranch className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 tracking-tight">
            {data.label}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {data.status && data.status !== "idle" && (
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                data.status === "yes"
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800"
                  : data.status === "no"
                  ? "bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800"
                  : "bg-indigo-50 text-indigo-700 animate-pulse border border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300"
              }`}
            >
              {data.status}
            </span>
          )}
          <button
            onClick={() => data.onDelete?.(id)}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 rounded-md"
            title="Delete node"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-4 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-medium text-slate-500 dark:text-slate-400">
          <span>Evaluation Condition</span>
          <HelpCircle className="w-3 h-3 text-slate-400" />
        </div>
        <textarea
          rows={3}
          value={data.prompt}
          onChange={(e) => data.onChangePrompt?.(id, e.target.value)}
          placeholder="Is this condition met? (YES/NO)"
          className="w-full text-xs leading-relaxed p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/50 text-slate-800 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 resize-none transition"
        />
      </div>

      {/* Card Footer / Output Handles */}
      <div className="flex items-center justify-between px-5 py-2.5 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/30 dark:bg-slate-900/40 rounded-b-2xl text-[11px] font-bold">
        <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
          <span>YES</span>
        </div>
        <div className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
          <span>NO</span>
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block" />
        </div>
      </div>

      {/* YES Bottom Source Handle */}
      <Handle
        type="source"
        id="yes"
        position={Position.Bottom}
        className="!left-[22%] !w-3 !h-3 !bg-emerald-500 !border-2 !border-white dark:!border-slate-900 shadow hover:scale-125 transition-transform"
      />

      {/* NO Bottom Source Handle */}
      <Handle
        type="source"
        id="no"
        position={Position.Bottom}
        className="!left-[78%] !w-3 !h-3 !bg-rose-500 !border-2 !border-white dark:!border-slate-900 shadow hover:scale-125 transition-transform"
      />
    </div>
  );
});

DecisionNode.displayName = "DecisionNode";
