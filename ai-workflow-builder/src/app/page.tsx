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
import { Plus, Play, RotateCcw, Save } from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "node-1",
    type: "decisionNode",
    position: { x: 250, y: 50 },
    data: {
      label: "Input Triage",
      prompt: "Is the user request urgent or high priority?",
      status: "idle",
    },
  },
  {
    id: "node-2",
    type: "decisionNode",
    position: { x: 80, y: 280 },
    data: {
      label: "Support Router",
      prompt: "Does this require immediate engineering escalation?",
      status: "idle",
    },
  },
  {
    id: "node-3",
    type: "decisionNode",
    position: { x: 420, y: 280 },
    data: {
      label: "Standard Queue",
      prompt: "Can this inquiry be resolved with documentation?",
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
    animated: true,
    style: { stroke: "#10b981", strokeWidth: 2 },
  },
  {
    id: "e1-3",
    source: "node-1",
    target: "node-3",
    sourceHandle: "no",
    label: "NO",
    animated: true,
    style: { stroke: "#f43f5e", strokeWidth: 2 },
  },
];

export default function WorkflowEditor() {
  const nodeTypes = useMemo(() => ({ decisionNode: DecisionNode }), []);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update prompt handler
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

  // Inject handlePromptChange into node data
  const populatedNodes = useMemo(() => {
    return nodes.map((n) => ({
      ...n,
      data: {
        ...n.data,
        onChangePrompt: handlePromptChange,
      },
    }));
  }, [nodes, handlePromptChange]);

  // Connect handler styling edge based on YES or NO handle
  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === "yes";
      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}-${params.sourceHandle}`,
        label: isYes ? "YES" : "NO",
        animated: true,
        style: {
          stroke: isYes ? "#10b981" : "#f43f5e",
          strokeWidth: 2,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  // Add new node
  const handleAddNode = () => {
    const newId = `node-${Date.now().toString().slice(-4)}`;
    const newNode: Node = {
      id: newId,
      type: "decisionNode",
      position: { x: 250 + (nodes.length % 3) * 40, y: 150 + nodes.length * 40 },
      data: {
        label: `Decision ${nodes.length + 1}`,
        prompt: "Does this condition apply?",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  // Local storage save/load
  const handleSave = () => {
    localStorage.setItem("ai_workflow_nodes", JSON.stringify(nodes));
    localStorage.setItem("ai_workflow_edges", JSON.stringify(edges));
    alert("Workflow saved locally!");
  };

  const handleReset = () => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    localStorage.removeItem("ai_workflow_nodes");
    localStorage.removeItem("ai_workflow_edges");
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
      <header className="h-14 border-b px-4 flex items-center justify-between bg-card z-10">
        <div className="flex items-center gap-2">
          <h1 className="text-base font-bold tracking-tight">Visual AI Workflow</h1>
          <span className="text-xs text-muted-foreground">(Phase 2: Foundations)</span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleAddNode}>
            <Plus className="w-4 h-4 mr-1" /> Add Decision Node
          </Button>
          <Button variant="outline" size="sm" onClick={handleSave}>
            <Save className="w-4 h-4 mr-1" /> Save
          </Button>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-1" /> Reset
          </Button>
          <Button size="sm" className="bg-primary text-primary-foreground">
            <Play className="w-4 h-4 mr-1" /> Run Workflow
          </Button>
        </div>
      </header>

      {/* Main Canvas */}
      <div className="flex-1 w-full h-full">
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
      </div>
    </div>
  );
}