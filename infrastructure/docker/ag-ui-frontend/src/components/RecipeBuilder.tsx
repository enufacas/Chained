/**
 * RecipeBuilder Component
 *
 * UI for creating and managing agent workflow recipes.
 * Allows users to select agents and define execution sequences.
 */

"use client";

import { useState, useEffect, useCallback } from "react";

interface AgentInfo {
  id: string;
  displayName: string;
  description: string;
  icon: string;
  category: string;
  configured: boolean;
  skills: string[];
}

interface RecipeStep {
  agentId: string;
  instruction: string;
  required: boolean;
  dependsOn: string[];
}

interface Recipe {
  id: string;
  name: string;
  description: string;
  goal: string;
  steps: RecipeStep[];
  tags: string[];
}

interface RecipeBuilderProps {
  onRecipeSelect?: (recipe: Recipe) => void;
  onGoalSubmit?: (recipeId: string, goal: string) => void;
}

export default function RecipeBuilder({ onRecipeSelect, onGoalSubmit }: RecipeBuilderProps) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch agents and recipes
  const fetchData = useCallback(async () => {
    try {
      const [agentsRes, recipesRes] = await Promise.all([
        fetch("/api/registry"),
        fetch("/api/team"),
      ]);
      
      if (agentsRes.ok) {
        const data = await agentsRes.json();
        setAgents(data.agents || []);
      }
      
      if (recipesRes.ok) {
        const data = await recipesRes.json();
        setRecipes(data.recipes || []);
      }
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  const handleRecipeSelect = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    onRecipeSelect?.(recipe);
  };
  
  const handleSubmit = async () => {
    if (!selectedRecipe || !goal.trim()) return;
    
    setExecuting(true);
    
    try {
      onGoalSubmit?.(selectedRecipe.id, goal.trim());
    } finally {
      setExecuting(false);
    }
  };
  
  const getAgentInfo = (agentId: string): AgentInfo | undefined => {
    return agents.find((a) => a.id === agentId);
  };
  
  if (loading) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-slate-700 rounded"></div>
          <div className="h-16 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📋</span>
          <div>
            <h3 className="font-semibold text-white">Recipe Builder</h3>
            <p className="text-xs text-slate-400">
              Select a recipe and define your goal
            </p>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="p-4 bg-red-500/10 border-b border-red-500/30">
          <p className="text-sm text-red-400">⚠️ {error}</p>
        </div>
      )}
      
      {/* Recipe Selection */}
      <div className="p-4 border-b border-slate-700">
        <h4 className="text-sm font-medium text-slate-300 mb-3">Available Recipes</h4>
        <div className="grid gap-3">
          {recipes.map((recipe) => (
            <button
              key={recipe.id}
              onClick={() => handleRecipeSelect(recipe)}
              className={`p-4 rounded-lg border text-left transition-all ${
                selectedRecipe?.id === recipe.id
                  ? "border-purple-500 bg-purple-500/10"
                  : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h5 className="font-medium text-white">{recipe.name}</h5>
                  <p className="text-xs text-slate-400 mt-1">{recipe.description}</p>
                </div>
                <div className="flex gap-1">
                  {recipe.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 text-xs rounded bg-slate-700 text-slate-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Agent Steps */}
              <div className="mt-3 flex items-center gap-2">
                {recipe.steps.map((step, i) => {
                  const agent = getAgentInfo(step.agentId);
                  return (
                    <div key={i} className="flex items-center">
                      {i > 0 && <span className="text-slate-600 mx-1">→</span>}
                      <span
                        className={`text-lg ${agent?.configured ? "" : "opacity-50"}`}
                        title={`${agent?.displayName || step.agentId}${agent?.configured ? "" : " (not configured)"}`}
                      >
                        {agent?.icon || "🤖"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </button>
          ))}
        </div>
      </div>
      
      {/* Selected Recipe Details */}
      {selectedRecipe && (
        <div className="p-4 border-b border-slate-700 bg-slate-800/50">
          <h4 className="text-sm font-medium text-slate-300 mb-3">
            Recipe Steps: {selectedRecipe.name}
          </h4>
          <div className="space-y-2">
            {selectedRecipe.steps.map((step, i) => {
              const agent = getAgentInfo(step.agentId);
              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 p-3 rounded-lg border ${
                    agent?.configured
                      ? "border-slate-700 bg-slate-800"
                      : "border-yellow-500/30 bg-yellow-500/5"
                  }`}
                >
                  <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white">
                    {i + 1}
                  </div>
                  <span className="text-xl">{agent?.icon || "🤖"}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white">
                        {agent?.displayName || step.agentId}
                      </span>
                      {!step.required && (
                        <span className="px-1.5 py-0.5 text-xs rounded bg-slate-700 text-slate-400">
                          optional
                        </span>
                      )}
                      {!agent?.configured && (
                        <span className="px-1.5 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400">
                          ⚠️ not configured
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5 truncate">
                      {step.instruction.substring(0, 100)}...
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Goal Input */}
      <div className="p-4">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Your Goal
        </label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Describe what you want to accomplish..."
          className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
          rows={3}
          disabled={!selectedRecipe || executing}
        />
        
        <button
          onClick={handleSubmit}
          disabled={!selectedRecipe || !goal.trim() || executing}
          className="mt-4 w-full py-3 px-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all"
        >
          {executing ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">⏳</span>
              Executing Team...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              🚀 Execute Recipe
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
