import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";

export interface DecisionNodeData {
  label: string;
  prompt: string;
  status?: "idle" | "running" | "yes" | "no";
  onChangePrompt?: (id: string, prompt: string) => void;
}

export const DecisionNode = memo(({ id, data, selected }: NodeProps<any>) => {
  const getBorderColor = () => {
    if (data.status === "running") return "border-blue-500 ring-2 ring-blue-400/50 animate-pulse";
    if (data.status === "yes") return "border-emerald-500 ring-2 ring-emerald-400/40 shadow-emerald-950/20";
    if (data.status === "no") return "border-rose-500 ring-2 ring-rose-400/40 shadow-rose-950/20";
    if (selected) return "border-primary ring-2 ring-primary/30";
    return "border-border";
  };

  return (
    <div
      className={`relative w-[280px] rounded-xl border bg-card text-card-foreground shadow-md transition-all duration-300 p-4 ${getBorderColor()}`}
    >
      {/* Incoming edge handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-muted-foreground border-2 border-background"
      />

      <div className="flex items-center justify-between pb-2 border-b mb-3">
        <span className="font-semibold text-xs tracking-wide uppercase text-foreground">
          {data.label}
        </span>
        {data.status && data.status !== "idle" && (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
              data.status === "yes"
                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                : data.status === "no"
                ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                : "bg-blue-500/10 text-blue-600 animate-pulse"
            }`}
          >
            {data.status}
          </span>
        )}
      </div>

      <div className="space-y-1.5">
        <label className="text-[11px] text-muted-foreground font-medium block">
          Decision Prompt (must resolve to YES/NO):
        </label>
        <textarea
          rows={3}
          value={data.prompt}
          onChange={(e) => data.onChangePrompt?.(id, e.target.value)}
          placeholder="e.g. Is this request urgent?"
          className="w-full text-xs p-2.5 rounded-lg border bg-muted/40 resize-none focus:outline-none focus:ring-1 focus:ring-primary focus:bg-background transition"
        />
      </div>

      {/* YES Handle */}
      <div className="flex justify-between items-center mt-3 pt-2 text-[11px] font-bold text-muted-foreground border-t border-muted/50">
        <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
          <span>YES</span>
        </div>
        <div className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
          <span>NO</span>
        </div>
      </div>

      <Handle
        type="source"
        id="yes"
        position={Position.Bottom}
        className="!left-[25%] w-3 h-3 !bg-emerald-500 border-2 border-background"
      />

      {/* NO Handle */}
      <Handle
        type="source"
        id="no"
        position={Position.Bottom}
        className="!left-[75%] w-3 h-3 !bg-rose-500 border-2 border-background"
      />
    </div>
  );
});

DecisionNode.displayName = "DecisionNode";
