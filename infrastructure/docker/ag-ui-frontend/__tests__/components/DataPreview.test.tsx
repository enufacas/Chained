/**
 * @jest-environment jsdom
 */

/**
 * DataPreview Component Tests
 * 
 * Tests for the pipeline data preview component with tabs
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DataPreview } from '@/components/DataPreview';
import { PipelineData } from '@/types';

describe('DataPreview Component', () => {
  const mockPipelineData: PipelineData = {
    research: {
      topic: 'Machine Learning',
      findings: 'ML is transforming industries',
    },
    trends: {
      keywords: ['AI', 'Deep Learning', 'Neural Networks'],
      popularity: 85,
    },
    blog: {
      title: 'Understanding Machine Learning',
      content: 'A comprehensive guide to ML',
      url: 'https://example.com/ml-guide',
    },
  };

  describe('Rendering', () => {
    it('should render with pipeline data provided', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      // Should show the heading
      expect(screen.getByText(/Data Preview/i)).toBeInTheDocument();
    });

    it('should render all tab buttons', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      expect(screen.getByRole('button', { name: /Research/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Trends/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Blog/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Full Result/i })).toBeInTheDocument();
    });

    it('should have research tab active by default', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const researchButton = screen.getByRole('button', { name: /Research/i });
      expect(researchButton).toHaveClass('bg-primary-500');
    });

    it('should display research data by default', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      // Check for research data in the preview
      expect(screen.getByText(/"topic"/)).toBeInTheDocument();
      expect(screen.getByText(/"Machine Learning"/)).toBeInTheDocument();
    });
  });

  describe('Tab switching', () => {
    it('should switch to trends tab when clicked', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const trendsButton = screen.getByRole('button', { name: /Trends/i });
      fireEvent.click(trendsButton);
      
      // Check that trends data is displayed
      expect(screen.getByText(/"keywords"/)).toBeInTheDocument();
      expect(screen.getByText(/"AI"/)).toBeInTheDocument();
    });

    it('should switch to blog tab when clicked', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const blogButton = screen.getByRole('button', { name: /Blog/i });
      fireEvent.click(blogButton);
      
      // Check that blog data is displayed
      expect(screen.getByText(/"title"/)).toBeInTheDocument();
      expect(screen.getByText(/"Understanding Machine Learning"/)).toBeInTheDocument();
    });

    it('should switch to full result tab when clicked', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const fullButton = screen.getByRole('button', { name: /Full Result/i });
      fireEvent.click(fullButton);
      
      // Check that full data is displayed (should have all sections)
      expect(screen.getByText(/"research"/)).toBeInTheDocument();
      expect(screen.getByText(/"trends"/)).toBeInTheDocument();
      expect(screen.getByText(/"blog"/)).toBeInTheDocument();
    });

    it('should update active tab styling when switching', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const trendsButton = screen.getByRole('button', { name: /Trends/i });
      const researchButton = screen.getByRole('button', { name: /Research/i });
      
      // Initially research is active
      expect(researchButton).toHaveClass('bg-primary-500');
      
      // Click trends
      fireEvent.click(trendsButton);
      
      // Now trends should be active
      expect(trendsButton).toHaveClass('bg-primary-500');
    });
  });

  describe('Data formatting', () => {
    it('should format JSON with proper indentation', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const preElement = document.querySelector('pre');
      expect(preElement).toBeInTheDocument();
      expect(preElement).toHaveClass('font-mono');
    });

    it('should display nested objects correctly', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const blogButton = screen.getByRole('button', { name: /Blog/i });
      fireEvent.click(blogButton);
      
      // Check for nested structure
      expect(screen.getByText(/"url"/)).toBeInTheDocument();
      expect(screen.getByText(/example.com/)).toBeInTheDocument();
    });

    it('should display arrays correctly', () => {
      render(<DataPreview data={mockPipelineData} />);
      
      const trendsButton = screen.getByRole('button', { name: /Trends/i });
      fireEvent.click(trendsButton);
      
      // Check for array display
      expect(screen.getByText(/"keywords"/)).toBeInTheDocument();
      expect(screen.getByText(/"Deep Learning"/)).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('should handle empty sections', () => {
      const emptyData: PipelineData = {
        research: {},
        trends: {},
        blog: {},
      };
      
      render(<DataPreview data={emptyData} />);
      
      // Should render without crashing
      expect(screen.getByText(/Data Preview/i)).toBeInTheDocument();
    });

    it('should handle missing sections gracefully', () => {
      const partialData: PipelineData = {
        research: { topic: 'Test' },
      } as PipelineData;
      
      render(<DataPreview data={partialData} />);
      
      // Should render research data
      expect(screen.getByText(/"topic"/)).toBeInTheDocument();
    });
  });
});
