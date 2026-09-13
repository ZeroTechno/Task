"use client";

import React, { useState, useCallback, useEffect, useMemo, useRef } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { DecisionNode } from "@/components/nodes/DecisionNode";
import { ActionNode } from "@/components/nodes/ActionNode";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Plus,
  Play,
  RotateCcw,
  Save,
  Loader2,
  ExternalLink,
  CheckCircle2,
  History,
  Download,
  Upload,
  Zap,
  Sparkles,
  Layers,
} from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "node-1",
    type: "decisionNode",
    position: { x: 380, y: 60 },
    data: {
      label: "Urgency Triage",
      prompt: "Is the user request urgent, an emergency, or a production outage?",
      status: "idle",
    },
  },
  {
    id: "node-2",
    type: "decisionNode",
    position: { x: 140, y: 320 },
    data: {
      label: "Escalation Router",
      prompt: "Does this involve data loss or system unavailability?",
      status: "idle",
    },
  },
  {
    id: "node-3",
    type: "actionNode",
    position: { x: 620, y: 320 },
    data: {
      label: "Documentation Queue",
      actionType: "resolve",
      status: "idle",
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: "e1-2",
    source: "node-1",
    target: "node-2",
    sourceHandle: "yes",
    label: "YES",
    type: "smoothstep",
    animated: false,
    style: { stroke: "#10b981", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" },
  },
  {
    id: "e1-3",
    source: "node-1",
    target: "node-3",
    sourceHandle: "no",
    label: "NO",
    type: "smoothstep",
    animated: false,
    style: { stroke: "#f43f5e", strokeWidth: 2 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" },
  },
];

export default function WorkflowEditor() {
  const nodeTypes = useMemo(
    () => ({ decisionNode: DecisionNode, actionNode: ActionNode }),
    []
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [inputContext, setInputContext] = useState(
    "Our entire production database is down and users cannot log in!"
  );
  const [isRunning, setIsRunning] = useState(false);
  const [executionLogs, setExecutionLogs] = useState<any[]>([]);
  const [showLogs, setShowLogs] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDeleteNode = useCallback(
    (id: string) => {
      setNodes((nds) => nds.filter((n) => n.id !== id));
      setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
    },
    [setNodes, setEdges]
  );

  const handlePromptChange = useCallback(
    (id: string, newPrompt: string) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === id ? { ...node, data: { ...node.data, prompt: newPrompt } } : node
        )
      );
    },
    [setNodes]
  );

  const handleActionChange = useCallback(
    (id: string, actionType: string) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === id ? { ...node, data: { ...node.data, actionType } } : node
        )
      );
    },
    [setNodes]
  );

  const populatedNodes = useMemo(() => {
    return nodes.map((n) => ({
      ...n,
      data: {
        ...n.data,
        onChangePrompt: handlePromptChange,
        onChangeAction: handleActionChange,
        onDelete: handleDeleteNode,
      },
    }));
  }, [nodes, handlePromptChange, handleActionChange, handleDeleteNode]);

  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === "yes";
      const isNo = params.sourceHandle === "no";
      const color = isYes ? "#10b981" : isNo ? "#f43f5e" : "#64748b";

      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}-${params.sourceHandle || "edge"}`,
        label: isYes ? "YES" : isNo ? "NO" : "",
        type: "smoothstep",
        animated: false,
        style: { stroke: color, strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const handleAddDecision = () => {
    const newId = `node-${Date.now().toString().slice(-4)}`;
    setNodes((nds) => [
      ...nds,
      {
        id: newId,
        type: "decisionNode",
        position: { x: 300 + (nds.length % 3) * 30, y: 150 + nds.length * 25 },
        data: {
          label: `Decision ${nds.length + 1}`,
          prompt: "Does this condition apply to the context?",
          status: "idle",
        },
      },
    ]);
  };

  const handleAddAction = () => {
    const newId = `action-${Date.now().toString().slice(-4)}`;
    setNodes((nds) => [
      ...nds,
      {
        id: newId,
        type: "actionNode",
        position: { x: 350 + (nds.length % 3) * 30, y: 220 + nds.length * 25 },
        data: {
          label: `Action ${nds.length + 1}`,
          actionType: "slack",
          status: "idle",
        },
      },
    ]);
  };

  const handleExportJSON = () => {
    const exportData = JSON.stringify({ nodes, edges }, null, 2);
    const blob = new Blob([exportData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `workflow-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImportJSON = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileReader = new FileReader();
    if (e.target.files && e.target.files[0]) {
      fileReader.readAsText(e.target.files[0], "UTF-8");
      fileReader.onload = (event) => {
        try {
          const parsed = JSON.parse(event.target?.result as string);
          if (parsed.nodes && parsed.edges) {
            setNodes(parsed.nodes);
            setEdges(parsed.edges);
          }
        } catch {
          alert("Invalid workflow JSON file.");
        }
      };
    }
  };

  const handleSave = () => {
    localStorage.setItem("ai_workflow_nodes", JSON.stringify(nodes));
    localStorage.setItem("ai_workflow_edges", JSON.stringify(edges));
    alert("Workflow saved locally!");
  };

  const handleReset = () => {
    localStorage.removeItem("ai_workflow_nodes");
    localStorage.removeItem("ai_workflow_edges");
    setNodes(initialNodes);
    setEdges(initialEdges);
    setExecutionLogs([]);
    setShowLogs(false);
  };

  const handleRunWorkflow = async () => {
    if (!inputContext.trim()) return;

    setIsRunning(true);
    setNodes((nds) => nds.map((n) => ({ ...n, data: { ...n.data, status: "idle" } })));
    setEdges((eds) =>
      eds.map((e) => ({ ...e, animated: false, style: { ...e.style, opacity: 1, strokeWidth: 2 } }))
    );

    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inputContext, nodes, edges }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Execution failed");

      const history = data.history || [];
      setExecutionLogs(history);
      setShowLogs(true);

      // Visual updates
      setNodes((nds) =>
        nds.map((n) => {
          const match = history.find((h: any) => h.nodeId === n.id);
          if (match) {
            return {
              ...n,
              data: {
                ...n.data,
                status: match.type === "action" ? "completed" : match.decision.toLowerCase(),
              },
            };
          }
          return { ...n, data: { ...n.data, status: "idle" } };
        })
      );

      setEdges((eds) =>
        eds.map((edge) => {
          const step = history.find((h: any) => h.nodeId === edge.source);
          if (step && step.decision) {
            const matched = step.decision.toLowerCase() === edge.sourceHandle;
            return {
              ...edge,
              animated: matched,
              style: {
                ...edge.style,
                strokeWidth: matched ? 3 : 1.5,
                opacity: matched ? 1 : 0.2,
              },
            };
          }
          return { ...edge, style: { ...edge.style, opacity: 0.2 } };
        })
      );
    } catch (err: any) {
      alert(`Execution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    const savedNodes = localStorage.getItem("ai_workflow_nodes");
    const savedEdges = localStorage.getItem("ai_workflow_edges");
    if (savedNodes && savedEdges) {
      try {
        setNodes(JSON.parse(savedNodes));
        setEdges(JSON.parse(savedEdges));
      } catch (e) {
        console.error("Failed to parse saved workflow", e);
      }
    }
  }, [setNodes, setEdges]);

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-50/60 dark:bg-slate-950">
      {/* Sleek Top Navigation */}
      <header className="h-16 border-b border-slate-200/80 dark:border-slate-800/80 px-6 flex items-center justify-between bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl z-20 gap-4 shrink-0 shadow-sm">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-xs font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Visual AI Workflow
            </h1>
            <p className="text-[10px] text-slate-500 font-medium">Qwen / Groq · Inngest</p>
          </div>
        </div>

        {/* Input Bar */}
        <div className="flex-1 max-w-xl mx-4">
          <div className="relative">
            <Input
              placeholder="Enter scenario to evaluate against the workflow..."
              value={inputContext}
              onChange={(e) => setInputContext(e.target.value)}
              className="h-10 text-xs pl-9 pr-24 rounded-xl border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-950/60 focus-visible:ring-indigo-500/30"
            />
            <Sparkles className="w-4 h-4 text-indigo-500 absolute left-3 top-3 pointer-events-none" />
            <button
              onClick={handleRunWorkflow}
              disabled={isRunning}
              className="absolute right-1.5 top-1.5 px-3 py-1 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-[11px] font-semibold rounded-lg hover:opacity-90 transition disabled:opacity-50 flex items-center gap-1.5"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" /> Evaluating
                </>
              ) : (
                <>
                  <Play className="w-3 h-3 fill-current" /> Run
                </>
              )}
            </button>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          <div className="flex items-center bg-slate-100 dark:bg-slate-800/60 p-1 rounded-xl gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleAddDecision}
              className="h-8 px-2.5 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-700 rounded-lg shadow-none"
            >
              <Plus className="w-3.5 h-3.5 mr-1 text-indigo-500" /> Decision
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleAddAction}
              className="h-8 px-2.5 text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-700 rounded-lg shadow-none"
            >
              <Zap className="w-3.5 h-3.5 mr-1 text-amber-500 fill-current" /> Action
            </Button>
          </div>

          <div className="h-4 w-px bg-slate-200 dark:bg-slate-800 mx-1" />

          <Button
            variant="outline"
            size="sm"
            onClick={handleExportJSON}
            className="h-8 text-xs rounded-xl"
            title="Export workflow JSON"
          >
            <Download className="w-3.5 h-3.5" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            className="h-8 text-xs rounded-xl"
            title="Import workflow JSON"
          >
            <Upload className="w-3.5 h-3.5" />
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImportJSON}
            accept=".json"
            className="hidden"
          />

          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            className="h-8 text-xs rounded-xl"
            title="Save to local storage"
          >
            <Save className="w-3.5 h-3.5" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="h-8 text-xs rounded-xl text-slate-500"
            title="Reset to default"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </Button>

          {executionLogs.length > 0 && (
            <Button
              variant={showLogs ? "secondary" : "outline"}
              size="sm"
              onClick={() => setShowLogs(!showLogs)}
              className="h-8 text-xs rounded-xl gap-1.5"
            >
              <History className="w-3.5 h-3.5" /> Logs
            </Button>
          )}

          <a
            href="http://localhost:8288/runs"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 p-2"
            title="Open Inngest dashboard"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </header>

      {/* Canvas Area */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={populatedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="bg-slate-50/50 dark:bg-slate-950"
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1.2} color="#cbd5e1" />
          <Controls className="!bg-white/90 dark:!bg-slate-900/90 !border-slate-200 dark:!border-slate-800 !rounded-xl !shadow-md !overflow-hidden" />
          <MiniMap
            className="!bg-white/80 dark:!bg-slate-900/80 !border-slate-200 dark:!border-slate-800 !rounded-xl !shadow-md !overflow-hidden"
            nodeStrokeWidth={2}
            zoomable
            pannable
          />
        </ReactFlow>

        {/* Floating Execution Log Panel */}
        {showLogs && executionLogs.length > 0 && (
          <div className="absolute bottom-6 right-6 w-96 max-h-[380px] bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-4 flex flex-col z-30 animate-in fade-in slide-in-from-bottom-3 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
                  Execution Trace
                </span>
              </div>
              <button
                onClick={() => setShowLogs(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs p-1 rounded-md"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 pr-1 text-xs">
              {executionLogs.map((log, index) => (
                <div
                  key={index}
                  className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 flex flex-col gap-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800 dark:text-slate-200">
                      {index + 1}. {log.label}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        log.type === "action"
                          ? "bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800"
                          : log.decision === "YES"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800"
                          : "bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800"
                      }`}
                    >
                      {log.type === "action" ? `ACTION: ${log.action}` : log.decision}
                    </span>
                  </div>
                  {log.prompt && (
                    <p className="text-[11px] text-slate-500 italic line-clamp-2">
                      "{log.prompt}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
