/**
 * ArtifactPreviewOverlay Component
 *
 * A full-screen overlay for previewing artifacts (JSON, SVG, Markdown, HTML, etc.)
 * Opens when clicking on an artifact from the progress/outcomes section.
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import AssetPreview from "./AssetPreview";

interface Artifact {
  name: string;
  type: string;
  data: string;
  preview?: string;
}

interface ArtifactPreviewOverlayProps {
  artifact: Artifact | null;
  onClose: () => void;
  allArtifacts?: Artifact[];
  onSelectArtifact?: (artifact: Artifact) => void;
}

export default function ArtifactPreviewOverlay({
  artifact,
  onClose,
  allArtifacts = [],
  onSelectArtifact,
}: ArtifactPreviewOverlayProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (artifact) {
      setIsVisible(true);
    }
  }, [artifact]);

  const handleClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(onClose, 200);
  }, [onClose]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleClose();
      }
    };

    if (artifact) {
      document.addEventListener("keydown", handleKeyDown);
      return () => document.removeEventListener("keydown", handleKeyDown);
    }
  }, [artifact, handleClose]);

  if (!artifact) return null;

  const currentIndex = allArtifacts.findIndex(
    (a) => a.name === artifact.name && a.type === artifact.type
  );
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < allArtifacts.length - 1;

  const handlePrev = () => {
    if (hasPrev && onSelectArtifact) {
      onSelectArtifact(allArtifacts[currentIndex - 1]);
    }
  };

  const handleNext = () => {
    if (hasNext && onSelectArtifact) {
      onSelectArtifact(allArtifacts[currentIndex + 1]);
    }
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-200 ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
      onClick={handleClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />

      {/* Content */}
      <div
        className={`relative w-full max-w-4xl max-h-[90vh] m-4 flex flex-col transition-transform duration-200 ${
          isVisible ? "scale-100" : "scale-95"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with navigation */}
        <div className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700 rounded-t-xl">
          <div className="flex items-center gap-3">
            <span className="text-lg">📄</span>
            <div>
              <h3 className="font-semibold text-white text-sm">{artifact.name}</h3>
              <span className="text-xs text-slate-500">{artifact.type}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Navigation arrows */}
            {allArtifacts.length > 1 && (
              <div className="flex items-center gap-1 mr-2">
                <button
                  onClick={handlePrev}
                  disabled={!hasPrev}
                  className={`w-8 h-8 rounded flex items-center justify-center transition ${
                    hasPrev
                      ? "bg-slate-700 hover:bg-slate-600 text-white"
                      : "bg-slate-800 text-slate-600 cursor-not-allowed"
                  }`}
                >
                  ←
                </button>
                <span className="text-xs text-slate-500 px-2">
                  {currentIndex + 1} / {allArtifacts.length}
                </span>
                <button
                  onClick={handleNext}
                  disabled={!hasNext}
                  className={`w-8 h-8 rounded flex items-center justify-center transition ${
                    hasNext
                      ? "bg-slate-700 hover:bg-slate-600 text-white"
                      : "bg-slate-800 text-slate-600 cursor-not-allowed"
                  }`}
                >
                  →
                </button>
              </div>
            )}

            {/* Close button */}
            <button
              onClick={handleClose}
              className="w-8 h-8 rounded bg-slate-700 hover:bg-slate-600 text-slate-400 hover:text-white transition flex items-center justify-center"
            >
              ×
            </button>
          </div>
        </div>

        {/* Preview content */}
        <div className="flex-1 overflow-auto bg-slate-900 rounded-b-xl">
          <AssetPreview
            name={artifact.name}
            type={artifact.type}
            data={artifact.data}
            maxHeight="calc(90vh - 120px)"
          />
        </div>
      </div>
    </div>
  );
}
