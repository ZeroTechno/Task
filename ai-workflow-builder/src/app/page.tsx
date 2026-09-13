"use client";

import React, { useState, useCallback, useEffect, useMemo } from "react";
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
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { DecisionNode } from "@/components/nodes/DecisionNode";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Play, RotateCcw, Save, Loader2, ExternalLink, CheckCircle2, History } from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "node-1",
    type: "decisionNode",
    position: { x: 250, y: 50 },
    data: {
      label: "Urgency Check",
      prompt: "Is the user request urgent or an emergency?",
      status: "idle",
    },
  },
  {
    id: "node-2",
    type: "decisionNode",
    position: { x: 80, y: 280 },
    data: {
      label: "Escalation Router",
      prompt: "Does this involve a production outage or data loss?",
      status: "idle",
    },
  },
  {
    id: "node-3",
    type: "decisionNode",
    position: { x: 420, y: 280 },
    data: {
      label: "Documentation Queue",
      prompt: "Can this inquiry be resolved with public documentation?",
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
    animated: false,
    style: { stroke: "#10b981", strokeWidth: 2 },
  },
  {
    id: "e1-3",
    source: "node-1",
    target: "node-3",
    sourceHandle: "no",
    label: "NO",
    animated: false,
    style: { stroke: "#f43f5e", strokeWidth: 2 },
  },
];

export default function WorkflowEditor() {
  const nodeTypes = useMemo(() => ({ decisionNode: DecisionNode }), []);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [inputContext, setInputContext] = useState(
    "Our entire production database is down and users cannot log in!"
  );
  const [isRunning, setIsRunning] = useState(false);
  const [executionLogs, setExecutionLogs] = useState<any[]>([]);
  const [showLogs, setShowLogs] = useState(false);

  const handlePromptChange = useCallback(
    (id: string, newPrompt: string) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === id) {
            return {
              ...node,
              data: { ...node.data, prompt: newPrompt },
            };
          }
          return node;
        })
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
      },
    }));
  }, [nodes, handlePromptChange]);

  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === "yes";
      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}-${params.sourceHandle}`,
        label: isYes ? "YES" : "NO",
        animated: false,
        style: {
          stroke: isYes ? "#10b981" : "#f43f5e",
          strokeWidth: 2,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const handleAddNode = () => {
    const newId = `node-${Date.now().toString().slice(-4)}`;
    const newNode: Node = {
      id: newId,
      type: "decisionNode",
      position: { x: 250 + (nodes.length % 3) * 40, y: 150 + nodes.length * 40 },
      data: {
        label: `Decision ${nodes.length + 1}`,
        prompt: "Does this condition apply to the context?",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
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
    if (!inputContext.trim()) {
      alert("Please enter a test input message.");
      return;
    }

    setIsRunning(true);
    // Reset previous run highlights
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
      if (!res.ok) {
        throw new Error(data.error || "Failed to execute");
      }

      const history = data.history || [];
      setExecutionLogs(history);
      setShowLogs(true);

      // 1. Highlight visited nodes
      setNodes((nds) =>
        nds.map((n) => {
          const match = history.find((h: any) => h.nodeId === n.id);
          if (match) {
            return {
              ...n,
              data: {
                ...n.data,
                status: match.decision.toLowerCase(),
              },
            };
          }
          return { ...n, data: { ...n.data, status: "idle" } };
        })
      );

      // 2. Animate and emphasize edges traversed
      setEdges((eds) =>
        eds.map((edge) => {
          const step = history.find((h: any) => h.nodeId === edge.source);
          if (step) {
            const matchedDecision = step.decision.toLowerCase() === edge.sourceHandle;
            return {
              ...edge,
              animated: matchedDecision,
              style: {
                ...edge.style,
                strokeWidth: matchedDecision ? 3 : 1.5,
                opacity: matchedDecision ? 1 : 0.25,
              },
            };
          }
          return { ...edge, style: { ...edge.style, opacity: 0.25 } };
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
    <div className="w-screen h-screen flex flex-col bg-background">
      {/* Top action toolbar */}
      <header className="h-16 border-b px-4 flex items-center justify-between bg-card z-10 gap-4 shrink-0">
        <div className="flex items-center gap-2 shrink-0">
          <h1 className="text-sm font-bold tracking-tight">Visual AI Workflow</h1>
          <span className="text-xs text-muted-foreground hidden sm:inline">(Phase 4: Polish)</span>
        </div>

        {/* Input context tester */}
        <div className="flex-1 max-w-xl flex items-center gap-2">
          <Input
            placeholder="Enter test user scenario or message..."
            value={inputContext}
            onChange={(e) => setInputContext(e.target.value)}
            className="text-xs h-9"
          />
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button variant="outline" size="sm" onClick={handleAddNode}>
            <Plus className="w-4 h-4 mr-1" /> Add Node
          </Button>
          <Button variant="outline" size="sm" onClick={handleSave}>
            <Save className="w-4 h-4 mr-1" /> Save
          </Button>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-1" /> Reset
          </Button>
          <Button
            size="sm"
            onClick={handleRunWorkflow}
            disabled={isRunning}
            className="bg-primary text-primary-foreground font-semibold"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 mr-1 animate-spin" /> Evaluating...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-1 fill-current" /> Run Workflow
              </>
            )}
          </Button>

          {executionLogs.length > 0 && (
            <Button variant="outline" size="sm" onClick={() => setShowLogs(!showLogs)}>
              <History className="w-4 h-4 mr-1" /> Logs
            </Button>
          )}

          <a
            href="http://localhost:8288/runs"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-blue-600 flex items-center gap-1 hover:underline ml-1"
          >
            Inngest <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </header>

      {/* React Flow Canvas */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={populatedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap nodeStrokeWidth={3} zoomable pannable />
        </ReactFlow>

        {/* Floating Execution Log Panel */}
        {showLogs && executionLogs.length > 0 && (
          <div className="absolute bottom-6 right-6 w-96 max-h-80 bg-card/95 backdrop-blur border rounded-xl shadow-xl p-4 flex flex-col z-20 overflow-hidden">
            <div className="flex items-center justify-between pb-2 border-b mb-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span className="text-xs font-bold uppercase tracking-wider">Execution Steps</span>
              </div>
              <button
                onClick={() => setShowLogs(false)}
                className="text-muted-foreground hover:text-foreground text-xs"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {executionLogs.map((log, index) => (
                <div
                  key={index}
                  className="p-2.5 rounded-lg border bg-muted/40 flex flex-col gap-1 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground">{log.label}</span>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        log.decision === "YES"
                          ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                          : "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      }`}
                    >
                      {log.decision}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground line-clamp-2 italic">
                    "{log.prompt}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
