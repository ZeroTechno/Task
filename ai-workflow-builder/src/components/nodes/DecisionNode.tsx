"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

export interface DecisionNodeData {
  label: string;
  prompt: string;
  onChangePrompt?: (id: string, prompt: string) => void;
  status?: "idle" | "running" | "yes" | "no" | "failed";
}

export const DecisionNode = memo(({ id, data, isConnectable }: NodeProps) => {
  const nodeData = data as unknown as DecisionNodeData;

  const getBorderColor = () => {
    switch (nodeData.status) {
      case "running":
        return "border-blue-500 ring-2 ring-blue-400";
      case "yes":
        return "border-emerald-500 ring-2 ring-emerald-400";
      case "no":
        return "border-rose-500 ring-2 ring-rose-400";
      case "failed":
        return "border-destructive ring-2 ring-destructive";
      default:
        return "border-border";
    }
  };

  return (
    <Card className={`w-72 shadow-md bg-card transition-all ${getBorderColor()}`}>
      {/* Incoming connection handle (Top) */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-muted-foreground"
      />

      <CardHeader className="p-3 pb-2 flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-sm font-semibold">{nodeData.label || "Decision Node"}</CardTitle>
        {nodeData.status && nodeData.status !== "idle" && (
          <Badge
            variant={
              nodeData.status === "yes"
                ? "default"
                : nodeData.status === "no"
                ? "secondary"
                : "outline"
            }
            className="text-[10px] uppercase tracking-wider"
          >
            {nodeData.status}
          </Badge>
        )}
      </CardHeader>

      <CardContent className="p-3 pt-0">
        <label className="text-[11px] text-muted-foreground block mb-1">
          Decision Prompt (must resolve to YES/NO):
        </label>
        <Textarea
          className="text-xs resize-none nodrag"
          rows={3}
          placeholder="e.g. Is this user request asking for technical support?"
          value={nodeData.prompt || ""}
          onChange={(e) => nodeData.onChangePrompt?.(id, e.target.value)}
        />

        {/* Output Branch Handles */}
        <div className="flex justify-between items-center mt-3 pt-2 border-t text-[10px] font-semibold">
          <div className="flex items-center gap-1 text-emerald-600">
            <span>YES</span>
            <Handle
              type="source"
              position={Position.Bottom}
              id="yes"
              style={{ left: "25%" }}
              isConnectable={isConnectable}
              className="w-3 h-3 bg-emerald-500"
            />
          </div>
          <div className="flex items-center gap-1 text-rose-600">
            <Handle
              type="source"
              position={Position.Bottom}
              id="no"
              style={{ left: "75%" }}
              isConnectable={isConnectable}
              className="w-3 h-3 bg-rose-500"
            />
            <span>NO</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

DecisionNode.displayName = "DecisionNode";
