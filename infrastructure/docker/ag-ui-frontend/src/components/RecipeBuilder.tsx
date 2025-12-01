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
  isExecuting?: boolean;
}

export default function RecipeBuilder({ onRecipeSelect, onGoalSubmit, isExecuting = false }: RecipeBuilderProps) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(true);
  const [localExecuting, setLocalExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Combine local and prop executing state
  const executing = isExecuting || localExecuting;
  
  // Reset local executing state when parent's isExecuting changes to false
  useEffect(() => {
    if (!isExecuting && localExecuting) {
      setLocalExecuting(false);
    }
  }, [isExecuting, localExecuting]);
  
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
    if (!selectedRecipe || !goal.trim() || executing) return;
    
    const currentGoal = goal.trim();
    setLocalExecuting(true);
    setGoal(""); // Clear the goal immediately
    
    try {
      onGoalSubmit?.(selectedRecipe.id, currentGoal);
    } catch (error) {
      // Restore goal if execution failed to start
      setGoal(currentGoal);
      setLocalExecuting(false);
      console.error("Failed to start execution:", error);
    }
    // Note: localExecuting will be reset via useEffect when isExecuting prop changes to false
  };
  
  const getAgentInfo = (agentId: string): AgentInfo | undefined => {
    return agents.find((a) => a.id === agentId);
  };
  
  if (loading) {
    return (
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-3 sm:p-4 animate-pulse">
        <div className="h-5 bg-slate-700 rounded w-1/3 mb-3"></div>
        <div className="space-y-2">
          <div className="h-12 bg-slate-700 rounded"></div>
          <div className="h-12 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
      {/* Header - Compact */}
      <div className="px-2 py-2 sm:px-3 sm:py-2 border-b border-slate-700 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-2">
          <span className="text-lg sm:text-xl">📋</span>
          <div>
            <h3 className="text-sm font-semibold text-white">Recipe Builder</h3>
            <p className="text-[10px] sm:text-xs text-slate-400">
              Select a recipe
            </p>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="px-2 py-2 sm:px-3 sm:py-2 bg-red-500/10 border-b border-red-500/30">
          <p className="text-xs text-red-400">⚠️ {error}</p>
        </div>
      )}
      
      {/* Recipe Selection - Compact */}
      <div className="p-2 sm:p-3 border-b border-slate-700">
        <h4 className="text-[10px] sm:text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Recipes</h4>
        <div className="grid gap-2">
          {recipes.map((recipe) => (
            <button
              key={recipe.id}
              onClick={() => handleRecipeSelect(recipe)}
              className={`p-2 sm:p-3 rounded border text-left transition-all active:scale-[0.98] ${
                selectedRecipe?.id === recipe.id
                  ? "border-purple-500 bg-purple-500/10 shadow-lg shadow-purple-500/10"
                  : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h5 className="text-xs sm:text-sm font-medium text-white">{recipe.name}</h5>
                  <p className="text-[10px] sm:text-xs text-slate-400 mt-0.5 line-clamp-1">{recipe.description}</p>
                </div>
                <div className="flex gap-0.5 sm:gap-1 flex-shrink-0">
                  {recipe.tags.slice(0, 2).map((tag) => (
                    <span
                      key={tag}
                      className="px-1 py-0.5 text-[10px] rounded bg-slate-700 text-slate-300 hidden sm:inline"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Agent Steps - Compact */}
              <div className="mt-1.5 sm:mt-2 flex items-center gap-1">
                {recipe.steps.map((step, i) => {
                  const agent = getAgentInfo(step.agentId);
                  return (
                    <div key={i} className="flex items-center">
                      {i > 0 && <span className="text-slate-600 mx-0.5 text-xs">→</span>}
                      <span
                        className={`text-sm sm:text-base ${agent?.configured ? "" : "opacity-50"}`}
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
      
      {/* Selected Recipe Details - Collapsible on mobile */}
      {selectedRecipe && (
        <div className="p-2 sm:p-3 border-b border-slate-700 bg-slate-800/50">
          <h4 className="text-[10px] sm:text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
            Steps: {selectedRecipe.name}
          </h4>
          <div className="space-y-1.5 sm:space-y-2">
            {selectedRecipe.steps.map((step, i) => {
              const agent = getAgentInfo(step.agentId);
              return (
                <div
                  key={i}
                  className={`flex items-center gap-2 p-2 rounded border ${
                    agent?.configured
                      ? "border-slate-700 bg-slate-800"
                      : "border-yellow-500/30 bg-yellow-500/5"
                  }`}
                >
                  <div className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-[10px] font-bold text-white">
                    {i + 1}
                  </div>
                  <span className="text-base">{agent?.icon || "🤖"}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1 flex-wrap">
                      <span className="text-xs font-medium text-white">
                        {agent?.displayName || step.agentId}
                      </span>
                      {!step.required && (
                        <span className="px-1 py-0.5 text-[10px] rounded bg-slate-700 text-slate-400">
                          opt
                        </span>
                      )}
                      {!agent?.configured && (
                        <span className="px-1 py-0.5 text-[10px] rounded bg-yellow-500/20 text-yellow-400">
                          ⚠️
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      
      {/* Goal Input - Compact */}
      <div className="p-2 sm:p-3">
        <label className="block text-[10px] sm:text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
          Goal
        </label>
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="What do you want to accomplish?"
          className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-sm text-white placeholder:text-slate-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 resize-none"
          rows={2}
          disabled={!selectedRecipe || executing}
        />
        
        <button
          onClick={handleSubmit}
          disabled={!selectedRecipe || !goal.trim() || executing}
          className={`mt-2 w-full py-2 px-3 text-sm font-medium rounded transition-all active:scale-[0.98] ${
            executing
              ? "bg-blue-500 text-white animate-pulse shadow-lg shadow-blue-500/30"
              : selectedRecipe && goal.trim()
              ? "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/20"
              : "bg-slate-600 text-slate-400 cursor-not-allowed"
          }`}
        >
          {executing ? (
            <span className="flex items-center justify-center gap-1.5">
              <span className="animate-spin">⏳</span>
              Working...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-1.5">
              🚀 Execute
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
